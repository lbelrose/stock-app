# src/api/analysis/models/xgboost_model.py
import xgboost as xgb
from .base_model import BaseModel

class XGBoostModel(BaseModel):
    """
    Implementation of an XGBoost Classifier model.
    """

    def __init__(self, ticker: str, features: list, **kwargs):
        super().__init__(ticker, features)
        # Define default hyperparameters and override with kwargs
        default_params = {
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "n_estimators": 100,
            "max_depth": 3,
            "learning_rate": 0.1,
            "random_state": 42
        }
        final_params = {**default_params, **kwargs}
        self.model = xgb.XGBClassifier(**final_params)

    def train(self, X_train, y_train, **kwargs):
        """
        Trains the XGBoostClassifier.
        """
        print(f"Training XGBoost model for {self.ticker}...")
        self.model.fit(X_train, y_train, **kwargs)
        print(f"XGBoost model for {self.ticker} trained.")

    def predict_proba(self, X_test) -> list:
        """
        Performs probability predictions with the XGBoostClassifier.
        Returns the probabilities for the positive class (1).
        """
        if self.model is None:
            raise ValueError("Model has not been trained. Cannot make predictions.")
        return self.model.predict_proba(X_test)[:, 1]
