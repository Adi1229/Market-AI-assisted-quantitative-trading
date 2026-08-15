import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.data.providers.base import MarketDataProvider
from app.data.database.models import OHLCVData, Instrument
import logging

logger = logging.getLogger(__name__)

class DataIngestionService:
    def __init__(self, provider: MarketDataProvider, db: Session):
        self.provider = provider
        self.db = db
        
    def ingest_historical_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> int:
        """
        Fetches data from provider and stores in database.
        Returns number of records inserted/updated.
        """
        # Ensure instrument exists
        instrument = self.db.query(Instrument).filter(Instrument.symbol == symbol).first()
        if not instrument:
            new_instrument = Instrument(
                symbol=symbol,
                name=f"{symbol} (Auto-created)",
                exchange="NSE"
            )
            self.db.add(new_instrument)
            self.db.commit()
            
        df = self.provider.get_historical_ohlcv(symbol, timeframe, start_date, end_date)
        if df.empty:
            return 0
            
        # Validate timezone
        if df['timestamp'].dt.tz is None:
            raise ValueError("Timestamps must be timezone-aware (UTC)")
            
        # Data Quality Validation
        df = df.sort_values(by='timestamp').drop_duplicates(subset=['timestamp'])
        
        # Drop rows with negative prices or invalid high/low/open/close relationships
        invalid_mask = (
            (df['open'] <= 0) | (df['high'] <= 0) | (df['low'] <= 0) | (df['close'] <= 0) |
            (df['volume'] < 0) |
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        )
        
        dropped = invalid_mask.sum()
        if dropped > 0:
            logger.warning(f"Dropped {dropped} invalid candles for {symbol} ({timeframe})")
            df = df[~invalid_mask]
            
        if df.empty:
            return 0
            
        records = []
        for _, row in df.iterrows():
            records.append({
                "timestamp": row['timestamp'],
                "symbol": symbol,
                "timeframe": timeframe,
                "open": row['open'],
                "high": row['high'],
                "low": row['low'],
                "close": row['close'],
                "volume": row['volume']
            })
            
        # Upsert handling to avoid duplicates
        stmt = insert(OHLCVData).values(records)
        
        # For timescaledb, the conflict target is usually the primary key components
        update_dict = {
            c.name: c for c in stmt.excluded if c.name not in ['timestamp', 'symbol', 'timeframe', 'created_at']
        }
        
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['timestamp', 'symbol', 'timeframe'],
            set_=update_dict
        )
        
        try:
            result = self.db.execute(upsert_stmt)
            self.db.commit()
            return result.rowcount
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during bulk upsert: {e}")
            raise
