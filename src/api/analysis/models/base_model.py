# src/api/analysis/models/base_model.py
from abc import ABC
import os
import re
import joblib
from typing import List, Tuple

class BaseModel(ABC):
    """
    Classe de base pour tous les modèles de prédiction.
    Gère la sauvegarde, le chargement et l'inspection des modèles.
    """

    def __init__(self, ticker: str, features: list):
        self.ticker = ticker
        self.features = features
        self.model = None
        self.optimal_buy_threshold = None  # Seuil optimal pour la stratégie d'achat

    # -----------------------------
    # Sauvegarde du modèle
    # -----------------------------
    def save(self, directory="models", filename=None):
        """
        Sauvegarde le modèle et ses métadonnées dans un fichier .joblib
        """
        os.makedirs(directory, exist_ok=True)
        if filename is None:
            filename = f"{self.__class__.__name__}_{self.ticker.upper()}.joblib"

        payload = {
            "model_class": self.__class__.__name__,
            "ticker": self.ticker,
            "features": self.features,
            "model": self.model,
            "optimal_buy_threshold": self.optimal_buy_threshold
        }

        filepath = os.path.join(directory, filename)
        joblib.dump(payload, filepath)
        print(f"Model saved: {filepath}")

    # -----------------------------
    # Liste des modèles sauvegardés
    # -----------------------------
    
    @staticmethod
    def list_saved_models(directory: str = "models", model_class: str = None, ticker: str = None) -> List[Tuple[str, str, str]]:
        """
        Liste tous les modèles sauvegardés dans un répertoire donné.
        
        :param directory: dossier contenant les fichiers .joblib
        :param model_class: si fourni, filtre par classe de modèle
        :param ticker: si fourni, filtre par ticker
        :return: liste de tuples (filename, model_class, ticker)
        """
        if not os.path.exists(directory):
            return []

        model_files = [f for f in os.listdir(directory) if f.endswith('.joblib')]
        result = []

        for file in model_files:
            match = re.match(r"([a-zA-Z0-9]+)_([A-Z0-9]+)\.joblib", file)
            if match:
                mc, tk = match.groups()
                if model_class and mc != model_class:
                    continue
                if ticker and tk != ticker:
                    continue
                result.append((file, mc, tk))
        return result
    
    # -----------------------------
    # Chargement du modèle
    # -----------------------------
    @staticmethod
    def load(ticker: str = None, directory="models", filename=None):
        """
        Recharge un modèle et renvoie l'instance complète.
        Si filename n'est pas fourni, cherche un fichier contenant le ticker.
        """
        if filename is None:
            if ticker is None:
                raise ValueError("ticker ou filename doit être fourni")
            # Cherche un fichier contenant le ticker
            files = [f for f in os.listdir(directory)
                     if f.endswith(".joblib") and ticker.upper() in f.upper()]
            if not files:
                raise FileNotFoundError(f"Aucun fichier modèle trouvé pour {ticker} dans {directory}")
            filename = files[0]

        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        payload = joblib.load(filepath)
        model_class_name = payload["model_class"]
        
        # Import ModelFactory locally to prevent circular import
        from .model_factory import ModelFactory
        
        model_instance = ModelFactory.create_model(
            model_class_name, payload["ticker"], payload["features"]
        )
        model_instance.model = payload["model"]
        model_instance.optimal_buy_threshold = payload.get("optimal_buy_threshold", None)

        return model_instance

    # -----------------------------
    # Inspection rapide
    # -----------------------------
    @staticmethod
    def inspect(model_path: str):
        """
        Affiche joliment le contenu d’un modèle sauvegardé (.joblib)
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        payload = joblib.load(model_path)
        import pprint
        print(f"\nInspecting model file: {model_path}")
        pprint.pprint(payload, indent=2, width=120)
        return payload
