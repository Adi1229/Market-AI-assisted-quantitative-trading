from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Market 2.0 MVP"
    DATABASE_URL: str = "postgresql://market_user:market_password@localhost:5432/market_db"
    
    # Provider Settings
    MOCK_PROVIDER_ENABLED: bool = True
    DATA_PROVIDER: str = "mock"
    AI_PROVIDER: str = "mock"
    
    # Telegram Settings
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
