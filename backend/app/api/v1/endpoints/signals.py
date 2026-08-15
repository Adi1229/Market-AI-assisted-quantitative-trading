from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime

from app.api.dependencies import get_signal_engine, get_workflow_orchestrator
from app.engine.signal import SignalEngine
from app.engine.workflow import WorkflowOrchestrator
from app.engine.models import DecisionMode, OpportunityStatus
from app.api.schemas import (
    OpportunityResponse, ApproveRequest, RejectRequest, MessageResponse,
    DecisionModeUpdate, StrategyEvidenceResponse, AIEvidenceResponse
)

router = APIRouter()

# MVP mock memory for generated opportunities to list in UI
_opportunities_store = {}

@router.get("/opportunities", response_model=List[OpportunityResponse])
def list_opportunities():
    """List recent trade opportunities."""
    # Convert internal to schema response
    results = []
    for opp in _opportunities_store.values():
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
                direction=opp.direction.value,
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
def get_opportunity(opp_id: str):
    if opp_id not in _opportunities_store:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    opp = _opportunities_store[opp_id]
    
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
        direction=opp.direction.value,
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
    orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator)
):
    """User approves trade (TAKE_TRADE)."""
    if opp_id not in _opportunities_store:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    opp = _opportunities_store[opp_id]
    
    try:
        order = await orchestrator.process_user_action(opp, "TAKE_TRADE", req.current_price)
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
    orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator)
):
    """User rejects trade (IGNORE)."""
    if opp_id not in _opportunities_store:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    opp = _opportunities_store[opp_id]
    try:
        await orchestrator.process_user_action(opp, "IGNORE", req.current_price)
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
    signal_engine: SignalEngine = Depends(get_signal_engine)
):
    """Generate a mock opportunity for testing the UI."""
    from app.strategies.base import StrategySignal
    from app.intelligence.models import AIAnalysis
    
    strategy_sig = StrategySignal(symbol="RELIANCE", strategy_id="mock", strategy_version="1", direction=1, features={}, timestamp=datetime.now())
    ai_analysis = AIAnalysis(
        symbol="RELIANCE", timestamp=datetime.now(), market_context="Bullish",
        thesis="Strong fundamentals and trend.", sentiment_evidence=[], fundamental_evidence=[],
        quantitative_evidence={}, provider_id="MockAI", confidence=0.85, risks=[]
    )
    
    opp = signal_engine.create_opportunity(
        symbol="RELIANCE", timestamp=datetime.now(), decision_mode=DecisionMode.HYBRID,
        strategy_signal=strategy_sig, ai_analysis=ai_analysis
    )
    opp.suggested_position_size = 10.0
    
    _opportunities_store[opp.opportunity_id] = opp
    
    # Push through risk to await approval
    await orchestrator.process_new_opportunity(opp, current_price=2450.0)
    
    return {"message": "Mock opportunity generated", "opportunity_id": opp.opportunity_id}
