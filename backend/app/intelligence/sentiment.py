from abc import ABC, abstractmethod
from typing import List
from app.intelligence.models import NewsItem, SentimentResult

class BaseSentimentAnalyzer(ABC):
    """Abstract interface for sentiment analysis."""
    
    @abstractmethod
    def analyze(self, news_items: List[NewsItem]) -> List[SentimentResult]:
        pass

class MockSentimentAnalyzer(BaseSentimentAnalyzer):
    """Deterministic mock NLP provider for offline testing."""
    
    def analyze(self, news_items: List[NewsItem]) -> List[SentimentResult]:
        results = []
        for item in news_items:
            # Very basic deterministic logic for testing
            text = (item.headline + " " + (item.text or "")).lower()
            
            if "profit" in text or "growth" in text or "up" in text:
                score = 0.8
                label = "Bullish"
            elif "scrutiny" in text or "loss" in text or "down" in text:
                score = -0.8
                label = "Bearish"
            else:
                score = 0.0
                label = "Neutral"
                
            # If item has symbols, associate the sentiment with the first symbol
            symbol = item.symbols[0] if item.symbols else None
            
            results.append(
                SentimentResult(
                    news_id=item.id,
                    symbol=symbol,
                    score=score,
                    label=label,
                    provider_id="MockNLP"
                )
            )
        return results
