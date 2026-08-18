import asyncio
import logging
import time
from datetime import datetime, timezone

from app.data.database.session import SessionLocal
from app.data.database.models import PaperExperimentDB

from scripts.phase15_live_paper_experiment import run_experiment_cycle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phase15LongRun")

def maintain_experiments():
    """
    Check if experiments are meant to expire.
    """
    db = SessionLocal()
    try:
        active_experiments = db.query(PaperExperimentDB).filter_by(status="ACTIVE").all()
        now = datetime.now(timezone.utc)
        for exp in active_experiments:
            if exp.end_time and now > exp.end_time:
                logger.info(f"Experiment {exp.experiment_id} reached end_time. Completing.")
                exp.status = "COMPLETED"
                db.commit()
    except Exception as e:
        logger.error(f"Error maintaining experiments: {e}")
    finally:
        db.close()

async def long_run_loop():
    logger.info("Starting Phase 15 Long Run Paper Experiment Orchestrator...")
    while True:
        try:
            logger.info(f"--- Starting Cycle at {datetime.now(timezone.utc)} ---")
            maintain_experiments()
            await run_experiment_cycle()
            
            logger.info("--- Cycle Complete. Sleeping for 5 minutes ---")
            await asyncio.sleep(300) # 5 minutes sleep
        except asyncio.CancelledError:
            logger.info("Received termination signal. Shutting down gracefully.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in long run loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(long_run_loop())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting.")
