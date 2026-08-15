"""
Phase 8 Audit: Controlled real-data probe — US ticker fallback.
Single small request. No retries.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta

print("=" * 60)
print("PHASE 8 AUDIT: CONTROLLED REAL DATA PROBE (US TICKER)")
print("=" * 60)

# Use a US ticker which yfinance handles more reliably
symbol = "AAPL"

# --- 1. Market Data ---
print(f"\n--- Market Data: {symbol} ---")
try:
    from app.data.providers.yfinance_provider import YFinanceMarketDataProvider
    provider = YFinanceMarketDataProvider()
    
    start = datetime(2026, 8, 1, tzinfo=timezone.utc)
    end = datetime(2026, 8, 10, tzinfo=timezone.utc)
    print(f"Range: {start.date()} -> {end.date()}")
    
    df = provider.get_historical_ohlcv(symbol, "1d", start, end)
    
    if df.empty:
        print("RESULT: Empty DataFrame returned.")
        print("STATUS: REAL MARKET DATA RETRIEVAL = NOT VERIFIED")
    else:
        print(f"Row count: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print(f"First timestamp: {df.iloc[0]['timestamp']}")
        print(f"Last timestamp: {df.iloc[-1]['timestamp']}")
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            print(f"  Row {i}: O={row['open']:.2f} H={row['high']:.2f} L={row['low']:.2f} C={row['close']:.2f} V={int(row['volume'])}")
        print("STATUS: REAL MARKET DATA RETRIEVAL = VERIFIED")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback; traceback.print_exc()
    print("STATUS: REAL MARKET DATA RETRIEVAL = NOT VERIFIED")

# Small delay to avoid hammering
time.sleep(2)

# --- 2. News ---
print(f"\n--- News: {symbol} ---")
try:
    from app.intelligence.news import YFinanceNewsProvider
    news_provider = YFinanceNewsProvider()
    news = news_provider.fetch_news(symbol, start, end)
    if news:
        print(f"Items returned: {len(news)}")
        for n in news[:3]:
            print(f"  Headline: {n.headline}")
            print(f"  Source: {n.source}")
            print(f"  Timestamp: {n.timestamp}")
        print("STATUS: REAL NEWS RETRIEVAL = VERIFIED")
    else:
        print("No news items returned.")
        print("STATUS: REAL NEWS RETRIEVAL = NOT VERIFIED")
except Exception as e:
    print(f"ERROR: {e}")
    print("STATUS: REAL NEWS RETRIEVAL = NOT VERIFIED")

time.sleep(2)

# --- 3. Fundamentals ---
print(f"\n--- Fundamentals: {symbol} ---")
try:
    from app.intelligence.fundamentals import YFinanceFundamentalProvider
    fund_provider = YFinanceFundamentalProvider()
    funds = fund_provider.fetch_fundamentals(symbol, end)
    if funds:
        print(f"Metrics returned: {len(funds)}")
        for f in funds:
            print(f"  {f.metric}: {f.value}")
        print("STATUS: REAL FUNDAMENTALS RETRIEVAL = VERIFIED")
    else:
        print("No fundamental metrics returned.")
        print("STATUS: REAL FUNDAMENTALS RETRIEVAL = NOT VERIFIED")
except Exception as e:
    print(f"ERROR: {e}")
    print("STATUS: REAL FUNDAMENTALS RETRIEVAL = NOT VERIFIED")

print("\n" + "=" * 60)
print("PROBE COMPLETE")
print("=" * 60)
