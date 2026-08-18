import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.intelligence.ai_engine import ConfigurableLLMProvider
from app.intelligence.openrouter_provider import OpenRouterAIProvider
from app.intelligence.models import MarketRegime, SentimentResult, FundamentalData

@pytest.fixture
def mock_evidence():
    return {
        "symbol": "RELIANCE",
        "timestamp": datetime(2023, 1, 1, 10, 0),
        "regime": MarketRegime(
            symbol="RELIANCE", 
            timestamp=datetime(2023, 1, 1, 10, 0), 
            trend_state="Bullish", 
            volatility_state="Normal", 
            momentum_state="Overbought"
        ),
        "sentiment_evidence": [
            SentimentResult(
                news_id="123", 
                symbol="RELIANCE", 
                score=0.9, 
                label="Bullish", 
                provider_id="Mock"
            )
        ],
        "fundamental_evidence": [],
        "quantitative_evidence": {"SMA_20": 100, "RSI": 60}
    }

def test_missing_credentials(mock_evidence):
    with patch("app.core.config.settings.AI_PROVIDER", "openrouter"), \
         patch("app.core.config.settings.OPENROUTER_API_KEY", None):
        provider = ConfigurableLLMProvider()
        result = provider.generate_analysis(**mock_evidence)
        assert result.thesis == "REAL LLM BLOCKED — CREDENTIALS UNAVAILABLE"
        assert result.confidence == 0.0
        assert result.source == "OPENROUTER"
        assert "SYSTEM_ERROR: AI Credentials missing" in result.risks

def test_mock_fallback(mock_evidence):
    with patch("app.core.config.settings.AI_PROVIDER", "mock"):
        provider = ConfigurableLLMProvider()
        result = provider.generate_analysis(**mock_evidence)
        assert result.source == "MOCK"

@patch("httpx.post")
def test_valid_llm_response(mock_post, mock_evidence):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "model": "poolside/laguna-xs-2.1:free",
            "choices": [{
                "message": {
                    "content": '{"thesis": "Valid LLM thesis", "confidence": 0.8, "bullish_factors": ["A"], "bearish_factors": ["B"], "risks": ["C"], "evidence": "Strong"}'
                }
            }]
        }
    )
    with patch("app.core.config.settings.AI_PROVIDER", "openrouter"), \
         patch("app.core.config.settings.OPENROUTER_API_KEY", "test_key"):
        provider = ConfigurableLLMProvider()
        result = provider.generate_analysis(**mock_evidence)
        assert result.thesis == "Valid LLM thesis"
        assert result.confidence == 0.8
        assert result.source == "OPENROUTER"
        assert result.actual_model == "poolside/laguna-xs-2.1:free"

@patch("httpx.post")
def test_malformed_json_response(mock_post, mock_evidence):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "choices": [{
                "message": {
                    "content": "Not JSON"
                }
            }]
        }
    )
    with patch("app.core.config.settings.AI_PROVIDER", "openrouter"), \
         patch("app.core.config.settings.OPENROUTER_API_KEY", "test_key"):
        provider = ConfigurableLLMProvider()
        result = provider.generate_analysis(**mock_evidence)
        assert result.thesis == "REAL LLM BLOCKED — API FAILURE"
        assert result.confidence == 0.0
        assert result.source == "OPENROUTER"
        assert any("Expecting value" in r for r in result.risks)

@patch("httpx.post")
def test_429_rate_limit(mock_post, mock_evidence):
    mock_post.return_value = MagicMock(status_code=429)
    with patch("app.core.config.settings.AI_PROVIDER", "openrouter"), \
         patch("app.core.config.settings.OPENROUTER_API_KEY", "test_key"):
        provider = ConfigurableLLMProvider()
        result = provider.generate_analysis(**mock_evidence)
        assert result.thesis == "REAL LLM BLOCKED — API FAILURE"
        assert any("429" in r for r in result.risks)

@patch("httpx.post")
def test_timeout(mock_post, mock_evidence):
    import httpx
    mock_post.side_effect = httpx.TimeoutException("Timeout")
    with patch("app.core.config.settings.AI_PROVIDER", "openrouter"), \
         patch("app.core.config.settings.OPENROUTER_API_KEY", "test_key"):
        provider = ConfigurableLLMProvider()
        result = provider.generate_analysis(**mock_evidence)
        assert result.thesis == "REAL LLM BLOCKED — API TIMEOUT"
        assert any("Timeout" in r for r in result.risks)

@patch("httpx.post")
def test_future_data_protection(mock_post, mock_evidence):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "choices": [{
                "message": {
                    "content": '{"thesis": "Valid LLM thesis", "confidence": 0.8, "bullish_factors": ["A"], "bearish_factors": ["B"], "risks": ["C"], "evidence": "Strong"}'
                }
            }]
        }
    )
    with patch("app.core.config.settings.AI_PROVIDER", "openrouter"), \
         patch("app.core.config.settings.OPENROUTER_API_KEY", "test_key"):
        provider = ConfigurableLLMProvider()
        provider.generate_analysis(**mock_evidence)
        
        call_kwargs = mock_post.call_args.kwargs
        messages = call_kwargs["json"]["messages"]
        prompt = messages[0]["content"]
        
        assert "2023-01-01T10:00:00" in prompt
        assert "Do not assume future knowledge" in prompt
        
@patch("httpx.post")
def test_authentication_failure(mock_post, mock_evidence):
    # Simulate a 401 Unauthorized from OpenRouter
    import httpx
    mock_response = MagicMock(status_code=401)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("401 Unauthorized", request=MagicMock(), response=mock_response)
    mock_post.return_value = mock_response
    
    with patch("app.core.config.settings.AI_PROVIDER", "openrouter"), \
         patch("app.core.config.settings.OPENROUTER_API_KEY", "invalid_key"):
        provider = ConfigurableLLMProvider()
        result = provider.generate_analysis(**mock_evidence)
        assert result.thesis == "REAL LLM BLOCKED — API FAILURE"
        assert any("401" in r for r in result.risks)
