# src/api/analysis/optimize_thresholds_fast.py
import os
import json
import numpy as np
import yfinance as yf

from .backtest import run_backtest
from .features import generate_technical_features
from .models.base_model import BaseModel


def optimize_thresholds_fast(
    ticker_arg=None,
    model_dir="src/api/analysis/models",
    output_file="src/api/analysis/optimized_thresholds.json",
    threshold_range=None,
    start_date="2000-01-01",
    end_date="2025-01-01"
):
    if threshold_range is None:
        threshold_range = np.arange(0.50, 0.66, 0.01)

    # Lister fichiers modèles
    if ticker_arg:
        model_files = [f for f in os.listdir(model_dir)
                       if ticker_arg.lower() in f.lower() and f.endswith(".joblib")]
        if not model_files:
            print(f"Model file for ticker {ticker_arg} not found.")
            return
    else:
        model_files = [f for f in os.listdir(model_dir) if f.endswith(".joblib")]

    # Charger thresholds existants
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            optimized_thresholds = json.load(f)
    else:
        optimized_thresholds = {}

    for model_file in model_files:
        ticker = model_file.split("_")[-1].replace(".joblib", "").upper()
        print(f"\nOptimizing thresholds for {ticker} using model {model_file}...")

        # Pré-calcul des données et features
        data = yf.Ticker(ticker).history(start=start_date, end=end_date)
        if data.empty:
            print(f"No data for {ticker}")
            continue
        data = data.sort_index()
        feature_df = generate_technical_features(data)

        # Charger modèle
        model_instance = BaseModel.load(filename=model_file, directory=model_dir)
        X = feature_df.shift(1).dropna()[model_instance.features]
        y_true = (data["Close"].shift(-1) > data["Close"]).astype(int).reindex(X.index)
        next_returns = (data["Close"].shift(-1) / data["Close"] - 1).reindex(X.index)

        # Prédiction unique
        proba = model_instance.model.predict_proba(X)

        best_threshold = None
        max_cum_return = -np.inf

        # Évaluer tous les thresholds vectorisés
        for threshold in threshold_range:
            signals = (proba >= threshold)
            trade_returns = next_returns[signals]

            if trade_returns.empty:
                continue

            cum_return = (1 + trade_returns).prod() - 1

            if cum_return > max_cum_return:
                max_cum_return = cum_return
                best_threshold = threshold

        if best_threshold is not None:
            optimized_thresholds[ticker] = {
                "model_name": model_file,
                "optimal_buy_threshold": float(f"{best_threshold:.2f}"),
                "max_cumulative_return_percent": float(f"{max_cum_return*100:.2f}")
            }
            print(f"Optimal threshold for {ticker}: {best_threshold:.2f} "
                  f"(Return: {max_cum_return*100:,.2f}%)")
        else:
            print(f"No valid threshold found for {ticker}")

    # Sauvegarde JSON
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(optimized_thresholds, f, indent=4)
    print(f"\nOptimized thresholds saved to {output_file}")


if __name__ == "__main__":
    optimize_thresholds_fast()
