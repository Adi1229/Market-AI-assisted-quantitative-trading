from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Market 2.0 MVP"
    DATABASE_URL: str = "postgresql://market_user:market_password@localhost:5432/market_db"
    
    # Auth Settings
    MARKET_API_TOKEN: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Provider Settings
    MOCK_PROVIDER_ENABLED: bool = True
    DATA_PROVIDER: str = "mock"
    AI_PROVIDER: str = "mock"
    
    # OpenRouter LLM Settings
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openrouter/free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # AI Cost Controls
    AI_MAX_TOKENS: int = 1024
    AI_REQUEST_TIMEOUT: float = 15.0
    AI_MAX_REQUESTS_PER_RUN: int = 1
    
    # Telegram Settings
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    # DhanHQ Settings
    DHAN_CLIENT_ID: Optional[str] = None
    DHAN_ACCESS_TOKEN: Optional[str] = None
    
    # Upstox Settings
    UPSTOX_ANALYTICS_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
