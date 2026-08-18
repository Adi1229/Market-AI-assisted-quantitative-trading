from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.data.database.session import get_db
from app.api.schemas import WatchlistCreate, WatchlistResponse, MessageResponse
from app.data.database.models import WatchlistDB, WatchlistInstrumentDB

router = APIRouter()

@router.get("/", response_model=List[WatchlistResponse])
def get_watchlists(db: Session = Depends(get_db)):
    db_watchlists = db.query(WatchlistDB).all()
    results = []
    for w in db_watchlists:
        instruments = db.query(WatchlistInstrumentDB).filter_by(watchlist_id=w.id).all()
        results.append(WatchlistResponse(
            id=w.id,
            name=w.name,
            instruments=[i.symbol for i in instruments],
            created_at=w.created_at
        ))
    return results

@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def create_watchlist(watchlist: WatchlistCreate, db: Session = Depends(get_db)):
    new_id = str(uuid.uuid4())
    db_watchlist = WatchlistDB(id=new_id, name=watchlist.name)
    db.add(db_watchlist)
    db.commit()
    db.refresh(db_watchlist)
    return WatchlistResponse(
        id=db_watchlist.id,
        name=db_watchlist.name,
        instruments=[],
        created_at=db_watchlist.created_at
    )

@router.post("/{watchlist_id}/instruments/{symbol}", response_model=MessageResponse)
def add_instrument(watchlist_id: str, symbol: str, db: Session = Depends(get_db)):
    w = db.query(WatchlistDB).filter_by(id=watchlist_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Watchlist not found")
        
    existing = db.query(WatchlistInstrumentDB).filter_by(watchlist_id=watchlist_id, symbol=symbol).first()
    if existing:
        return MessageResponse(message="Instrument already in watchlist")
        
    instr = WatchlistInstrumentDB(id=str(uuid.uuid4()), watchlist_id=watchlist_id, symbol=symbol)
    db.add(instr)
    db.commit()
    return MessageResponse(message=f"Added {symbol} to watchlist {w.name}")

@router.delete("/{watchlist_id}/instruments/{symbol}", response_model=MessageResponse)
def remove_instrument(watchlist_id: str, symbol: str, db: Session = Depends(get_db)):
    w = db.query(WatchlistDB).filter_by(id=watchlist_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Watchlist not found")
        
    instr = db.query(WatchlistInstrumentDB).filter_by(watchlist_id=watchlist_id, symbol=symbol).first()
    if not instr:
        raise HTTPException(status_code=404, detail="Instrument not found in watchlist")
        
    db.delete(instr)
    db.commit()
    return MessageResponse(message=f"Removed {symbol} from watchlist {w.name}")
