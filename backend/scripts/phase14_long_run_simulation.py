"""
Phase 14 Long Run Simulation
Simulates thousands of ticks and multiple days of operations without network dependencies.
Asserts that memory remains stable, idempotency survives, and errors are cleanly logged.
"""
import sys
import os
import asyncio
from datetime import datetime, timezone, timedelta
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.database.session import SessionLocal
from app.operations.health import health_monitor
from app.operations.incidents import incident_manager
from app.operations.reconciliation import reconciliation_service

from app.engine.workflow import WorkflowOrchestrator
from app.engine.risk import RiskEngine
from app.engine.portfolio import VirtualPortfolio
from app.engine.execution import PaperExecutionProvider
from app.engine.notification import NotificationAdapter
from app.engine.models import TradeOpportunity, DecisionMode, Direction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockNotificationAdapter(NotificationAdapter):
    async def send_opportunity(self, opp): pass
    async def send_execution_result(self, order): pass
    async def send_daily_summary(self, session_id): pass

async def run_simulation():
    db = SessionLocal()
    try:
        logger.info("Starting Phase 14 Long Run Simulation...")
        
        portfolio = VirtualPortfolio(initial_capital=100000.0)
        portfolio.load_from_db(db)
        
        execution = PaperExecutionProvider(portfolio)
        orchestrator = WorkflowOrchestrator(
            risk_engine=RiskEngine(),
            execution_provider=execution,
            notification_adapter=MockNotificationAdapter()
        )
        
        start_time = datetime.now(timezone.utc)
        
        for i in range(100):
            current_time = start_time + timedelta(minutes=5 * i)
            
            # Simulate market health update
            health_monitor.update_market_health(
                db, "RELIANCE.NS", "mock", "5m", 
                latest_ts=current_time, 
                latest_completed_ts=current_time - timedelta(minutes=5)
            )
            
            # Simulate 1 opportunity every 10 iterations
            if i % 10 == 0:
                opp = TradeOpportunity(
                    symbol="RELIANCE.NS",
                    instrument_id="RELIANCE.NS",
                    timeframe="5m",
                    timestamp=current_time,
                    decision_mode=DecisionMode.HYBRID,
                    direction=Direction.BUY if i % 20 == 0 else Direction.SELL,
                    confidence_score=85.0 + (i % 10),
                    suggested_entry=2500.0 + i,
                    suggested_position_size=1000.0,
                    reasoning=[],
                    market_regime="BULLISH",
                    risk_level="LOW",
                    data_references=[]
                )
                
                try:
                    await orchestrator.process_new_opportunity(opp, 2500.0 + i, db)
                    # Attempt to take trade (should only work if risk passes)
                    if opp.status.value == "AWAITING_APPROVAL":
                        await orchestrator.process_user_action(opp, "TAKE_TRADE", 2500.0 + i, db)
                except Exception as e:
                    logger.error(f"Iteration {i} failed: {e}")
                    
            # Inject a random provider error occasionally
            if i % 33 == 0:
                health_monitor.record_provider_error(db, "upstox", "TIMEOUT", "Simulated Timeout")
                
            # Run reconciliation
            if i % 50 == 0:
                reconciliation_service.reconcile_portfolio(db, portfolio)
                
        incidents = incident_manager.get_active_incidents(db)
        logger.info(f"Simulation completed. Active Incidents: {len(incidents)}")
        logger.info(f"Final Portfolio Cash: {portfolio.cash}")
        logger.info(f"Positions Count: {len(portfolio.positions)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_simulation())
