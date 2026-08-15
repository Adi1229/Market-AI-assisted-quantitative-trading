from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import json

from app.api.dependencies import get_signal_engine, get_workflow_orchestrator
from app.data.database.session import get_db
from app.data.database.models import TradeOpportunityDB
from app.engine.signal import SignalEngine
from app.engine.workflow import WorkflowOrchestrator
from app.engine.models import DecisionMode, OpportunityStatus, TradeOpportunity, StrategyEvidence, AIEvidence
from app.api.schemas import (
    OpportunityResponse, ApproveRequest, RejectRequest, MessageResponse,
    DecisionModeUpdate, StrategyEvidenceResponse, AIEvidenceResponse
)

router = APIRouter()

def _db_to_pydantic(db_opp: TradeOpportunityDB) -> TradeOpportunity:
    strat_ev = None
    if db_opp.strategy_evidence:
        strat_ev = StrategyEvidence(**db_opp.strategy_evidence)
    ai_ev = None
    if db_opp.ai_evidence:
        ai_ev = AIEvidence(**db_opp.ai_evidence)
        
    return TradeOpportunity(
        opportunity_id=db_opp.opportunity_id,
        symbol=db_opp.symbol,
        instrument_id=db_opp.symbol, # For MVP, symbol and instrument_id are the same
        timestamp=db_opp.timestamp,
        decision_mode=DecisionMode(db_opp.decision_mode),
        direction=db_opp.direction,
        confidence_score=db_opp.confidence_score,
        strategy_evidence=strat_ev,
        ai_evidence=ai_ev,
        market_regime="N/A", # not fully persisted in Phase 7 simple model
        risk_level="MEDIUM", # dummy
        reasoning=[],
        data_references=[],
        status=OpportunityStatus(db_opp.status)
    )

@router.get("/opportunities", response_model=List[OpportunityResponse])
def list_opportunities(db: Session = Depends(get_db)):
    """List recent trade opportunities."""
    db_opps = db.query(TradeOpportunityDB).order_by(TradeOpportunityDB.timestamp.desc()).limit(50).all()
    
    results = []
    for db_opp in db_opps:
        opp = _db_to_pydantic(db_opp)
        strat_ev = None
        if opp.strategy_evidence:
            strat_ev = StrategyEvidenceResponse(
                strategy_id=opp.strategy_evidence.strategy_id,
                strategy_name=opp.strategy_evidence.strategy_name,
                signal_direction=1 if opp.strategy_evidence.signal_type == "BUY" else -1 if opp.strategy_evidence.signal_type == "SELL" else 0,
                signal_score=opp.strategy_evidence.signal_score,
                signal_type=opp.strategy_evidence.signal_type
            )
            
        ai_ev = None
        if opp.ai_evidence:
            ai_ev = AIEvidenceResponse(
                provider_id=opp.ai_evidence.ai_model_id,
                direction=opp.ai_evidence.direction,
                ai_score=opp.ai_evidence.ai_score,
                market_context="Computed values: " + str(opp.ai_evidence.computed_values),
                thesis=opp.ai_evidence.model_inference
            )
            
        results.append(
            OpportunityResponse(
                opportunity_id=opp.opportunity_id,
                symbol=opp.symbol,
                timestamp=opp.timestamp,
                decision_mode=opp.decision_mode.value,
                direction=opp.direction.value if hasattr(opp.direction, 'value') else opp.direction,
                confidence_score=opp.confidence_score,
                status=opp.status.value,
                suggested_entry=opp.suggested_entry,
                market_regime=opp.market_regime,
                risk_level=opp.risk_level,
                strategy_evidence=strat_ev,
                ai_evidence=ai_ev,
                reasoning=opp.reasoning
            )
        )
    return results

@router.get("/opportunities/{opp_id}", response_model=OpportunityResponse)
def get_opportunity(opp_id: str, db: Session = Depends(get_db)):
    db_opp = db.query(TradeOpportunityDB).filter(TradeOpportunityDB.opportunity_id == opp_id).first()
    if not db_opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    opp = _db_to_pydantic(db_opp)
    
    strat_ev = None
    if opp.strategy_evidence:
        strat_ev = StrategyEvidenceResponse(
            strategy_id=opp.strategy_evidence.strategy_id,
            strategy_name=opp.strategy_evidence.strategy_name,
            signal_direction=1 if opp.strategy_evidence.signal_type == "BUY" else -1 if opp.strategy_evidence.signal_type == "SELL" else 0,
            signal_score=opp.strategy_evidence.signal_score,
            signal_type=opp.strategy_evidence.signal_type
        )
        
    ai_ev = None
    if opp.ai_evidence:
        ai_ev = AIEvidenceResponse(
            provider_id=opp.ai_evidence.ai_model_id,
            direction=opp.ai_evidence.direction,
            ai_score=opp.ai_evidence.ai_score,
            market_context="Computed values: " + str(opp.ai_evidence.computed_values),
            thesis=opp.ai_evidence.model_inference
        )
        
    return OpportunityResponse(
        opportunity_id=opp.opportunity_id,
        symbol=opp.symbol,
        timestamp=opp.timestamp,
        decision_mode=opp.decision_mode.value,
        direction=opp.direction.value if hasattr(opp.direction, 'value') else opp.direction,
        confidence_score=opp.confidence_score,
        status=opp.status.value,
        suggested_entry=opp.suggested_entry,
        market_regime=opp.market_regime,
        risk_level=opp.risk_level,
        strategy_evidence=strat_ev,
        ai_evidence=ai_ev,
        reasoning=opp.reasoning
    )

@router.post("/opportunities/{opp_id}/approve", response_model=MessageResponse)
async def approve_opportunity(
    opp_id: str, 
    req: ApproveRequest,
    orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator),
    db: Session = Depends(get_db)
):
    """User approves trade (TAKE_TRADE)."""
    db_opp = db.query(TradeOpportunityDB).filter(TradeOpportunityDB.opportunity_id == opp_id).first()
    if not db_opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    opp = _db_to_pydantic(db_opp)
    
    try:
        order = await orchestrator.process_user_action(opp, "TAKE_TRADE", req.current_price, db=db)
        if not order:
            raise HTTPException(status_code=400, detail="Order could not be processed (potentially duplicate/idempotency or rejected).")
        return MessageResponse(message=f"Opportunity {opp_id} executed. Order ID: {order.order_id}")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=403, detail=str(e)) # E.g., LIVE execution disabled
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/opportunities/{opp_id}/ignore", response_model=MessageResponse)
async def ignore_opportunity(
    opp_id: str, 
    req: RejectRequest,
    orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator),
    db: Session = Depends(get_db)
):
    """User rejects trade (IGNORE)."""
    db_opp = db.query(TradeOpportunityDB).filter(TradeOpportunityDB.opportunity_id == opp_id).first()
    if not db_opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    opp = _db_to_pydantic(db_opp)
    try:
        await orchestrator.process_user_action(opp, "IGNORE", req.current_price, db=db)
        return MessageResponse(message=f"Opportunity {opp_id} ignored.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/signal-engine/mode", response_model=MessageResponse)
def set_decision_mode(req: DecisionModeUpdate):
    """Configure active decision mode."""
    valid_modes = [m.value for m in DecisionMode]
    if req.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Must be one of {valid_modes}")
    
    # Store globally or in settings - for MVP we just return success
    return MessageResponse(message=f"Decision mode set to {req.mode}")

# --- INTERNAL TEST MOCK ---
@router.post("/test/generate_mock_opportunity")
async def generate_mock_opportunity(
    orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator),
    signal_engine: SignalEngine = Depends(get_signal_engine),
    db: Session = Depends(get_db)
):
    """Generate a mock opportunity for testing the UI."""
    from app.strategies.base import StrategySignal
    from app.intelligence.models import AIAnalysis
    import uuid
    
    unique_symbol = f"TEST_SYM_{uuid.uuid4().hex[:6]}"
    
    strategy_sig = StrategySignal(symbol=unique_symbol, strategy_id="mock", strategy_version="1", direction=1, features={}, timestamp=datetime.now())
    ai_analysis = AIAnalysis(
        symbol=unique_symbol, timestamp=datetime.now(), market_context="Bullish",
        thesis="Strong fundamentals and trend.", sentiment_evidence=[], fundamental_evidence=[],
        quantitative_evidence={}, provider_id="MockAI", confidence=0.85, risks=[]
    )
    
    opp = signal_engine.create_opportunity(
        symbol=unique_symbol, timestamp=datetime.now(), decision_mode=DecisionMode.HYBRID,
        strategy_signal=strategy_sig, ai_analysis=ai_analysis
    )
    opp.suggested_position_size = 10.0
    
    # Push through risk to await approval
    await orchestrator.process_new_opportunity(opp, current_price=2450.0, db=db)
    
    return {"message": "Mock opportunity generated", "opportunity_id": opp.opportunity_id}
