from abc import ABC, abstractmethod
import joblib
import os

class BaseModel(ABC):
    """
    Classe de base abstraite pour les modèles de prédiction.
    Définit l'interface commune pour l'entraînement, la prédiction, la sauvegarde et le chargement des modèles.
    """

    def __init__(self, ticker: str, features: list):
        self.ticker = ticker
        self.features = features
        self.model = None

    @abstractmethod
    def train(self, X_train, y_train, **kwargs):
        """
        Entraîne le modèle avec les données fournies.
        """
        pass

    @abstractmethod
    def predict_proba(self, X_test) -> list:
        """
        Effectue des prédictions de probabilité sur les données de test.
        Doit retourner les probabilités de la classe positive (ex: probabilité de hausse).
        """
        pass

    def save(self, directory: str = None):
        """
        Sauvegarde le modèle entraîné et ses métadonnées.
        """
        if self.model is None:
            raise ValueError("Le modèle n'a pas été entraîné. Impossible de sauvegarder.")

        if directory is None:
            directory = os.path.join(os.path.dirname(__file__), 'trained_models')
        os.makedirs(directory, exist_ok=True)

        model_filename = f"buy_signal_classifier_{self.ticker.lower()}.joblib"
        model_path = os.path.join(directory, model_filename)

        payload = {
            'model': self.model,
            'features': self.features,
            'ticker': self.ticker,
            'model_class': self.__class__.__name__ # Pour identifier la classe lors du chargement
        }
        joblib.dump(payload, model_path)
        print(f"Modèle sauvegardé à : {model_path}")

    @classmethod
    def load(cls, ticker: str, directory: str = None):
        """
        Charge un modèle entraîné et ses métadonnées.
        """
        if directory is None:
            directory = os.path.join(os.path.dirname(__file__), 'trained_models')

        model_filename = f"buy_signal_classifier_{ticker.lower()}.joblib"
        model_path = os.path.join(directory, model_filename)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle non trouvé à {model_path}.")

        payload = joblib.load(model_path)
        # Ici, nous devrions idéalement instancier la classe de modèle concrète
        # en fonction de 'model_class' dans le payload. Pour l'instant, nous retournons le payload.
        # Cette logique sera affinée avec un ModelFactory.
        return payload
