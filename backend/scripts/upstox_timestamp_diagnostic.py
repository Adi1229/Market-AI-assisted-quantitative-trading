import sys
import os
import asyncio
from datetime import datetime, timezone
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.data.providers.upstox_provider import UpstoxMarketDataProvider

async def main():
    provider = UpstoxMarketDataProvider()
    from datetime import timedelta
    start_date = datetime.now(timezone.utc) - timedelta(days=2)
    end_date = datetime.now(timezone.utc)
    df = provider.get_historical_ohlcv("RELIANCE.NS", "5m", start_date, end_date)
    if not df.empty:
        latest = df.iloc[-1]
        print(f"Current time: {datetime.now(timezone.utc)}")
        print(f"Latest candle timestamp: {latest['timestamp']}")
        print(f"Age in minutes: {(datetime.now(timezone.utc) - latest['timestamp']).total_seconds() / 60}")
    else:
        print("No data")

if __name__ == "__main__":
    asyncio.run(main())
