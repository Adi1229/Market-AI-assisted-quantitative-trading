from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.v1.endpoints import market, strategies, backtesting, signals, portfolio

app = FastAPI(title=settings.PROJECT_NAME)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

app.include_router(market.router, prefix="/api/v1", tags=["market"])
app.include_router(strategies.router, prefix="/api/v1", tags=["strategies"])
app.include_router(backtesting.router, prefix="/api/v1", tags=["backtesting"])
app.include_router(signals.router, prefix="/api/v1", tags=["signals"])
app.include_router(portfolio.router, prefix="/api/v1", tags=["portfolio"])
