from sklearn.ensemble import RandomForestClassifier
from .base_model import BaseModel

class RandomForestModel(BaseModel):
    """
    Implémentation d'un modèle RandomForestClassifier.
    """

    def __init__(self, ticker: str, features: list, **kwargs):
        super().__init__(ticker, features)
        # Définir les hyperparamètres par défaut et les surcharger avec kwargs
        default_params = {
            "n_estimators": 100,
            "max_depth": 5,
            "min_samples_split": 20,
            "min_samples_leaf": 10,
            "random_state": 42,
            "n_jobs": -1
        }
        final_params = {**default_params, **kwargs}
        self.model = RandomForestClassifier(**final_params)

    def train(self, X_train, y_train, **kwargs):
        """
        Entraîne le RandomForestClassifier.
        """
        print(f"Entraînement du modèle RandomForest pour {self.ticker}...")
        self.model.fit(X_train, y_train)
        print(f"Modèle RandomForest pour {self.ticker} entraîné.")

    def predict_proba(self, X_test) -> list:
        """
        Effectue des prédictions de probabilité avec le RandomForestClassifier.
        Retourne les probabilités de la classe positive (1).
        """
        if self.model is None:
            raise ValueError("Le modèle n'a pas été entraîné. Impossible de faire des prédictions.")
        return self.model.predict_proba(X_test)[:, 1]
