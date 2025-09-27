# src/api/analysis/train_model.py
import pandas as pd
import numpy as np
import yfinance as yf
import os
import argparse
from pathlib import Path

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score

from .features import generate_technical_features
from .models.model_factory import ModelFactory


def train_model(ticker: str, model_class_name: str = "RandomForestModel", optimize_threshold=True, **model_kwargs):
    print(f"Starting training for {ticker} with model {model_class_name}...")

    # 1. Récupérer les données
    data = yf.Ticker(ticker).history(start="2000-01-01", end="2025-01-01")
    if data.empty:
        raise ValueError(f"No data found for {ticker}")
    data = data.sort_index()

    # 2. Features
    features_df = generate_technical_features(data)
    target = (data['Close'].shift(-1) > data['Close']).astype(int)
    X = features_df.shift(1).dropna()
    y = target.reindex(X.index)

    selected_features = [
        'return_lag_1','return_lag_2','return_lag_3',
        'volume_ratio_lag_1','volume_ratio_lag_2','volume_lag_1','volume_lag_2',
        'close_sma10_ratio','volatility_20','rsi_lag_1','return_1d','return_5d'
    ]
    X = X[[f for f in selected_features if f in X.columns]]

    # 3. Cross-validation (TimeSeriesSplit)
    tscv = TimeSeriesSplit(n_splits=5)
    accuracies = []

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model_instance = ModelFactory.create_model(model_class_name, ticker, list(X.columns), **model_kwargs)
        model_instance.train(X_train, y_train)

        if len(np.unique(y_test)) < 2:
            continue

        y_pred = model_instance.model.predict(X_test)
        accuracies.append(accuracy_score(y_test, y_pred))

    if accuracies:
        print(f"Average CV Accuracy: {np.mean(accuracies):.4f}")
    else:
        print("CV Skipped")

    # 4. Entraînement final et optimisation
    # Entraînement sur les n-1 premiers folds
    train_indices = np.concatenate([idx for i, (idx, _) in enumerate(tscv.split(X)) if i < tscv.n_splits - 1])
    X_train_final, y_train_final = X.iloc[train_indices], y.iloc[train_indices]
    
    model_instance = ModelFactory.create_model(model_class_name, ticker, list(X.columns), **model_kwargs)
    model_instance.train(X_train_final, y_train_final)

    # Optimisation sur le dernier fold (out-of-sample)
    _, test_indices = list(tscv.split(X))[-1]
    X_opt, y_opt = X.iloc[test_indices], y.iloc[test_indices]
    
    print("\n--- Threshold optimization on the last fold ---")
    returns_next_opt = (data["Close"].shift(-1) / data["Close"] - 1).reindex(X_opt.index).fillna(0)
    proba_opt = model_instance.predict_proba(X_opt)

    best_threshold = 0.5
    max_cum_return = -np.inf

    for th in np.arange(0.50, 0.66, 0.01):
        signals = proba_opt >= th
        trade_returns = returns_next_opt[signals]
        if not trade_returns.empty:
            cum_return = (1 + trade_returns).prod() - 1
            if cum_return > max_cum_return:
                max_cum_return = cum_return
                best_threshold = th
    
    model_instance.optimal_buy_threshold = best_threshold
    print(f"Optimal threshold found: {best_threshold:.2f} with cumulative return: {max_cum_return*100:.2f}%")

    # 5. Sauvegarde
    save_dir = Path(__file__).parent / 'models'
    save_dir.mkdir(parents=True, exist_ok=True)
    model_instance.save(directory=save_dir)
    print(f"Training and threshold optimization completed for {ticker}.")
    return model_instance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a buy signal classifier for a specific stock ticker.")
    parser.add_argument('--ticker', type=str, required=True, help="The stock ticker symbol (e.g., 'AAPL').")
    parser.add_argument('--model_class', type=str, default="RandomForestModel", help="The model class name.")
    
    args, unknown = parser.parse_known_args()
    model_kwargs = {}
    for i in range(0, len(unknown), 2):
        key = unknown[i].lstrip('--')
        value = unknown[i+1]
        try:
            model_kwargs[key] = int(value)
        except ValueError:
            try:
                model_kwargs[key] = float(value)
            except ValueError:
                model_kwargs[key] = value

    ticker = args.ticker.upper()
    train_model(ticker=ticker, model_class_name=args.model_class, **model_kwargs)


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
    
    # Parse known arguments, and collect the rest as model_kwargs
    args, unknown = parser.parse_known_args()

    model_kwargs = {}
    # Convert unknown arguments (e.g., --n_estimators 100) into a dictionary
    for i in range(0, len(unknown), 2):
        key = unknown[i].lstrip('--')
        value = unknown[i+1]
        # Attempt to convert to int or float if possible
        try:
            model_kwargs[key] = int(value)
        except ValueError:
            try:
                model_kwargs[key] = float(value)
            except ValueError:
                model_kwargs[key] = value

    ticker = args.ticker.upper()
    train_model(ticker=ticker, model_class_name=args.model_class, **model_kwargs)