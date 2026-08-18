import sys
import os
import asyncio
from datetime import datetime, timezone, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.data.providers.upstox_provider import UpstoxMarketDataProvider
import app.quantitative.features.core as features
from app.core.config import settings

async def main():
    provider = UpstoxMarketDataProvider()
    start_date = datetime.now(timezone.utc) - timedelta(days=14)
    end_date = datetime.now(timezone.utc)
    df = provider.get_historical_ohlcv("RELIANCE.NS", "5m", start_date, end_date)
    df['SMA_50'] = features.calculate_sma(df, 50)
    df['RSI_14'] = features.calculate_rsi(df, 14)
    df = df.dropna()
    print("Latest 5 candles:")
    print(df[['timestamp', 'close', 'SMA_50', 'RSI_14']].tail(5))

if __name__ == "__main__":
    asyncio.run(main())
