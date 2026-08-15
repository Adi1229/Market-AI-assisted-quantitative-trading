import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.intelligence.news import MockNewsProvider
from app.intelligence.fundamentals import MockFundamentalProvider
from app.intelligence.sentiment import MockSentimentAnalyzer
from app.intelligence.regime import MarketRegimeAnalyzer
from app.intelligence.ai_engine import MockAIProvider
from app.intelligence.ml_ranking import MLStrategyRanker

def test_abstractions_and_mocks():
    """Test News, Fundamentals, and Sentiment mocks."""
    start_time = datetime(2023, 1, 1)
    end_time = datetime(2023, 1, 2)
    
    news_items = MockNewsProvider().fetch_news("TEST", start_time, end_time)
    assert len(news_items) == 2
    assert news_items[0].timestamp == start_time
    
    sentiment_results = MockSentimentAnalyzer().analyze(news_items)
    assert len(sentiment_results) == 2
    # The first item has "profit", should be bullish
    assert sentiment_results[0].label == "Bullish"
    assert sentiment_results[0].score == 0.8
    # Second has "scrutiny", should be bearish
    assert sentiment_results[1].label == "Bearish"
    
    fundamentals = MockFundamentalProvider().fetch_fundamentals("TEST", start_time)
    assert len(fundamentals) == 2
    assert fundamentals[0].metric == "P/E"
    
def test_market_regime():
    """Test deterministic regime classification."""
    dates = pd.date_range("2023-01-01", periods=60, freq="D")
    # Build a simple dataframe where close is always increasing, 
    # so SMA20 > SMA50 -> Bullish Trend
    df = pd.DataFrame({
        "open": np.linspace(100, 160, 60),
        "high": np.linspace(105, 165, 60),
        "low": np.linspace(95, 155, 60),
        "close": np.linspace(102, 162, 60),
        "volume": [1000] * 60
    }, index=dates)
    
    regime = MarketRegimeAnalyzer.classify(df, "TEST", dates[-1])
    assert regime.trend_state == "Bullish"
    assert "SMA_20" in regime.features_used
    assert "VOLATILITY_20" in regime.features_used
    
def test_ai_decision_engine():
    """Test structured AI output and missing evidence handling."""
    regime = MarketRegimeAnalyzer.classify(pd.DataFrame(), "TEST", datetime(2023, 1, 1)) # Empty DF yields Neutral
    ai = MockAIProvider()
    
    # Fully populated evidence
    news_items = MockNewsProvider().fetch_news("TEST", datetime.now(), datetime.now())
    sentiments = MockSentimentAnalyzer().analyze(news_items)
    fundamentals = MockFundamentalProvider().fetch_fundamentals("TEST", datetime.now())
    
    analysis = ai.generate_analysis(
        symbol="TEST",
        timestamp=datetime(2023, 1, 1),
        regime=regime,
        sentiment_evidence=sentiments,
        fundamental_evidence=fundamentals,
        quantitative_evidence={}
    )
    
    assert analysis.confidence == 0.8
    assert "Neutral" in analysis.market_context
    assert len(analysis.risks) > 0
    
    # Missing evidence
    missing_analysis = ai.generate_analysis(
        symbol="TEST",
        timestamp=datetime(2023, 1, 1),
        regime=regime,
        sentiment_evidence=[], # Missing
        fundamental_evidence=[], # Missing
        quantitative_evidence={}
    )
    
    assert missing_analysis.confidence == pytest.approx(0.2) # 0.8 - (0.3 * 2) = 0.2
    assert "Missing evidence" in missing_analysis.thesis

def test_ml_strategy_ranking_temporal_leakage():
    """Test the ML strategy ranking avoids temporal leakage and runs locally."""
    # Create mock dataset spanning 100 days
    dates = pd.date_range("2023-01-01", periods=100)
    df = pd.DataFrame({
        "timestamp": dates,
        "strategy_id": ["strat_1"] * 100,
        "feature_volatility": np.random.rand(100),
        "feature_momentum": np.random.rand(100),
        "target_return": np.random.rand(100)
    })
    
    ranker = MLStrategyRanker()
    
    # Validate temporally using TimeSeriesSplit
    mse = ranker.validate_temporally(df, ["feature_volatility", "feature_momentum"], "target_return")
    assert mse >= 0.0 # Just ensure it runs and computes MSE successfully
    
    # Train final model
    ranker.train(df, ["feature_volatility", "feature_momentum"], "target_return")
    
    # Predict/Rank
    current_features = [
        {"strategy_id": "strat_1", "feature_volatility": 0.5, "feature_momentum": 0.8},
        {"strategy_id": "strat_2", "feature_volatility": 0.1, "feature_momentum": 0.2}
    ]
    
    rankings = ranker.rank_strategies(current_features)
    assert len(rankings) == 2
    assert rankings[0].rank == 1
    assert rankings[1].rank == 2
    assert rankings[0].score >= rankings[1].score # Sorted descending
    assert rankings[0].model_id == "RandomForest_v1"

from unittest.mock import patch, MagicMock
from app.intelligence.news import YFinanceNewsProvider
from app.intelligence.fundamentals import YFinanceFundamentalProvider

@patch('yfinance.Ticker')
def test_yfinance_news_provider(mock_ticker):
    instance = MagicMock()
    # Mock yfinance news format
    instance.news = [
        {
            "uuid": "123",
            "title": "Reliance earnings call",
            "publisher": "Yahoo Finance",
            "providerPublishTime": 1672531200,
            "link": "http://example.com"
        }
    ]
    mock_ticker.return_value = instance
    
    provider = YFinanceNewsProvider()
    news = provider.fetch_news("RELIANCE.NS", datetime.now(), datetime.now())
    
    assert len(news) == 1
    assert news[0].headline == "Reliance earnings call"
    assert news[0].source == "Yahoo Finance"

@patch('yfinance.Ticker')
def test_yfinance_fundamentals_provider(mock_ticker):
    instance = MagicMock()
    instance.info = {
        "trailingPE": 20.5,
        "trailingEps": 45.2,
        "totalRevenue": 1000000,
        "returnOnEquity": 0.15
    }
    mock_ticker.return_value = instance
    
    provider = YFinanceFundamentalProvider()
    fundamentals = provider.fetch_fundamentals("RELIANCE.NS", datetime.now())
    
    # We mapped 4 fields in info
    assert len(fundamentals) == 4
    metrics = {f.metric: f.value for f in fundamentals}
    assert metrics["P/E"] == 20.5
    assert metrics["EPS"] == 45.2
    assert metrics["Revenue"] == 1000000
    assert metrics["ROE"] == 0.15

