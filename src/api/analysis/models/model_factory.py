from .random_forest_model import RandomForestModel

class ModelFactory:
    """
    Fabrique pour instancier dynamiquement les modèles de prédiction.
    """
    _models = {
        "RandomForestModel": RandomForestModel,
        # Ajouter d'autres modèles ici au fur et à mesure
    }

    @classmethod
    def create_model(cls, model_class_name: str, ticker: str, features: list, **kwargs):
        """
        Crée une instance d'un modèle spécifié par son nom de classe.
        """
        model_class = cls._models.get(model_class_name)
        if not model_class:
            raise ValueError(f"Classe de modèle inconnue : {model_class_name}")
        return model_class(ticker, features, **kwargs)

    @classmethod
    def get_available_models(cls):
        """
        Retourne la liste des noms de classes de modèles disponibles.
        """
        return list(cls._models.keys())
