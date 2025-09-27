# src/api/analysis/optimize_thresholds_vectorized.py
import os
import json
import numpy as np
import yfinance as yf

from .features import generate_technical_features
from .models.base_model import BaseModel


def optimize_thresholds_vectorized(
    ticker_arg=None,
    model_dir="src/api/analysis/models",
    output_file="src/api/analysis/optimized_thresholds.json",
    threshold_range=None,
    start_date="2000-01-01",
    end_date="2025-01-01"
):
    if threshold_range is None:
        threshold_range = np.arange(0.50, 0.66, 0.01)

    # Lister les fichiers modèles
    if ticker_arg:
        model_files = [f for f in os.listdir(model_dir)
                       if ticker_arg.lower() in f.lower() and f.endswith(".joblib")]
        if not model_files:
            print(f"Model file for ticker {ticker_arg} not found.")
            return
    else:
        model_files = [f for f in os.listdir(model_dir) if f.endswith(".joblib")]

    # Charger JSON existant
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            optimized_thresholds = json.load(f)
    else:
        optimized_thresholds = {}

    for model_file in model_files:
        ticker = model_file.split("_")[-1].replace(".joblib", "").upper()
        print(f"\nOptimizing thresholds for {ticker} using model {model_file}...")

        # Récupérer les données
        data = yf.Ticker(ticker).history(start=start_date, end=end_date)
        if data.empty:
            print(f"No data for {ticker}")
            continue
        data = data.sort_index()

        # Features
        feature_df = generate_technical_features(data)
        X = feature_df.shift(1).dropna()
        
        # Charger modèle
        model_instance = BaseModel.load(filename=model_file, directory=model_dir)
        X_model = X[model_instance.features]
        y_true = (data["Close"].shift(-1) > data["Close"]).astype(int).reindex(X_model.index)
        next_returns = (data["Close"].shift(-1) / data["Close"] - 1).reindex(X_model.index)

        # Prédiction unique
        proba = model_instance.model.predict_proba(X_model)

        # Vectorisation complète : créer une matrice de signals (n_samples x n_thresholds)
        thresholds = np.array(threshold_range)
        signals_matrix = proba[:, None] >= thresholds[None, :]  # broadcasting

        # Calculer le retour cumulatif pour chaque threshold
        trade_returns_matrix = np.where(signals_matrix, next_returns.values[:, None], 0.0)
        cumulative_returns = np.prod(1 + trade_returns_matrix, axis=0) - 1

        # Trouver la threshold optimale
        best_idx = np.argmax(cumulative_returns)
        best_threshold = thresholds[best_idx]
        max_cum_return = cumulative_returns[best_idx]

        optimized_thresholds[ticker] = {
            "model_name": model_file,
            "optimal_buy_threshold": float(f"{best_threshold:.2f}"),
            "max_cumulative_return_percent": float(f"{max_cum_return*100:.2f}")
        }

        print(f"Optimal threshold for {ticker}: {best_threshold:.2f} "
              f"(Return: {max_cum_return*100:,.2f}%)")

    # Sauvegarder JSON
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(optimized_thresholds, f, indent=4)
    print(f"\nOptimized thresholds saved to {output_file}")


if __name__ == "__main__":
    optimize_thresholds_vectorized()
