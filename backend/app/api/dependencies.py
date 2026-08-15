from fastapi import Depends, HTTPException
from typing import Generator

from app.engine.signal import SignalEngine
from app.engine.risk import RiskEngine
from app.engine.portfolio import VirtualPortfolio
from app.engine.execution import PaperExecutionProvider
from app.engine.notification import MockTelegramAdapter, TelegramAdapter
from app.core.config import settings
from app.engine.workflow import WorkflowOrchestrator
from app.strategies.registry import StrategyRegistry
from app.backtesting.engine import BacktestEngine
from app.intelligence.ml_ranking import MLStrategyRanker

from app.data.database.session import SessionLocal

_signal_engine = SignalEngine()
_risk_engine = RiskEngine()
_portfolio = VirtualPortfolio(initial_capital=100000.0)

# Initialize portfolio from DB
db = SessionLocal()
try:
    _portfolio.load_from_db(db)
except Exception as e:
    print(f"Failed to load portfolio from DB on startup: {e}")
finally:
    db.close()

_execution_provider = PaperExecutionProvider(_portfolio)
if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
    _notification = TelegramAdapter(bot_token=settings.TELEGRAM_BOT_TOKEN, chat_id=settings.TELEGRAM_CHAT_ID)
else:
    _notification = MockTelegramAdapter()
_workflow_orchestrator = WorkflowOrchestrator(
    risk_engine=_risk_engine,
    execution_provider=_execution_provider,
    notification_adapter=_notification
)

from app.data.providers.mock import MockMarketDataProvider
from app.data.providers.yfinance_provider import YFinanceMarketDataProvider
from app.data.providers.base import MarketDataProvider
from app.intelligence.news import MockNewsProvider, YFinanceNewsProvider, BaseNewsProvider
from app.intelligence.fundamentals import MockFundamentalProvider, YFinanceFundamentalProvider, BaseFundamentalProvider
from app.data.ingestion import DataIngestionService


# Registries and Services
_strategy_registry = StrategyRegistry

from app.strategies.momentum.strategy import MomentumStrategy
from app.strategies.mean_reversion.strategy import MeanReversionStrategy
try:
    _strategy_registry.register(MomentumStrategy)
except: pass
try:
    _strategy_registry.register(MeanReversionStrategy)
except: pass

_ml_selector = MLStrategyRanker()

def get_market_data_provider() -> MarketDataProvider:
    if settings.DATA_PROVIDER.lower() == "real":
        return YFinanceMarketDataProvider()
    return MockMarketDataProvider()

def get_news_provider() -> BaseNewsProvider:
    if settings.DATA_PROVIDER.lower() == "real":
        return YFinanceNewsProvider()
    return MockNewsProvider()

def get_fundamental_provider() -> BaseFundamentalProvider:
    if settings.DATA_PROVIDER.lower() == "real":
        return YFinanceFundamentalProvider()
    return MockFundamentalProvider()

def get_data_ingestion_service(
    provider: MarketDataProvider = Depends(get_market_data_provider)
) -> DataIngestionService:
    db = SessionLocal()
    try:
        yield DataIngestionService(provider, db)
    finally:
        db.close()

def get_signal_engine() -> SignalEngine:
    return _signal_engine

def get_risk_engine() -> RiskEngine:
    return _risk_engine

def get_portfolio() -> VirtualPortfolio:
    return _portfolio

def get_execution_provider() -> PaperExecutionProvider:
    return _execution_provider

def get_workflow_orchestrator() -> WorkflowOrchestrator:
    return _workflow_orchestrator

def get_strategy_registry() -> type[StrategyRegistry]:
    return _strategy_registry

def get_ml_selector() -> MLStrategyRanker:
    return _ml_selector

