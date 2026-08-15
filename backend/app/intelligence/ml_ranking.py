import pandas as pd
import numpy as np
from typing import List, Dict, Any
from app.intelligence.models import StrategyRanking

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import mean_squared_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class MLStrategyRanker:
    """
    Machine Learning component to rank strategies based on expected forward returns.
    Strictly enforces temporal validation.
    """
    
    def __init__(self):
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for MLStrategyRanker")
            
        # Baseline model
        self.model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
        self.is_trained = False
        self.feature_cols = []
        
    def validate_temporally(self, df: pd.DataFrame, feature_cols: List[str], target_col: str) -> float:
        """
        Validates the model using TimeSeriesSplit to guarantee no future-data leakage.
        Returns the average MSE across chronological folds.
        """
        # Ensure data is sorted by time
        df = df.sort_values(by="timestamp").reset_index(drop=True)
        
        X = df[feature_cols].fillna(0)
        y = df[target_col].fillna(0)
        
        tscv = TimeSeriesSplit(n_splits=3)
        mses = []
        
        for train_index, test_index in tscv.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            # Temporary model for validation fold
            fold_model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
            fold_model.fit(X_train, y_train)
            
            preds = fold_model.predict(X_test)
            mses.append(mean_squared_error(y_test, preds))
            
        return float(np.mean(mses))
        
    def train(self, df: pd.DataFrame, feature_cols: List[str], target_col: str):
        """
        Trains the final ranking model on all available historical data.
        """
        self.feature_cols = feature_cols
        X = df[feature_cols].fillna(0)
        y = df[target_col].fillna(0)
        
        self.model.fit(X, y)
        self.is_trained = True
        
    def rank_strategies(self, current_features: List[Dict[str, Any]]) -> List[StrategyRanking]:
        """
        Given a list of feature dictionaries (one for each strategy at the current timestamp),
        predict their scores and return a ranked list.
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before ranking.")
            
        rankings = []
        
        for item in current_features:
            strategy_id = item["strategy_id"]
            strategy_version = item.get("strategy_version", "1.0.0")
            
            # Extract only the required features in the correct order
            X_input = pd.DataFrame([{col: item.get(col, 0.0) for col in self.feature_cols}])
            
            score = self.model.predict(X_input)[0]
            
            rankings.append(StrategyRanking(
                strategy_id=strategy_id,
                strategy_version=strategy_version,
                score=float(score),
                rank=0, # Placeholder, will be sorted
                supporting_features={col: float(item.get(col, 0.0)) for col in self.feature_cols},
                model_id="RandomForest_v1"
            ))
            
        # Sort by score descending
        rankings.sort(key=lambda x: x.score, reverse=True)
        
        # Assign ranks
        for i, ranking in enumerate(rankings):
            ranking.rank = i + 1
            
        return rankings
