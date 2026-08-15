from abc import ABC, abstractmethod
from typing import Optional
from app.engine.models import TradeOpportunity, ExecutionOrder

class NotificationAdapter(ABC):
    """Abstract notification channel."""

    @abstractmethod
    async def send_opportunity(self, opportunity: TradeOpportunity) -> bool: ...

    @abstractmethod
    async def send_execution_result(self, result: ExecutionOrder) -> bool: ...

class MockTelegramAdapter(NotificationAdapter):
    """
    Mocks out Telegram payload formatting. Prints to console/logs.
    Does NOT contain trading logic, just formatting.
    """
    
    async def send_opportunity(self, opportunity: TradeOpportunity) -> bool:
        msg = f"""
🚨 TRADE OPPORTUNITY

Symbol: {opportunity.symbol}
Decision Mode: {opportunity.decision_mode.value}
"""
        if opportunity.strategy_evidence:
            msg += f"""
📊 Strategy: {opportunity.strategy_evidence.strategy_name}
Strategy Signal: {opportunity.strategy_evidence.signal_type} — {opportunity.strategy_evidence.signal_score}/100
"""
        if opportunity.ai_evidence:
            msg += f"""
🤖 AI Analysis:
AI Signal: {opportunity.ai_evidence.direction} — {opportunity.ai_evidence.ai_score}/100
"""
        
        msg += f"""
📰 Market Regime: {opportunity.market_regime}
⚠️ Risk: {opportunity.risk_level}

💰 Suggested Entry: {opportunity.suggested_entry}
Combined Score: {opportunity.confidence_score}/100

[ ✅ TAKE PAPER TRADE ]  [ ❌ IGNORE ]
"""
        # In a real app, this sends HTTP request to Telegram API.
        # We print it here for E2E validation.
        print(msg)
        return True

    async def send_execution_result(self, order: ExecutionOrder) -> bool:
        msg = f"""
✅ TRADE EXECUTED

Symbol: {order.instrument_id}
Direction: {order.direction}
Quantity: {order.quantity}
Fill Price: {order.fill_price}
"""
        print(msg)
        return True
