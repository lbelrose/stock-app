# src/api/analysis/optimize_threshold.py
import os
import numpy as np

from .models.base_model import BaseModel
from .backtest import run_backtest


def optimize_thresholds(model_dir="src/api/analysis/models", tickers: list = None):
    """
    Optimise le seuil d'achat pour chaque modèle en testant différents thresholds
    et en sauvegardant directement le seuil optimal dans le payload du modèle.
    
    :param model_dir: dossier contenant les modèles .joblib
    :param tickers: liste optionnelle de tickers à traiter
    """
    # Liste tous les modèles disponibles
    models = BaseModel.list_saved_models(directory=model_dir)

    if not models:
        print("No models found for threshold optimization.")
        return

    # Filtrer par tickers si fourni
    if tickers:
        models = [m for m in models if m[2] in tickers]

    threshold_range = np.arange(0.50, 0.66, 0.01)

    for filename, model_class, ticker in models:
        print(f"\nOptimizing threshold for {ticker} ({model_class})...")
        model_path = os.path.join(model_dir, filename)

        best_threshold = None
        max_cum_return = -np.inf

        for threshold in threshold_range:
            try:
                result = run_backtest(
                    ticker=ticker,
                    buy_threshold=threshold,
                    model_name=filename
                )
                if not result:
                    continue
                cum_return = result.get("cumulative_return", 0.0) * 100
                if cum_return > max_cum_return:
                    max_cum_return = cum_return
                    best_threshold = threshold
            except Exception as e:
                print(f"  Threshold {threshold:.2f} failed: {e}")
                continue

        if best_threshold is not None:
            # Charger le payload existant
            payload = BaseModel.load(ticker, directory=model_dir)
            payload["optimal_buy_threshold"] = float(f"{best_threshold:.2f}")

            # Réécrire le modèle avec le nouveau seuil
            from joblib import dump
            dump(payload, model_path)

            # Formate le retour cumulé pour affichage
            cum_return_formatted = f"{cum_return:,.2f}%"
            print(f"Optimal threshold for {ticker}: {threshold:,.2f} (Cumulative return: {cum_return_formatted})")
        else:
            print(f"No valid threshold found for {ticker}")


if __name__ == "__main__":
    optimize_thresholds()
