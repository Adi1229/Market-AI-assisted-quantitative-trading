"""
Phase 14 Real Market Operations Validation
Runs a continuous loop fetching live UPSTOX data, logging health and heartbeats,
and verifying that the system safely processes (or cleanly rejects) data.
"""
import sys
import os
import asyncio
from datetime import datetime, timezone
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from app.data.database.session import SessionLocal
from app.operations.health import health_monitor
from app.data.providers.upstox_provider import UpstoxMarketDataProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_operations_loop():
    logger.info("Starting Phase 14 Real Market Operations...")
    provider = UpstoxMarketDataProvider()
    db = SessionLocal()
    
    try:
        # We will do 3 iterations for validation
        for i in range(3):
            now = datetime.now(timezone.utc)
            logger.info(f"--- Iteration {i+1} at {now} ---")
            
            # Update heartbeats
            health_monitor.record_heartbeat(db, "system", {"last_processed": now})
            
            try:
                from datetime import timedelta
                start = now - timedelta(days=1)
                
                # Fetch data
                df = provider.get_historical_ohlcv("RELIANCE.NS", "5m", start, now)
                
                if df is not None and not df.empty:
                    health_monitor.record_provider_success(db, "upstox")
                    
                    latest_ts = df["timestamp"].iloc[-1].to_pydatetime()
                    # Since we are fetching up to current, the latest completed is the one before it
                    if len(df) > 1:
                        latest_completed = df["timestamp"].iloc[-2].to_pydatetime()
                    else:
                        latest_completed = latest_ts
                        
                    health_monitor.update_market_health(
                        db, "RELIANCE.NS", "upstox", "5m",
                        latest_ts=latest_ts,
                        latest_completed_ts=latest_completed
                    )
                    
                    logger.info(f"Fetched {len(df)} candles. Latest: {latest_ts}")
                else:
                    health_monitor.record_provider_error(db, "upstox", "EMPTY", "Empty dataframe returned")
                    
            except Exception as e:
                health_monitor.record_provider_error(db, "upstox", "CONNECTION", str(e))
                logger.error(f"Provider Error: {e}")
                
            await asyncio.sleep(2)
            
        logger.info("Real market operations validation complete.")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_operations_loop())
