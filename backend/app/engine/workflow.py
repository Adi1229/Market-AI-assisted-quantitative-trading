from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from app.engine.models import (
    TradeOpportunity, OpportunityStatus, ExecutionOrder
)
from app.engine.risk import RiskEngine
from app.engine.execution import ExecutionProvider
from app.engine.notification import NotificationAdapter

class IdempotencyTracker:
    def __init__(self):
        self._processed_opportunities = set()
        
    def is_processed(self, opportunity_id: str) -> bool:
        return opportunity_id in self._processed_opportunities
        
    def mark_processed(self, opportunity_id: str):
        self._processed_opportunities.add(opportunity_id)

class WorkflowOrchestrator:
    """
    Manages the lifecycle of a TradeOpportunity.
    Enforces state machine and idempotency.
    """
    def __init__(
        self, 
        risk_engine: RiskEngine, 
        execution_provider: ExecutionProvider,
        notification_adapter: NotificationAdapter
    ):
        self.risk_engine = risk_engine
        self.execution = execution_provider
        self.notification = notification_adapter
        self.idempotency = IdempotencyTracker()
        
    async def process_new_opportunity(self, opportunity: TradeOpportunity, current_price: float):
        """
        Runs opportunity through risk and sends to notification if approved.
        """
        if opportunity.status != OpportunityStatus.CREATED:
            raise ValueError(f"Cannot process opportunity in state {opportunity.status}")
            
        portfolio = await self.execution.get_portfolio_summary({"mock": 0})
        positions = await self.execution.get_positions()
        
        # Risk Gate
        risk_decision = self.risk_engine.evaluate(
            opportunity=opportunity,
            portfolio_cash=portfolio.cash,
            current_positions=positions,
            current_time=datetime.now()
        )
        
        if not risk_decision.approved:
            opportunity.status = OpportunityStatus.RISK_REJECTED
            opportunity.reasoning.append(f"Rejected by Risk: {risk_decision.reason}")
            return
            
        opportunity.status = OpportunityStatus.AWAITING_APPROVAL
        # Notify user
        await self.notification.send_opportunity(opportunity)
        
    async def process_user_action(
        self, 
        opportunity: TradeOpportunity, 
        action: str, 
        current_price: float
    ) -> Optional[ExecutionOrder]:
        """
        Handles TAKE_TRADE or IGNORE from user.
        Enforces Idempotency.
        """
        if self.idempotency.is_processed(opportunity.opportunity_id):
            print(f"Idempotency hit! Opportunity {opportunity.opportunity_id} already processed.")
            return None
            
        if opportunity.status != OpportunityStatus.AWAITING_APPROVAL:
            raise ValueError(f"Opportunity {opportunity.opportunity_id} is in state {opportunity.status}, expected AWAITING_APPROVAL")
            
        if action == "IGNORE":
            opportunity.status = OpportunityStatus.REJECTED
            self.idempotency.mark_processed(opportunity.opportunity_id)
            return None
            
        if action == "TAKE_TRADE":
            opportunity.status = OpportunityStatus.APPROVED
            
            # Additional check to ensure LIVE trading is blocked in MVP unless explicitly overriden
            if self.execution.execution_mode == "LIVE":
                opportunity.status = OpportunityStatus.EXECUTION_FAILED
                opportunity.reasoning.append("LIVE execution mode disabled by default.")
                self.idempotency.mark_processed(opportunity.opportunity_id)
                raise RuntimeError("LIVE execution mode disabled.")
                
            opportunity.status = OpportunityStatus.EXECUTING
            
            # Execute
            order = ExecutionOrder(
                opportunity_id=opportunity.opportunity_id,
                instrument_id=opportunity.instrument_id,
                direction=opportunity.direction.value,
                order_type="MARKET",
                quantity=opportunity.suggested_position_size or 1.0
            )
            
            try:
                filled_order = await self.execution.place_order(order, current_price)
                opportunity.status = OpportunityStatus.EXECUTED
                self.idempotency.mark_processed(opportunity.opportunity_id)
                
                await self.notification.send_execution_result(filled_order)
                return filled_order
                
            except Exception as e:
                opportunity.status = OpportunityStatus.EXECUTION_FAILED
                opportunity.reasoning.append(f"Execution failed: {str(e)}")
                self.idempotency.mark_processed(opportunity.opportunity_id)
                return None
