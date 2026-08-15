from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import asyncio

from app.engine.models import ExecutionOrder, ExecutionPosition, PortfolioSummary, OrderStatus
from app.engine.portfolio import VirtualPortfolio

class ExecutionProvider(ABC):
    """Abstract execution interface — Paper and Broker share same contract."""

    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @property
    @abstractmethod
    def execution_mode(self) -> str: ...

    @abstractmethod
    async def place_order(self, order: ExecutionOrder, current_price: float) -> ExecutionOrder: ...

    @abstractmethod
    async def get_positions(self) -> List[ExecutionPosition]: ...

    @abstractmethod
    async def get_portfolio_summary(self, current_prices: dict) -> PortfolioSummary: ...

class PaperExecutionProvider(ExecutionProvider):
    """
    Paper execution provider. Simulates fills and manages the VirtualPortfolio.
    Does NOT call any real broker.
    """
    def __init__(self, portfolio: VirtualPortfolio):
        self.portfolio = portfolio
        
    @property
    def provider_id(self) -> str:
        return "PAPER_PROVIDER"
        
    @property
    def execution_mode(self) -> str:
        return "PAPER"
        
    async def place_order(self, order: ExecutionOrder, current_price: float) -> ExecutionOrder:
        """
        Simulate order fill immediately for MVP.
        """
        # Simulate slippage (0.01%) and commission
        slippage = current_price * 0.0001
        fill_price = current_price + slippage if order.direction == "BUY" else current_price - slippage
        commission = fill_price * order.quantity * 0.0005 # 0.05% commission
        
        order.status = OrderStatus.FILLED
        order.filled_at = datetime.now()
        order.fill_price = fill_price
        order.commission = commission
        order.slippage = slippage
        
        self.portfolio.add_order(order)
        self.portfolio.update_position(order, order.filled_at)
        
        return order
        
    async def get_positions(self) -> List[ExecutionPosition]:
        return self.portfolio.get_positions()
        
    async def get_portfolio_summary(self, current_prices: dict) -> PortfolioSummary:
        return self.portfolio.get_summary(current_prices)
