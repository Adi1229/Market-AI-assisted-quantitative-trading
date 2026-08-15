from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict
    finish_reason: str

class AIProvider(ABC):
    """Abstract interface for LLM/AI providers."""

    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @abstractmethod
    async def generate(
        self, messages: List[dict],
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2048
    ) -> LLMResponse:
        """Generate a completion."""
        ...

    @abstractmethod
    async def health_check(self) -> bool: ...

class MockAIProvider(AIProvider):
    """
    Mock AI Provider for offline testing and MVP without API keys.
    Returns deterministic responses.
    """
    
    @property
    def provider_id(self) -> str:
        return "MockAI"
        
    async def generate(
        self, messages: List[dict],
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2048
    ) -> LLMResponse:
        
        # Simple mock logic based on last user message
        last_msg = messages[-1]["content"] if messages else ""
        
        if "analyze" in last_msg.lower():
            content = """
            {"direction": "BUY", "confidence_score": 85, "reasoning": ["Mock AI analysis supports upward trend based on recent data."], "key_factors": {"momentum": 0.8, "sentiment": 0.9}}
            """
        else:
            content = "This is a mock AI response."
            
        return LLMResponse(
            content=content.strip(),
            model="mock-llm-v1",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop"
        )
        
    async def health_check(self) -> bool:
        return True
