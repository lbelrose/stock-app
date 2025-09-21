import pandas as pd
import yfinance as yf
import joblib
import os
from datetime import datetime, timedelta
from .services import PredictionService
from .features import generate_technical_features

def predict_next_day_movement(ticker, model_name="buy_signal_classifier_general.joblib", buy_threshold=0.55):
    """
    Predicts the probability of an upward movement for the next trading day.
    This function now leverages the centralized prediction logic in PredictionService.
    """
    print(f"Prédiction pour {ticker} avec le modèle {model_name}...")

    # We need to load the model and features to pass them to _generate_prediction_for_model
    # This part is still necessary as predict_next_day_movement can be called independently
    model_path = os.path.join(os.path.dirname(__file__), 'models', model_name)
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Cannot make prediction.")
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
    model_file = "buy_signal_classifier_amzn.joblib"
    
    print(f"--- Prédiction pour le prochain jour de bourse de {ticker_to_predict} ---")
    prob, signal = predict_next_day_movement(ticker_to_predict, model_file)
    
    print("\n" + "="*50)
    print(f"Résultat final pour {ticker_to_predict}:")
    if prob is not None:
        print(f"Probabilité de hausse: {prob:.2%}")
        print(f"Signal d'achat: {'Oui' if signal else 'Non'}")
    else:
        print("Prédiction non disponible.")
    print("="*50)
