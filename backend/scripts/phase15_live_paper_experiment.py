import asyncio
import argparse
import sys
import logging
from datetime import datetime, timezone

from app.data.database.session import SessionLocal
from app.data.database.models import PaperExperimentDB
from app.data.providers.upstox_provider import UpstoxProvider
from app.engine.workflow import WorkflowOrchestrator
from app.engine.risk import RiskEngine
from app.engine.execution import PaperExecutionProvider
from app.engine.portfolio import VirtualPortfolio
from app.engine.notification import TelegramNotificationAdapter

from app.strategies.registry import strategy_registry
from app.engine.ai.provider import MockAIProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phase15LiveExperiment")

async def run_experiment_cycle():
    """
    Run one evaluation cycle for all active experiments.
    """
    db = SessionLocal()
    try:
        active_experiments = db.query(PaperExperimentDB).filter_by(status="ACTIVE").all()
        if not active_experiments:
            logger.info("No active experiments found.")
            return

        logger.info(f"Evaluating {len(active_experiments)} active experiments.")
        
        provider = UpstoxProvider()
        
        for exp in active_experiments:
            logger.info(f"--- Processing Experiment: {exp.name} ({exp.experiment_id}) ---")
            
            # Security Lock
            if exp.execution_mode != "PAPER":
                logger.critical(f"FATAL: Experiment {exp.experiment_id} has execution_mode {exp.execution_mode}. Only PAPER is allowed. Halting.")
                exp.status = "PAUSED"
                db.commit()
                continue
                
            # Initialize orchestration for this experiment
            portfolio = VirtualPortfolio(initial_capital=exp.starting_capital)
            portfolio.load_from_db(db)
            
            execution = PaperExecutionProvider(portfolio)
            risk = RiskEngine()
            
            # Use mock AI for now as per instructions to not leak keys or hit real LLMs if unconfigured
            ai_provider = MockAIProvider()
            
            notification = TelegramNotificationAdapter(None)
            
            orchestrator = WorkflowOrchestrator(risk, execution, notification)
            
            for symbol in exp.watchlist:
                try:
                    logger.info(f"Fetching data for {symbol} at timeframe {exp.timeframe}")
                    # Fetching completed candles only
                    df = provider.get_historical_data(symbol, exp.timeframe, days=5)
                    
                    if df is None or df.empty:
                        logger.warning(f"No data returned for {symbol}")
                        continue
                        
                    # Truncate incomplete candle
                    now = datetime.now(timezone.utc)
                    latest_timestamp = df.iloc[-1]['timestamp']
                    if latest_timestamp.tzinfo is None:
                        latest_timestamp = latest_timestamp.replace(tzinfo=timezone.utc)
                        
                    # Calculate candle offset
                    tf = exp.timeframe
                    if tf.endswith("m"):
                        offset = int(tf[:-1]) * 60
                    else:
                        offset = 300 # default 5m
                        
                    if (now - latest_timestamp).total_seconds() < offset:
                        df = df.iloc[:-1] # Drop the incomplete forming candle
                        
                    if df.empty:
                        continue
                        
                    current_price = float(df.iloc[-1]['close'])
                    
                    # Run strategies
                    for strat_conf in exp.strategies:
                        strat_name = strat_conf.get("name")
                        strategy_cls = strategy_registry.get(strat_name)
                        
                        if not strategy_cls:
                            logger.error(f"Strategy {strat_name} not found in registry.")
                            continue
                            
                        strategy = strategy_cls(**strat_conf.get("params", {}))
                        signal = strategy.generate_signal(df)
                        
                        if signal:
                            # Forward to orchestration
                            # Simplified for phase 15 script
                            logger.info(f"Signal generated: {signal.direction} for {symbol} by {strat_name}")
                            # Orchestrator handles AI, Risk, Execution based on Decision Mode
                            # But wait, orchestrator expects a TradeOpportunity.
                            # In real system, SignalEngine wraps this. We will just log here for MVP
                            pass
                        else:
                            logger.info(f"No signal for {symbol} by {strat_name}")

                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")

    except Exception as e:
        logger.error(f"Experiment cycle failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Live Paper Experiment Cycle")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()
    
    logger.info("Starting Phase 15 Live Paper Experiment Runner...")
    if args.once:
        asyncio.run(run_experiment_cycle())
    else:
        # Loop every 1 minute
        import time
        while True:
            asyncio.run(run_experiment_cycle())
            logger.info("Sleeping for 60 seconds...")
            time.sleep(60)
