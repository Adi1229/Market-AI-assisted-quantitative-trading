from sqlalchemy import Column, String, Float, DateTime, Boolean, BigInteger, UniqueConstraint
from sqlalchemy.sql import func
from app.data.database.session import Base
import datetime

class Instrument(Base):
    __tablename__ = "instruments"

    symbol = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    active = Column(Boolean, default=True)

class OHLCVData(Base):
    __tablename__ = "ohlcv_data"

    # TimescaleDB requires the time column to be part of any primary key 
    # if it's partitioned, but usually we don't define a PK in SQLAlchemy 
    # for hypertables, or we use a composite PK.
    timestamp = Column(DateTime(timezone=True), primary_key=True, index=True)
    symbol = Column(String, primary_key=True, index=True)
    
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
