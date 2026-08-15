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

class TelegramAdapter(NotificationAdapter):
    """
    Real Telegram adapter using python-telegram-bot.
    Sends notifications to the configured chat.
    """
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        from telegram import Bot
        self.bot = Bot(token=self.bot_token)
        
    async def send_opportunity(self, opportunity: TradeOpportunity) -> bool:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        msg = f"🚨 *TRADE OPPORTUNITY*\n\n"
        msg += f"Symbol: *{opportunity.symbol}*\n"
        msg += f"Decision Mode: {opportunity.decision_mode.value}\n\n"
        
        if opportunity.strategy_evidence:
            msg += f"📊 *Strategy*: {opportunity.strategy_evidence.strategy_name}\n"
            msg += f"Signal: {opportunity.strategy_evidence.signal_type} — {opportunity.strategy_evidence.signal_score}/100\n\n"
            
        if opportunity.ai_evidence:
            ai_label = "REAL" if opportunity.ai_evidence.ai_model_id != "MockAI" else "MOCK/SIMULATED"
            msg += f"🤖 *AI Analysis*: {ai_label}\n"
            msg += f"Signal: {opportunity.ai_evidence.direction} — {opportunity.ai_evidence.ai_score}/100\n\n"
            
        msg += f"📰 Market Regime: {opportunity.market_regime}\n"
        msg += f"⚠️ Risk: {opportunity.risk_level}\n\n"
        
        msg += f"💰 Suggested Entry: {opportunity.suggested_entry}\n"
        msg += f"Combined Score: {opportunity.confidence_score}/100\n\n"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ TAKE PAPER TRADE", callback_data=f"TAKE_TRADE:{opportunity.opportunity_id}"),
                InlineKeyboardButton("❌ IGNORE", callback_data=f"IGNORE:{opportunity.opportunity_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=msg,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            return True
        except Exception as e:
            print(f"TelegramAdapter failed: {e}")
            return False

    async def send_execution_result(self, order: ExecutionOrder) -> bool:
        msg = f"✅ *TRADE EXECUTED*\n\n"
        msg += f"Symbol: {order.instrument_id}\n"
        msg += f"Direction: {order.direction}\n"
        msg += f"Quantity: {order.quantity}\n"
        msg += f"Fill Price: {order.fill_price}\n"
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=msg,
                parse_mode="Markdown"
            )
            return True
        except Exception as e:
            print(f"TelegramAdapter execution notification failed: {e}")
            return False
