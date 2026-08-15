from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.v1.endpoints import market, strategies, backtesting, signals, portfolio

from contextlib import asynccontextmanager
from app.engine.telegram_bot import TelegramBot
import logging

logging.basicConfig(level=logging.INFO)

telegram_bot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_bot
    if settings.TELEGRAM_BOT_TOKEN:
        telegram_bot = TelegramBot(bot_token=settings.TELEGRAM_BOT_TOKEN)
        await telegram_bot.start()
    yield
    if telegram_bot:
        await telegram_bot.stop()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "provider": settings.DATA_PROVIDER}

app.include_router(market.router, prefix="/api/v1", tags=["market"])
app.include_router(strategies.router, prefix="/api/v1", tags=["strategies"])
app.include_router(backtesting.router, prefix="/api/v1", tags=["backtesting"])
app.include_router(signals.router, prefix="/api/v1", tags=["signals"])
app.include_router(portfolio.router, prefix="/api/v1", tags=["portfolio"])
