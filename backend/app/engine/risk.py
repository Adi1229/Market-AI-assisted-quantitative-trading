from typing import List, Dict, Optional
from datetime import datetime
from app.engine.models import TradeOpportunity, RiskDecision, ExecutionPosition

class RiskEngine:
    """
    Evaluates TradeOpportunity objects against configurable risk thresholds.
    Functions as a HARD GATE before User Approval / Execution.
    """
    def __init__(self):
        # MVP Configuration
        self.max_position_size = 10000.0  # Max exposure per trade/instrument
        self.max_daily_loss = 5000.0
        self.stale_signal_seconds = 300   # 5 minutes
        
    def evaluate(
        self, 
        opportunity: TradeOpportunity, 
        portfolio_cash: float, 
        current_positions: List[ExecutionPosition],
        current_time: datetime
    ) -> RiskDecision:
        """
        Evaluate if the opportunity passes all risk checks.
        """
        try:
            from datetime import timezone, timedelta
            # Stale Signal Check — ensure both timestamps are tz-aware for safe subtraction
            if current_time.tzinfo is None:
                current_time = current_time.replace(tzinfo=timezone.utc)
            if opportunity.timestamp.tzinfo is None:
                opportunity.timestamp = opportunity.timestamp.replace(tzinfo=timezone.utc)
                
            timeframe_offset_seconds = 0
            if hasattr(opportunity, "timeframe") and opportunity.timeframe:
                if opportunity.timeframe.endswith("m"):
                    timeframe_offset_seconds = int(opportunity.timeframe[:-1]) * 60
                elif opportunity.timeframe.endswith("h"):
                    timeframe_offset_seconds = int(opportunity.timeframe[:-1]) * 3600
                elif opportunity.timeframe.endswith("d"):
                    timeframe_offset_seconds = int(opportunity.timeframe[:-1]) * 86400
                    
            effective_generation_time = opportunity.timestamp + timedelta(seconds=timeframe_offset_seconds)
            age_seconds = (current_time - effective_generation_time).total_seconds()
            
            if age_seconds > self.stale_signal_seconds:
                return RiskDecision(approved=False, reason="STALE_SIGNAL")
                
            # 2. Invalid price check
            # For simplicity, if suggested_entry is extremely negative or 0.
            if opportunity.suggested_entry is not None and opportunity.suggested_entry <= 0:
                return RiskDecision(approved=False, reason="INVALID_PRICE")
                
            # 3. Available capital check
            if opportunity.suggested_position_size:
                if opportunity.suggested_position_size > portfolio_cash:
                    return RiskDecision(approved=False, reason="INSUFFICIENT_CAPITAL")
                    
            # 4. Max position violation
            if opportunity.suggested_position_size and opportunity.suggested_position_size > self.max_position_size:
                return RiskDecision(approved=False, reason="MAX_POSITION_SIZE_EXCEEDED")
                
            # 5. Duplicate trade protection
            # If we already have a LONG position and the signal is BUY, we reject to avoid duplicates
            for pos in current_positions:
                if pos.instrument_id == opportunity.instrument_id:
                    if opportunity.direction.value == "BUY" and pos.direction == "LONG":
                        return RiskDecision(approved=False, reason="DUPLICATE_TRADE")
                    if opportunity.direction.value == "SELL" and pos.direction == "SHORT":
                        return RiskDecision(approved=False, reason="DUPLICATE_TRADE")

            # Assume daily loss check is managed in portfolio tracking
            
            return RiskDecision(approved=True, reason="APPROVED")
        except Exception as e:
            # FAIL CLOSED
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"RiskEngine crashed during evaluate: {e}")
            return RiskDecision(approved=False, reason=f"RISK_CRASH_FAIL_CLOSED")
