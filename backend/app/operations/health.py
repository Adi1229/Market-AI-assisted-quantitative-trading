import pytz
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.data.database.models import HeartbeatDB, MarketHealthDB, ProviderHealthDB
from app.operations.incidents import incident_manager

IST = pytz.timezone('Asia/Kolkata')

class HealthMonitor:
    def __init__(self):
        pass

    def is_indian_market_open(self, current_time: datetime = None) -> bool:
        if not current_time:
            current_time = datetime.now(timezone.utc)
        ist_time = current_time.astimezone(IST)
        
        # Weekend check
        if ist_time.weekday() >= 5:
            return False
            
        market_open = ist_time.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = ist_time.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= ist_time <= market_close

    def get_market_status(self, current_time: datetime = None) -> str:
        if not current_time:
            current_time = datetime.now(timezone.utc)
        ist_time = current_time.astimezone(IST)
        
        if ist_time.weekday() >= 5:
            return "MARKET_CLOSED"
            
        market_open = ist_time.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = ist_time.replace(hour=15, minute=30, second=0, microsecond=0)
        pre_market = ist_time.replace(hour=9, minute=0, second=0, microsecond=0)
        
        if pre_market <= ist_time < market_open:
            return "PRE_MARKET"
        elif market_open <= ist_time <= market_close:
            return "MARKET_OPEN"
        else:
            return "MARKET_CLOSED"

    def record_heartbeat(self, db: Session, component: str, field_updates: dict):
        """
        Updates the HeartbeatDB for a specific component (e.g. 'system').
        """
        hb = db.query(HeartbeatDB).filter_by(id=component).first()
        if not hb:
            hb = HeartbeatDB(id=component)
            db.add(hb)
            
        for k, v in field_updates.items():
            if hasattr(hb, k):
                setattr(hb, k, v)
                
        hb.last_processed = datetime.now(timezone.utc)
        db.commit()

    def record_provider_success(self, db: Session, provider_id: str):
        ph = db.query(ProviderHealthDB).filter_by(provider_id=provider_id).first()
        if not ph:
            ph = ProviderHealthDB(provider_id=provider_id)
            db.add(ph)
            
        ph.success_count += 1
        ph.consecutive_failures = 0
        ph.last_successful_request = datetime.now(timezone.utc)
        ph.status = "HEALTHY"
        db.commit()

    def record_provider_error(self, db: Session, provider_id: str, error_type: str, message: str):
        ph = db.query(ProviderHealthDB).filter_by(provider_id=provider_id).first()
        if not ph:
            ph = ProviderHealthDB(
                provider_id=provider_id,
                success_count=0,
                error_429_count=0,
                timeout_count=0,
                auth_error_count=0,
                empty_response_count=0,
                malformed_response_count=0,
                connection_error_count=0,
                consecutive_failures=0
            )
            db.add(ph)
            
        if error_type == "429":
            ph.error_429_count += 1
        elif error_type == "TIMEOUT":
            ph.timeout_count += 1
        elif error_type == "AUTH":
            ph.auth_error_count += 1
        else:
            ph.connection_error_count += 1
            
        ph.consecutive_failures += 1
        if ph.consecutive_failures >= 3:
            ph.status = "ERROR"
            
        db.commit()
        
        incident_manager.log_incident(
            db, 
            severity="ERROR" if ph.consecutive_failures >= 3 else "WARNING", 
            category=f"PROVIDER_{error_type}",
            message=message,
            provider=provider_id
        )

    def update_market_health(
        self, 
        db: Session, 
        symbol: str, 
        provider: str, 
        timeframe: str, 
        latest_ts: datetime,
        latest_completed_ts: datetime
    ):
        mh = db.query(MarketHealthDB).filter_by(symbol=symbol).first()
        if not mh:
            mh = MarketHealthDB(
                symbol=symbol, 
                provider=provider, 
                timeframe=timeframe,
                expected_interval_seconds=300 if timeframe == '5m' else 60,
                candles_received=0,
                missing_candles=0,
                duplicate_candles=0,
                invalid_candles=0
            )
            db.add(mh)
            
        mh.latest_candle_ts = latest_ts
        mh.latest_completed_ts = latest_completed_ts
        mh.candles_received += 1
        
        # Calculate data age relative to now
        now = datetime.now(timezone.utc)
        if latest_completed_ts.tzinfo is None:
            latest_completed_ts = latest_completed_ts.replace(tzinfo=timezone.utc)
            
        age = (now - latest_completed_ts).total_seconds()
        mh.data_age_seconds = age
        
        market_status = self.get_market_status(now)
        if market_status == "MARKET_OPEN":
            if age > mh.expected_interval_seconds * 2:
                mh.status = "STALE"
                incident_manager.log_incident(
                    db,
                    severity="WARNING",
                    category="DATA_STALE",
                    message=f"Data for {symbol} is stale. Age: {age}s",
                    instrument=symbol,
                    provider=provider
                )
            else:
                mh.status = "HEALTHY"
        else:
            mh.status = "MARKET_CLOSED"
            
        db.commit()
        
health_monitor = HealthMonitor()
