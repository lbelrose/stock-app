import pandas as pd
import yfinance as yf
import joblib
import os
import json
from datetime import datetime, timedelta
from .services import PredictionService
from .features import generate_technical_features

# Charger les seuils optimisés
OPTIMIZED_THRESHOLDS_PATH = os.path.join(os.path.dirname(__file__), 'optimized_thresholds.json')
try:
    with open(OPTIMIZED_THRESHOLDS_PATH, 'r') as f:
        OPTIMIZED_THRESHOLDS = json.load(f)
except FileNotFoundError:
    print(f"Attention: Le fichier de seuils optimisés n'a pas été trouvé à {OPTIMIZED_THRESHOLDS_PATH}. Utilisation des valeurs par défaut.")
    OPTIMIZED_THRESHOLDS = {}

def predict_next_day_movement(ticker):
    """
    Predicts the probability of an upward movement for the next trading day.
    This function now leverages the centralized prediction logic in PredictionService.
    """
    # Récupérer le seuil optimisé et le nom du modèle pour le ticker, ou utiliser des valeurs par défaut
    ticker_info = OPTIMIZED_THRESHOLDS.get(ticker.upper(), {})
    model_name = ticker_info.get('model_name', "buy_signal_classifier_general.joblib")
    buy_threshold = ticker_info.get('optimal_buy_threshold', 0.55) # Seuil par défaut si non trouvé

    print(f"Prédiction pour {ticker} avec le modèle {model_name} et le seuil d'achat {buy_threshold:.2f}...")

    model_path = os.path.join(os.path.dirname(__file__), 'models', model_name)
    if not os.path.exists(model_path):
        print(f"Modèle non trouvé à {model_path}. Impossible de faire la prédiction.")
        return None, None
    
    payload = joblib.load(model_path)
    model = payload['model']
    feature_names = payload['features']

    # Use the centralized prediction logic
    try:
        prediction_result = PredictionService._generate_prediction_for_model(
            ticker=ticker,
            model=model,
            feature_names=feature_names,
            model_type=f"standalone ({model_name})"
        )
    except (ValueError, FileNotFoundError) as e:
        print(f"Erreur lors de la prédiction pour {ticker}: {e}")
        return None, None

    proba_up = float(prediction_result['probability_up'])
    signal = proba_up >= buy_threshold

    print(f"Probabilité que le cours de {ticker} monte : {proba_up:.2%}")
    if signal:
        print(f"Signal d'ACHAT pour {ticker} (probabilité >= {buy_threshold:.2%})")
    else:
        print(f"Pas de signal d'achat pour {ticker} (probabilité < {buy_threshold:.2%})")
    
    return proba_up, signal

if __name__ == "__main__":
    # Exemple d'utilisation pour AMZN
    ticker_to_predict = "AMZN"
    
    print(f"--- Prédiction pour le prochain jour de bourse de {ticker_to_predict} ---")
    prob, signal = predict_next_day_movement(ticker_to_predict)
    
    print("\n" + "="*50)
    print(f"Résultat final pour {ticker_to_predict}:")
    if prob is not None:
        print(f"Probabilité de hausse: {prob:.2%}")
        print(f"Signal d'achat: {'Oui' if signal else 'Non'}")
    else:
        print("Prédiction non disponible.")
    print("="*50)
