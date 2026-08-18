from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import verify_api_token

from app.api.v1.endpoints import market, strategies, backtesting, signals, portfolio, watchlist, analytics, research, sessions, operations, experiments

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
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "provider": settings.DATA_PROVIDER}

# Protect all standard API routes with verify_api_token
app.include_router(market.router, prefix="/api/v1", tags=["market"], dependencies=[Depends(verify_api_token)])
app.include_router(strategies.router, prefix="/api/v1", tags=["strategies"], dependencies=[Depends(verify_api_token)])
app.include_router(backtesting.router, prefix="/api/v1", tags=["backtesting"], dependencies=[Depends(verify_api_token)])
app.include_router(signals.router, prefix="/api/v1", tags=["signals"], dependencies=[Depends(verify_api_token)])
app.include_router(portfolio.router, prefix="/api/v1", tags=["portfolio"], dependencies=[Depends(verify_api_token)])
app.include_router(watchlist.router, prefix="/api/v1/watchlists", tags=["watchlists"], dependencies=[Depends(verify_api_token)])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"], dependencies=[Depends(verify_api_token)])
app.include_router(research.router, prefix="/api/v1/research", tags=["research"], dependencies=[Depends(verify_api_token)])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"], dependencies=[Depends(verify_api_token)])
app.include_router(operations.router, prefix="/api/v1/operations", tags=["operations"], dependencies=[Depends(verify_api_token)])
app.include_router(experiments.router, prefix="/api/v1/experiments", tags=["experiments"], dependencies=[Depends(verify_api_token)])
