from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.engine.models import ExecutionPosition, ExecutionOrder, PortfolioSummary, OrderStatus
from app.data.database.models import PortfolioStateDB, PositionDB, OrderDB

class VirtualPortfolio:
    """
    Deterministically manages the paper trading portfolio.
    Now backed by PostgreSQL.
    """
    def __init__(self, initial_capital: float = 100000.0, portfolio_id: str = "virtual"):
        self.portfolio_id = portfolio_id
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: List[ExecutionPosition] = []
        self.orders: List[ExecutionOrder] = []
        self.realized_pnl = 0.0

    def load_from_db(self, db: Session):
        """Loads state from the database."""
        state = db.query(PortfolioStateDB).filter(PortfolioStateDB.id == self.portfolio_id).first()
        if state:
            self.cash = state.cash
            self.realized_pnl = state.realized_pnl
        else:
            state = PortfolioStateDB(id=self.portfolio_id, cash=self.initial_capital, realized_pnl=0.0)
            db.add(state)
            db.commit()
            
        # Load positions
        db_positions = db.query(PositionDB).all()
        self.positions = []
        for p in db_positions:
            self.positions.append(ExecutionPosition(
                instrument_id=p.instrument_id,
                direction=p.direction,
                quantity=p.quantity,
                entry_price=p.entry_price,
                current_price=p.entry_price,
                unrealized_pnl=0.0,
                opened_at=p.opened_at
            ))
            
        # Load orders
        db_orders = db.query(OrderDB).all()
        self.orders = []
        for o in db_orders:
            # Reconstruct basic order info
            self.orders.append(ExecutionOrder(
                order_id=o.order_id,
                opportunity_id=o.opportunity_id,
                instrument_id=o.instrument_id,
                direction=o.direction,
                order_type=o.order_type,
                quantity=o.quantity,
                status=o.status,
                fill_price=o.fill_price,
                created_at=o.created_at,
                filled_at=o.filled_at
            ))
        
    def add_order(self, order: ExecutionOrder, db: Session = None):
        self.orders.append(order)
        if db:
            db_order = OrderDB(
                order_id=order.order_id,
                opportunity_id=order.opportunity_id,
                instrument_id=order.instrument_id,
                direction=order.direction,
                order_type=order.order_type,
                quantity=order.quantity,
                status=order.status.value if isinstance(order.status, OrderStatus) else order.status,
                fill_price=order.fill_price,
                created_at=order.created_at,
                filled_at=order.filled_at
            )
            db.add(db_order)
        
    def get_positions(self) -> List[ExecutionPosition]:
        return self.positions
        
    def get_open_orders(self) -> List[ExecutionOrder]:
        return [o for o in self.orders if o.status == "pending"]
        
    def update_position(self, order: ExecutionOrder, current_time: datetime, db: Session = None):
        """
        Applies a filled order to the portfolio positions and cash.
        Writes through to DB if session provided.
        """
        cost_basis = order.fill_price * order.quantity
        commission = order.commission or 0.0
        
        import uuid
        from app.data.database.models import TradeOpportunityDB, PaperTradingJournalDB
        
        # Load opportunity details for journal
        opp = None
        if db:
            opp = db.query(TradeOpportunityDB).filter_by(opportunity_id=order.opportunity_id).first()
        
        if order.direction == "BUY":
            self.cash -= (cost_basis + commission)
            
            existing = next((p for p in self.positions if p.instrument_id == order.instrument_id and p.direction == "LONG"), None)
            if existing:
                total_qty = existing.quantity + order.quantity
                avg_price = ((existing.entry_price * existing.quantity) + cost_basis) / total_qty
                existing.quantity = total_qty
                existing.entry_price = avg_price
                
                if db:
                    db_pos = db.query(PositionDB).filter_by(instrument_id=order.instrument_id, direction="LONG").first()
                    if db_pos:
                        db_pos.quantity = total_qty
                        db_pos.entry_price = avg_price
            else:
                new_pos = ExecutionPosition(
                    instrument_id=order.instrument_id,
                    direction="LONG",
                    quantity=order.quantity,
                    entry_price=order.fill_price,
                    current_price=order.fill_price,
                    unrealized_pnl=0.0,
                    opened_at=current_time
                )
                self.positions.append(new_pos)
                if db:
                    db.add(PositionDB(
                        id=str(uuid.uuid4()),
                        instrument_id=new_pos.instrument_id,
                        direction=new_pos.direction,
                        quantity=new_pos.quantity,
                        entry_price=new_pos.entry_price,
                        opened_at=new_pos.opened_at
                    ))
                    
            # Record Journal Entry (Open)
            if db and opp:
                session_id = None
                from app.data.database.models import PaperTradingSessionDB
                active_session = db.query(PaperTradingSessionDB).filter_by(status="ACTIVE").first()
                if active_session:
                    session_id = active_session.id
                    
                journal = PaperTradingJournalDB(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    opportunity_id=opp.opportunity_id,
                    symbol=order.instrument_id,
                    direction="LONG",
                    entry_price=order.fill_price,
                    quantity=order.quantity,
                    strategy=opp.strategy_evidence.get('strategy_id') if opp.strategy_evidence else None,
                    strategy_version=opp.strategy_version,
                    decision_mode=opp.decision_mode,
                    ai_score=opp.ai_confidence,
                    hybrid_score=opp.hybrid_score,
                    regime=opp.market_regime,
                    fees=commission,
                    slippage=0.0,
                    data_source="UPSTOX", # Hardcoded default for MVP, can be updated later
                    ai_source="MOCK / SIMULATED",
                    entry_time=current_time
                )
                db.add(journal)
                
        elif order.direction == "SELL":
            self.cash += (cost_basis - commission)
            
            existing = next((p for p in self.positions if p.instrument_id == order.instrument_id and p.direction == "LONG"), None)
            if existing:
                if order.quantity >= existing.quantity:
                    pnl = (order.fill_price - existing.entry_price) * existing.quantity
                    self.realized_pnl += pnl - commission
                    self.positions.remove(existing)
                    if db:
                        db_pos = db.query(PositionDB).filter_by(instrument_id=order.instrument_id, direction="LONG").first()
                        if db_pos:
                            db.delete(db_pos)
                            
                        # Update Journal (Close)
                        journal = db.query(PaperTradingJournalDB).filter_by(
                            symbol=order.instrument_id, 
                            direction="LONG",
                            exit_price=None
                        ).order_by(PaperTradingJournalDB.entry_time.desc()).first()
                        if journal:
                            journal.exit_price = order.fill_price
                            journal.exit_time = current_time
                            journal.realized_pnl = pnl - commission
                else:
                    pnl = (order.fill_price - existing.entry_price) * order.quantity
                    self.realized_pnl += pnl - commission
                    existing.quantity -= order.quantity
                    if db:
                        db_pos = db.query(PositionDB).filter_by(instrument_id=order.instrument_id, direction="LONG").first()
                        if db_pos:
                            db_pos.quantity = existing.quantity
                            
                        # Partially close journal (approximation for MVP)
                        journal = db.query(PaperTradingJournalDB).filter_by(
                            symbol=order.instrument_id, 
                            direction="LONG",
                            exit_price=None
                        ).order_by(PaperTradingJournalDB.entry_time.desc()).first()
                        if journal:
                            journal.exit_price = order.fill_price
                            journal.exit_time = current_time
                            journal.realized_pnl = pnl - commission
            else:
                new_pos = ExecutionPosition(
                    instrument_id=order.instrument_id,
                    direction="SHORT",
                    quantity=order.quantity,
                    entry_price=order.fill_price,
                    current_price=order.fill_price,
                    unrealized_pnl=0.0,
                    opened_at=current_time
                )
                self.positions.append(new_pos)
                if db:
                    db.add(PositionDB(
                        id=str(uuid.uuid4()),
                        instrument_id=new_pos.instrument_id,
                        direction=new_pos.direction,
                        quantity=new_pos.quantity,
                        entry_price=new_pos.entry_price,
                        opened_at=new_pos.opened_at
                    ))
                    
            # Record Journal Entry for Shorting (if not closing a long)
            if db and opp and not existing:
                session_id = None
                from app.data.database.models import PaperTradingSessionDB
                active_session = db.query(PaperTradingSessionDB).filter_by(status="ACTIVE").first()
                if active_session:
                    session_id = active_session.id
                    
                journal = PaperTradingJournalDB(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    opportunity_id=opp.opportunity_id,
                    symbol=order.instrument_id,
                    direction="SHORT",
                    entry_price=order.fill_price,
                    quantity=order.quantity,
                    strategy=opp.strategy_evidence.get('strategy_id') if opp.strategy_evidence else None,
                    strategy_version=opp.strategy_version,
                    decision_mode=opp.decision_mode,
                    ai_score=opp.ai_confidence,
                    hybrid_score=opp.hybrid_score,
                    regime=opp.market_regime,
                    fees=commission,
                    slippage=0.0,
                    data_source="UPSTOX",
                    ai_source="MOCK / SIMULATED",
                    entry_time=current_time
                )
                db.add(journal)

        if db:
            state = db.query(PortfolioStateDB).filter(PortfolioStateDB.id == self.portfolio_id).first()
            if state:
                state.cash = self.cash
                state.realized_pnl = self.realized_pnl

    def get_summary(self, current_prices: dict) -> PortfolioSummary:
        """
        Generates current portfolio summary based on latest prices.
        """
        positions_value = 0.0
        unrealized_pnl = 0.0
        
        for pos in self.positions:
            current_price = current_prices.get(pos.instrument_id, pos.current_price)
            pos.current_price = current_price
            if pos.direction == "LONG":
                pos.unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
                positions_value += current_price * pos.quantity
            else:
                pos.unrealized_pnl = (pos.entry_price - current_price) * pos.quantity
                # Simplifying short value
                positions_value += pos.entry_price * pos.quantity 
            unrealized_pnl += pos.unrealized_pnl
            
        total_value = self.cash + positions_value + unrealized_pnl
        total_pnl = self.realized_pnl + unrealized_pnl
        exposure = (positions_value / total_value) * 100 if total_value > 0 else 0.0
        
        return PortfolioSummary(
            total_value=total_value,
            cash=self.cash,
            positions_value=positions_value,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=self.realized_pnl,
            total_pnl=total_pnl,
            exposure_pct=exposure,
            drawdown=0.0, # Not calculating complex drawdown in MVP memory state
            max_drawdown=0.0,
            open_positions=len(self.positions),
            total_trades=len([o for o in self.orders if o.status == "filled"])
        )
