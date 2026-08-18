from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from app.engine.models import (
    TradeOpportunity, DecisionMode, Direction, 
    StrategyEvidence, AIEvidence, OpportunityStatus, DataReference
)
from app.strategies.base import StrategySignal
from app.intelligence.models import AIAnalysis

class HybridDecisionAggregator:
    """
    Deterministically combines strategy and AI evidence based on configurations.
    """
    def __init__(self):
        # MVP Configuration
        self.weights = {
            "strategy_signal": 0.50,
            "ai_signal": 0.50
        }
        self.agreement_bonus = 10.0
        self.disagreement_penalty = -10.0
        
    def aggregate(
        self, 
        strategy_evidence: Optional[StrategyEvidence], 
        ai_evidence: Optional[AIEvidence]
    ) -> Dict[str, Any]:
        """
        Calculates final combined score and determines direction.
        """
        if not strategy_evidence and not ai_evidence:
            raise ValueError("Must provide at least one source of evidence.")
            
        strat_score = strategy_evidence.signal_score if strategy_evidence else 0.0
        ai_score = ai_evidence.ai_score if ai_evidence else 0.0
        
        strat_dir = strategy_evidence.signal_type if strategy_evidence else None
        ai_dir = ai_evidence.direction if ai_evidence else None
        
        if strategy_evidence and ai_evidence:
            # Hybrid
            score = (strat_score * self.weights["strategy_signal"]) + (ai_score * self.weights["ai_signal"])
            if strat_dir == ai_dir:
                score += self.agreement_bonus
                direction = strat_dir
            else:
                score += self.disagreement_penalty
                # Default to strategy direction in conflict for MVP, or could reject
                direction = strat_dir
                
            score = max(0.0, min(100.0, score))
            return {"score": score, "direction": Direction(direction)}
            
        elif strategy_evidence:
            return {"score": strat_score, "direction": Direction(strat_dir)}
        elif ai_evidence:
            return {"score": ai_score, "direction": Direction(ai_dir)}

class SignalEngine:
    """
    Central orchestration layer. Consumes outputs and produces TradeOpportunities.
    """
    def __init__(self):
        self.aggregator = HybridDecisionAggregator()
        
    def create_opportunity(
        self,
        symbol: str,
        timestamp: datetime,
        decision_mode: DecisionMode,
        timeframe: Optional[str] = None,
        strategy_signal: Optional[StrategySignal] = None,
        ai_analysis: Optional[AIAnalysis] = None
    ) -> TradeOpportunity:
        
        strat_ev = None
        if strategy_signal and decision_mode in [DecisionMode.STRATEGY_ONLY, DecisionMode.HYBRID]:
            direction_str = "BUY" if strategy_signal.direction == 1 else ("SELL" if strategy_signal.direction == -1 else "FLAT")
            strat_ev = StrategyEvidence(
                strategy_id=getattr(strategy_signal, "strategy_id", "strat"), 
                strategy_name=getattr(strategy_signal, "strategy_name", "Strat"), 
                strategy_version=getattr(strategy_signal, "strategy_version", "1.0"),
                parameters={},
                signal_type=direction_str,
                signal_score=80.0,
                features_used={},
                explanation="Strategy generated signal."
            )
            
        ai_ev = None
        if ai_analysis and decision_mode in [DecisionMode.AI_ONLY, DecisionMode.HYBRID]:
            # Convert AIAnalysis
            ai_ev = AIEvidence(
                ai_model_id=ai_analysis.provider_id,
                ai_model_version="1.0",
                direction="BUY" if "Bullish" in ai_analysis.market_context else "SELL", # Simplistic
                ai_score=ai_analysis.confidence * 100,
                reasoning=[ai_analysis.thesis],
                retrieved_facts=[],
                computed_values={},
                model_inference="Inference",
                uncertainty="None",
                evidence_sources=[]
            )
            
        # Validate inputs for mode
        if decision_mode == DecisionMode.STRATEGY_ONLY and not strat_ev:
            raise ValueError("STRATEGY_ONLY mode requires strategy signal.")
        if decision_mode == DecisionMode.AI_ONLY and not ai_ev:
            raise ValueError("AI_ONLY mode requires AI analysis.")
            
        # Aggregate
        agg_result = self.aggregator.aggregate(strat_ev, ai_ev)
        
        # Risk level determination based on score
        risk_level = "LOW" if agg_result["score"] > 80 else "MEDIUM"
        
        return TradeOpportunity(
            symbol=symbol,
            instrument_id=symbol,
            timeframe=timeframe,
            timestamp=timestamp,
            decision_mode=decision_mode,
            direction=agg_result["direction"],
            confidence_score=agg_result["score"],
            strategy_version=strat_ev.strategy_version if strat_ev else None,
            ai_confidence=ai_analysis.confidence if ai_analysis else None,
            hybrid_score=agg_result["score"] if decision_mode == DecisionMode.HYBRID else None,
            strategy_evidence=strat_ev,
            ai_evidence=ai_ev,
            market_regime=ai_analysis.market_context if ai_analysis else "Unknown",
            reasoning=["Aggregated by SignalEngine"],
            data_references=[],
            risk_level=risk_level
        )
