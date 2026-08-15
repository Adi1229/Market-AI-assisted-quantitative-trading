from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from app.engine.models import (
    TradeOpportunity, OpportunityStatus, ExecutionOrder
)
from app.engine.risk import RiskEngine
from app.engine.execution import ExecutionProvider
from app.engine.notification import NotificationAdapter

import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.data.database.models import TradeOpportunityDB, UserDecisionDB, IdempotencyKeyDB

class WorkflowOrchestrator:
    """
    Manages the lifecycle of a TradeOpportunity.
    Enforces state machine and database-backed idempotency.
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
        
    async def process_new_opportunity(self, opportunity: TradeOpportunity, current_price: float, db: Session = None):
        """
        Runs opportunity through risk and sends to notification if approved.
        Persists to DB.
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
        else:
            opportunity.status = OpportunityStatus.AWAITING_APPROVAL
            await self.notification.send_opportunity(opportunity)
            
        # Persist Opportunity
        if db:
            db_opp = TradeOpportunityDB(
                opportunity_id=opportunity.opportunity_id,
                symbol=opportunity.symbol,
                timestamp=opportunity.timestamp,
                decision_mode=opportunity.decision_mode.value,
                direction=opportunity.direction.value,
                confidence_score=opportunity.confidence_score,
                strategy_evidence=opportunity.strategy_evidence.model_dump() if opportunity.strategy_evidence else None,
                ai_evidence=opportunity.ai_evidence.model_dump() if opportunity.ai_evidence else None,
                status=opportunity.status.value
            )
            db.add(db_opp)
            db.commit()
            
    async def process_user_action(
        self, 
        opportunity: TradeOpportunity, 
        action: str, 
        current_price: float,
        db: Session = None
    ) -> Optional[ExecutionOrder]:
        """
        Handles TAKE_TRADE or IGNORE from user.
        Enforces Database-backed Idempotency and Transactional safety.
        """
        if db is None:
            raise ValueError("DB Session required for WorkflowOrchestrator.process_user_action")
            
        # 1. Idempotency Check (Transactional)
        idempotency_key = f"{opportunity.opportunity_id}_{action}"
        try:
            db_key = IdempotencyKeyDB(
                idempotency_key=idempotency_key,
                opportunity_id=opportunity.opportunity_id,
                action=action
            )
            db.add(db_key)
            db.commit() # Commits the lock
        except IntegrityError:
            db.rollback()
            print(f"Idempotency hit! Opportunity {opportunity.opportunity_id} already processed for {action}.")
            return None
            
        if opportunity.status != OpportunityStatus.AWAITING_APPROVAL:
            raise ValueError(f"Opportunity {opportunity.opportunity_id} is in state {opportunity.status}, expected AWAITING_APPROVAL")
            
        # 2. Record User Decision
        decision_id = str(uuid.uuid4())
        db_decision = UserDecisionDB(
            action_id=decision_id,
            opportunity_id=opportunity.opportunity_id,
            action=action
        )
        db.add(db_decision)
        
        # 3. Handle Action
        if action == "IGNORE" or action == "REJECT_TRADE":
            opportunity.status = OpportunityStatus.REJECTED
            db_opp = db.query(TradeOpportunityDB).filter_by(opportunity_id=opportunity.opportunity_id).first()
            if db_opp:
                db_opp.status = OpportunityStatus.REJECTED.value
            db.commit()
            return None
            
        if action == "TAKE_TRADE":
            opportunity.status = OpportunityStatus.APPROVED
            
            # Additional check to ensure LIVE trading is blocked in MVP unless explicitly overriden
            if self.execution.execution_mode == "LIVE":
                opportunity.status = OpportunityStatus.EXECUTION_FAILED
                opportunity.reasoning.append("LIVE execution mode disabled by default.")
                db_opp = db.query(TradeOpportunityDB).filter_by(opportunity_id=opportunity.opportunity_id).first()
                if db_opp:
                    db_opp.status = OpportunityStatus.EXECUTION_FAILED.value
                db.commit()
                raise RuntimeError("LIVE execution mode disabled.")
                
            opportunity.status = OpportunityStatus.EXECUTING
            
            # Execute
            order = ExecutionOrder(
                opportunity_id=opportunity.opportunity_id,
                instrument_id=opportunity.instrument_id,
                direction=opportunity.direction.value if hasattr(opportunity.direction, 'value') else opportunity.direction,
                order_type="MARKET",
                quantity=opportunity.suggested_position_size or 1.0
            )
            
            try:
                filled_order = await self.execution.place_order(order, current_price, db=db)
                opportunity.status = OpportunityStatus.EXECUTED
                
                db_opp = db.query(TradeOpportunityDB).filter_by(opportunity_id=opportunity.opportunity_id).first()
                if db_opp:
                    db_opp.status = OpportunityStatus.EXECUTED.value
                
                db.commit() # Commit all portfolio and status changes
                
                await self.notification.send_execution_result(filled_order)
                return filled_order
                
            except Exception as e:
                db.rollback() # Rollback on execution failure
                opportunity.status = OpportunityStatus.EXECUTION_FAILED
                opportunity.reasoning.append(f"Execution failed: {str(e)}")
                
                db_opp = db.query(TradeOpportunityDB).filter_by(opportunity_id=opportunity.opportunity_id).first()
                if db_opp:
                    db_opp.status = OpportunityStatus.EXECUTION_FAILED.value
                db.commit()
                return None
