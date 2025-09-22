import pandas as pd
import numpy as np
import yfinance as yf
import os
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import argparse

from features import generate_technical_features
from models.model_factory import ModelFactory

def train_model(ticker: str, model_class_name: str = "RandomForestModel", **model_kwargs):
    """
    Trains a classifier for a specific ticker using the modular architecture.
    """
    print(f"Starting training for {ticker} with model {model_class_name}...")

    # 1. Fetch data
    data = yf.Ticker(ticker).history(start="2015-01-01", end="2024-12-31")
    if data.empty:
        raise ValueError(f"No data found for {ticker}")
    data = data.sort_index(ascending=True)

    # 2. Generate features
    print("Generating features...")
    raw_features = generate_technical_features(data)

    # Target: 1 if tomorrow's close > today's close (good day to have bought)
    target = (data['Close'].shift(-1) > data['Close']).astype(int)

    # Lag features by one day (no leakage)
    lagged_features = raw_features.shift(1)
    model_df = lagged_features.copy()
    model_df['target'] = target
    model_df = model_df.dropna()

    if model_df.empty:
        print("Not enough data after processing.")
        return

    # Select only the 12 most interpretable and relevant features
    selected_features = [
        'return_lag_1',
        'return_lag_2',
        'return_lag_3',
        'volume_ratio_lag_1',
        'volume_ratio_lag_2',
        'volume_lag_1',
        'volume_lag_2',
        'close_sma10_ratio',
        'volatility_20',
        'rsi_lag_1',
        'return_1d',  # lagged via shift(1), so this is yesterday's return
        'return_5d'   # lagged
    ]

    # Safety check
    missing = [f for f in selected_features if f not in model_df.columns]
    if missing:
        print(f"Error: Missing features: {missing}")
        return

    X = model_df[selected_features]
    y = model_df['target']

    print(f"Using {len(X.columns)} features: {list(X.columns)}")
    print(f"Dataset size: {len(X)} samples")

    # Validate index
    if not X.index.equals(y.index):
        raise ValueError("Feature and target indices do not match.")
    if not X.index.is_monotonic_increasing:
        raise ValueError("Index is not sorted in ascending order.")

    # TimeSeriesSplit: use last split for evaluation
    tscv = TimeSeriesSplit(n_splits=5)
    X_train, X_test, y_train, y_test = None, None, None, None

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    print(f"Training size: {len(X_train)}, Test size: {len(X_test)}")

    # 3. Create and train model
    model_instance = ModelFactory.create_model(model_class_name, ticker, selected_features, **model_kwargs)
    model_instance.train(X_train, y_train)

    # 4. Evaluate model (using the internal sklearn model for metrics)
    y_pred = model_instance.model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Down (0)", "Up (1)"])
    cm = confusion_matrix(y_test, y_pred)

    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(report)
    print("Confusion Matrix:")
    print(cm)

    # Feature importance
    if hasattr(model_instance.model, 'feature_importances_'):
        importances = model_instance.model.feature_importances_
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': importances
        }).sort_values('importance', ascending=False)

        print("\nFeature Importance:")
        print(importance_df)

    # 5. Save model
    model_instance.save(directory=os.path.join(os.path.dirname(__file__), 'models'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a buy signal classifier for a specific stock ticker.")
    parser.add_argument(
        '--ticker',
        type=str,
        required=True,
        help="The stock ticker symbol to train the model on (e.g., 'AAPL', 'MSFT')."
    )
    parser.add_argument(
        '--model_class',
        type=str,
        default="RandomForestModel",
        help="The class name of the model to train (e.g., 'RandomForestModel')."
    )
    args = parser.parse_args()

    ticker = args.ticker.upper()
    train_model(ticker=ticker, model_class_name=args.model_class)