# src/api/analysis/evaluate_performance.py
import os
import sys
import pandas as pd
from datetime import datetime

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath('src'))

from api.analysis.models.base_model import BaseModel
from api.analysis.backtest import run_backtest

def analyze_all_performances(start_date="2025-01-01", end_date=None):
    """
    Runs backtests for all saved models using their optimized thresholds stored in payload.
    Displays a summary of performance metrics.
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    model_dir = "src/api/analysis/models"
    models = BaseModel.list_saved_models(directory=model_dir)

    if not models:
        print("No models found for performance evaluation.")
        return

    results = []

    print(f"--- Running Backtests from {start_date} to {end_date} ---")
    for filename, model_class, ticker in models:
        model_path = os.path.join(model_dir, filename)
        try:
            model_instance = BaseModel.load(ticker, directory=model_dir, filename=filename)
            optimal_threshold = model_instance.optimal_buy_threshold if model_instance.optimal_buy_threshold is not None else 0.55
        except FileNotFoundError:
            print(f"Model file not found for {ticker}. Skipping.")
            continue

        print(f"\nRunning backtest for {ticker} ({model_class}) with threshold {optimal_threshold:.2f}...")
        try:
            result = run_backtest(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                buy_threshold=optimal_threshold,
                model_name=filename
            )
            if result:
                results.append({
                    "Ticker": ticker,
                    "Model": model_class,
                    "Threshold": optimal_threshold,
                    "Return (%)": result.get("cumulative_return", 0.0) * 100,
                    "Return B&H (%)": result.get("buy_and_hold_return", 0.0) * 100,
                    "Max Drawdown (%)": result.get("max_drawdown", 0.0) * 100,
                    "Win Rate (%)": result.get("win_rate", 0.0) * 100,
                    "Trades": result.get("signals_count", 0)
                })
        except Exception as e:
            print(f"Failed backtest for {ticker}: {e}")

    if not results:
        print("No results to display.")
        return

    df = pd.DataFrame(results)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    print("\n--- Performance Summary ---")
    print(df.to_string(index=False))


if __name__ == "__main__":
    analyze_all_performances()
