from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from app.data.database.models import (
    PaperTradingSessionDB, 
    TradeOpportunityDB, 
    PaperTradingJournalDB, 
    UserDecisionDB,
    PortfolioStateDB
)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        
    def start_session(self, name: str = None) -> PaperTradingSessionDB:
        # End any active sessions
        active_sessions = self.db.query(PaperTradingSessionDB).filter(PaperTradingSessionDB.status == "ACTIVE").all()
        for session in active_sessions:
            session.status = "PAUSED"
            session.end_time = datetime.now(timezone.utc)
            
        portfolio = self.db.query(PortfolioStateDB).filter_by(id="virtual").first()
        current_cap = portfolio.cash if portfolio else 100000.0
        
        session = PaperTradingSessionDB(
            id=str(uuid.uuid4()),
            name=name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            starting_capital=current_cap,
            current_capital=current_cap,
            start_time=datetime.now(timezone.utc),
            status="ACTIVE",
            execution_mode="PAPER"
        )
        self.db.add(session)
        self.db.commit()
        return session
        
    def end_session(self, session_id: str) -> PaperTradingSessionDB:
        session = self.db.query(PaperTradingSessionDB).filter_by(id=session_id).first()
        if session:
            portfolio = self.db.query(PortfolioStateDB).filter_by(id="virtual").first()
            session.current_capital = portfolio.cash if portfolio else session.current_capital
            session.status = "COMPLETED"
            session.end_time = datetime.now(timezone.utc)
            self.db.commit()
        return session
        
    def pause_session(self, session_id: str) -> PaperTradingSessionDB:
        session = self.db.query(PaperTradingSessionDB).filter_by(id=session_id).first()
        if session and session.status == "ACTIVE":
            session.status = "PAUSED"
            self.db.commit()
        return session
        
    def resume_session(self, session_id: str) -> PaperTradingSessionDB:
        session = self.db.query(PaperTradingSessionDB).filter_by(id=session_id).first()
        if session and session.status == "PAUSED":
            # ensure no other active sessions
            active_sessions = self.db.query(PaperTradingSessionDB).filter(PaperTradingSessionDB.status == "ACTIVE").all()
            for s in active_sessions:
                s.status = "PAUSED"
            session.status = "ACTIVE"
            session.end_time = None
            self.db.commit()
        return session
        
    def get_current_session(self) -> Optional[PaperTradingSessionDB]:
        return self.db.query(PaperTradingSessionDB).filter(PaperTradingSessionDB.status == "ACTIVE").first()
        
    def get_session_metrics(self, session_id: str) -> Dict[str, Any]:
        session = self.db.query(PaperTradingSessionDB).filter_by(id=session_id).first()
        if not session:
            return {}
            
        journals = self.db.query(PaperTradingJournalDB).filter_by(session_id=session_id).all()
        
        realized_pnl = sum([j.realized_pnl for j in journals if j.realized_pnl is not None])
        closed_trades = [j for j in journals if j.exit_price is not None]
        wins = [j for j in closed_trades if j.realized_pnl > 0]
        losses = [j for j in closed_trades if j.realized_pnl <= 0]
        
        return {
            "status": session.status,
            "starting_capital": session.starting_capital,
            "current_capital": session.current_capital,
            "realized_pnl": realized_pnl,
            "return_pct": (session.current_capital - session.starting_capital) / session.starting_capital * 100 if session.starting_capital > 0 else 0,
            "total_trades": len(closed_trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(closed_trades) if closed_trades else 0,
            "profit_factor": sum(w.realized_pnl for w in wins) / abs(sum(l.realized_pnl for l in losses)) if losses and sum(l.realized_pnl for l in losses) != 0 else float('inf') if wins else 0
        }
        
    def get_strategy_performance(self, session_id: str) -> List[Dict[str, Any]]:
        journals = self.db.query(PaperTradingJournalDB).filter(
            PaperTradingJournalDB.session_id == session_id,
            PaperTradingJournalDB.exit_price.isnot(None)
        ).all()
        
        strats = {}
        for j in journals:
            key = f"{j.strategy} (v{j.strategy_version})"
            if key not in strats:
                strats[key] = {"trades": 0, "wins": 0, "losses": 0, "pnl": 0}
            strats[key]["trades"] += 1
            strats[key]["pnl"] += (j.realized_pnl or 0)
            if (j.realized_pnl or 0) > 0:
                strats[key]["wins"] += 1
            else:
                strats[key]["losses"] += 1
                
        results = []
        for s, data in strats.items():
            data["strategy"] = s
            data["win_rate"] = data["wins"] / data["trades"] if data["trades"] > 0 else 0
            results.append(data)
        return results
        
    def get_regime_performance(self, session_id: str) -> List[Dict[str, Any]]:
        journals = self.db.query(PaperTradingJournalDB).filter(
            PaperTradingJournalDB.session_id == session_id,
            PaperTradingJournalDB.exit_price.isnot(None)
        ).all()
        
        regimes = {}
        for j in journals:
            key = j.regime or "Unknown"
            if key not in regimes:
                regimes[key] = {"trades": 0, "wins": 0, "pnl": 0}
            regimes[key]["trades"] += 1
            regimes[key]["pnl"] += (j.realized_pnl or 0)
            if (j.realized_pnl or 0) > 0:
                regimes[key]["wins"] += 1
                
        results = []
        for r, data in regimes.items():
            data["regime"] = r
            data["win_rate"] = data["wins"] / data["trades"] if data["trades"] > 0 else 0
            results.append(data)
        return results
        
    def get_decision_mode_performance(self, session_id: str) -> List[Dict[str, Any]]:
        journals = self.db.query(PaperTradingJournalDB).filter(
            PaperTradingJournalDB.session_id == session_id,
            PaperTradingJournalDB.exit_price.isnot(None)
        ).all()
        # We need to join with TradeOpportunity to get decision mode
        opps = self.db.query(TradeOpportunityDB).filter_by(session_id=session_id).all()
        opp_dict = {o.opportunity_id: o.decision_mode for o in opps}
        
        modes = {}
        for j in journals:
            key = opp_dict.get(j.opportunity_id, "UNKNOWN")
            if key not in modes:
                modes[key] = {"trades": 0, "wins": 0, "pnl": 0}
            modes[key]["trades"] += 1
            modes[key]["pnl"] += (j.realized_pnl or 0)
            if (j.realized_pnl or 0) > 0:
                modes[key]["wins"] += 1
                
        results = []
        for m, data in modes.items():
            data["mode"] = m
            data["win_rate"] = data["wins"] / data["trades"] if data["trades"] > 0 else 0
            results.append(data)
        return results
        
    def get_signal_funnel(self, session_id: str) -> Dict[str, int]:
        opps = self.db.query(TradeOpportunityDB).filter_by(session_id=session_id).all()
        
        generated = len(opps)
        risk_approved = sum(1 for o in opps if o.status not in ["RISK_REJECTED", "EXPIRED"])
        user_approved = sum(1 for o in opps if o.status in ["APPROVED", "EXECUTING", "EXECUTED", "CLOSED"])
        executed = sum(1 for o in opps if o.status in ["EXECUTED", "CLOSED"])
        closed = sum(1 for o in opps if o.status == "CLOSED")
        
        return {
            "generated": generated,
            "risk_approved": risk_approved,
            "user_approved": user_approved,
            "executed": executed,
            "closed": closed
        }
        
    def get_rejection_analytics(self, session_id: str) -> List[Dict[str, Any]]:
        opps = self.db.query(TradeOpportunityDB).filter_by(session_id=session_id).all()
        
        reasons = {}
        for o in opps:
            if o.status == "RISK_REJECTED" and o.reasoning:
                for r in o.reasoning:
                    reason_type = r.split(": ")[-1] if ": " in r else r
                    reasons[reason_type] = reasons.get(reason_type, 0) + 1
                    
        total_rejections = sum(reasons.values())
        results = []
        for r, count in reasons.items():
            results.append({
                "reason": r,
                "count": count,
                "percentage": (count / total_rejections * 100) if total_rejections else 0
            })
        return results

    def get_ai_effectiveness(self, session_id: str) -> Dict[str, Any]:
        journals = self.db.query(PaperTradingJournalDB).filter(
            PaperTradingJournalDB.session_id == session_id,
            PaperTradingJournalDB.exit_price.isnot(None)
        ).all()
        
        correct = 0
        incorrect = 0
        
        for j in journals:
            # Simple heuristic: if AI score > 50 and trade won -> correct, else incorrect
            if j.ai_score is not None:
                if (j.ai_score > 50 and j.realized_pnl > 0) or (j.ai_score <= 50 and j.realized_pnl <= 0):
                    correct += 1
                else:
                    incorrect += 1
                    
        total = correct + incorrect
        return {
            "ai_source": "MOCK / SIMULATED", # Would be dynamically fetched if real LLM is used
            "accuracy": correct / total if total > 0 else 0,
            "correct_predictions": correct,
            "incorrect_predictions": incorrect,
            "total_evaluated": total
        }

    def get_daily_report(self) -> Dict[str, Any]:
        """Generate a daily paper trading report based on today's UTC data."""
        today = datetime.now(timezone.utc).date()
        
        # Get journals for today
        journals = self.db.query(PaperTradingJournalDB).filter(
            func.date(PaperTradingJournalDB.entry_time) == today
        ).all()
        
        portfolio = self.db.query(PortfolioStateDB).filter_by(id="virtual").first()
        current_val = portfolio.cash if portfolio else 0.0
        
        realized_pnl = sum([j.realized_pnl for j in journals if j.realized_pnl is not None])
        closed_trades = [j for j in journals if j.exit_price is not None]
        wins = [j for j in closed_trades if j.realized_pnl > 0]
        losses = [j for j in closed_trades if j.realized_pnl <= 0]
        
        best_trade = max(closed_trades, key=lambda x: x.realized_pnl) if closed_trades else None
        worst_trade = min(closed_trades, key=lambda x: x.realized_pnl) if closed_trades else None
        
        total_trades = len(closed_trades)
        
        if total_trades == 0:
            return {
                "date": today.isoformat(),
                "portfolio_value": current_val,
                "daily_pnl": 0.0,
                "daily_return_pct": 0.0,
                "total_trades": 0,
                "message": "NO TRADES TODAY"
            }
            
        return {
            "date": today.isoformat(),
            "portfolio_value": current_val,
            "daily_pnl": realized_pnl,
            "daily_return_pct": (realized_pnl / (current_val - realized_pnl) * 100) if (current_val - realized_pnl) > 0 else 0.0,
            "total_trades": total_trades,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / total_trades if total_trades > 0 else 0,
            "best_trade_pnl": best_trade.realized_pnl if best_trade else 0.0,
            "worst_trade_pnl": worst_trade.realized_pnl if worst_trade else 0.0,
            "message": "INSUFFICIENT SAMPLE SIZE" if total_trades < 3 else "VALID"
        }
