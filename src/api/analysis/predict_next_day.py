import pandas as pd
import yfinance as yf
import os
import json
import argparse
from datetime import datetime, timedelta

from features import generate_technical_features
from models.base_model import BaseModel
from models.model_factory import ModelFactory

def predict_next_day(ticker: str):
    """
    Predicts the next day's price movement for a given ticker using the trained model
    and optimized threshold.
    """
    print(f"Starting prediction for {ticker}...")

    # 1. Load optimized threshold and model class name
    optimized_thresholds_path = os.path.join(os.path.dirname(__file__), 'optimized_thresholds.json')
    with open(optimized_thresholds_path, 'r') as f:
        optimized_thresholds = json.load(f)

    if ticker not in optimized_thresholds:
        raise ValueError(f"No optimized threshold found for {ticker}. Train the model first.")

    ticker_data = optimized_thresholds[ticker]
    buy_threshold = ticker_data['optimal_buy_threshold']
    model_class_name = ticker_data.get('model_class_name', 'RandomForestModel') # Default to RandomForestModel

    # 2. Fetch recent data (need enough for features and one day lag)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60) # Get enough data for feature calculation
    data = yf.Ticker(ticker).history(start=start_date, end=end_date)

    if data.empty:
        raise ValueError(f"No recent data for {ticker}")
    data = data.sort_index(ascending=True)

    # 3. Generate features
    feature_df = generate_technical_features(data)

    # 4. Prepare data for prediction (last available day, lagged)
    # We need the features for the *last complete day* to predict the *next day*
    X_predict = feature_df.iloc[[-2]] # Get the second to last row for prediction (features of yesterday)
    
    # Ensure feature names match the trained model
    # Load model to get feature names
    payload = BaseModel.load(ticker, directory=os.path.join(os.path.dirname(__file__), 'models'))
    model_features = payload['features']

    X_predict = X_predict[model_features].dropna()

    if X_predict.empty:
        raise ValueError("Not enough data to generate features for prediction after lagging.")

    # 5. Load model
    model_instance = ModelFactory.create_model(model_class_name, ticker, model_features)
    model_instance.model = payload['model'] # Assign the loaded sklearn model

    print(f"Model {model_class_name} loaded for {ticker}. Using {len(model_features)} features.")

    # 6. Predict probability
    proba = model_instance.predict_proba(X_predict)[0] # Get probability for the positive class

    # 7. Generate signal
    signal = "BUY" if proba >= buy_threshold else "HOLD/SELL"

    print("\n" + "="*50)
    print(f"           PREDICTION FOR {ticker}")
    print("="*50)
    print(f"Date de la prédiction: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    print(f"Probabilité de hausse (classe 1): {proba:.4f}")
    print(f"Seuil d'achat optimisé: {buy_threshold:.4f}")
    print(f"Signal: {signal}")
    print("="*50)

    return {
        "ticker": ticker,
        "prediction_date": datetime.now().isoformat(),
        "probability_up": float(proba),
        "buy_threshold": float(buy_threshold),
        "signal": signal
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict next day's price movement for a given stock ticker.")
    parser.add_argument(
        '--ticker',
        type=str,
        required=True,
        help="The stock ticker symbol (e.g., 'AAPL', 'AIR.PA')."
    )
    args = parser.parse_args()

    predict_next_day(ticker=args.ticker.upper())