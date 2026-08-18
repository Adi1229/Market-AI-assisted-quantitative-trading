from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any

from app.analytics.service import AnalyticsService

class DailyReportService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsService(db)
        
    def generate_daily_report(self, session_id: str) -> Dict[str, Any]:
        """Generate the structured daily paper report."""
        session_metrics = self.analytics.get_session_metrics(session_id)
        if not session_metrics:
            return {"message": "Session not found or no data available."}
            
        strategy_perf = self.analytics.get_strategy_performance(session_id)
        mode_perf = self.analytics.get_decision_mode_performance(session_id)
        rejections = self.analytics.get_rejection_analytics(session_id)
        ai_perf = self.analytics.get_ai_effectiveness(session_id)
        
        return {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "portfolio_value": session_metrics.get("current_capital", 0),
            "daily_pnl": session_metrics.get("realized_pnl", 0),
            "daily_return": session_metrics.get("return_pct", 0),
            "trades": session_metrics.get("total_trades", 0),
            "wins": session_metrics.get("wins", 0),
            "losses": session_metrics.get("losses", 0),
            "win_rate": session_metrics.get("win_rate", 0),
            "strategy_breakdown": strategy_perf,
            "decision_mode_breakdown": mode_perf,
            "risk_rejections": rejections,
            "ai_performance": ai_perf
        }
