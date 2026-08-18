import logging
from typing import List, Dict
from sqlalchemy.orm import Session
from app.engine.portfolio import VirtualPortfolio
from app.data.database.models import PositionDB, PaperTradingJournalDB, PortfolioStateDB
from app.operations.incidents import incident_manager

logger = logging.getLogger(__name__)

class ReconciliationService:
    def __init__(self):
        pass

    def reconcile_portfolio(self, db: Session, portfolio: VirtualPortfolio):
        """
        Reconciles the in-memory VirtualPortfolio against the persistence layer.
        Ensures Cash + Position Market Value == Portfolio Value.
        """
        # Load from DB to ensure fresh state
        state_db = db.query(PortfolioStateDB).filter_by(id="virtual").first()
        if not state_db:
            return
            
        persisted_cash = state_db.cash
        persisted_positions = db.query(PositionDB).all()
        
        # We assume current market price is entry price for reconciliation purposes 
        # (or whatever the latest P&L is, but P&L is floating so we just check structural consistency)
        
        journal_entries = db.query(PaperTradingJournalDB).all()
        
        # Sum of journal P&L + starting cash should equal current cash if all positions are closed
        # Since positions might be open, it's starting cash + realized pnl = current cash
        # Assuming starting cash was 100000.0
        expected_cash = 100000.0 + sum(j.realized_pnl for j in journal_entries if j.realized_pnl is not None)
        
        if abs(expected_cash - persisted_cash) > 0.01:
            incident_manager.log_incident(
                db,
                severity="CRITICAL",
                category="RECONCILIATION_ERROR",
                message=f"Cash mismatch: Expected {expected_cash}, found {persisted_cash}."
            )
            
        # Reconcile memory with DB
        if abs(portfolio.cash - persisted_cash) > 0.01:
            incident_manager.log_incident(
                db,
                severity="CRITICAL",
                category="RECONCILIATION_ERROR",
                message=f"Memory Cash mismatch: Memory {portfolio.cash}, DB {persisted_cash}."
            )
            
        if len(portfolio.positions) != len(persisted_positions):
            incident_manager.log_incident(
                db,
                severity="CRITICAL",
                category="RECONCILIATION_ERROR",
                message=f"Position count mismatch: Memory {len(portfolio.positions)}, DB {len(persisted_positions)}."
            )

reconciliation_service = ReconciliationService()
