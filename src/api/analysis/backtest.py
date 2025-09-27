# src/api/analysis/backtest.py
import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import argparse

from .features import generate_technical_features
from .models.base_model import BaseModel


def run_backtest(
    ticker="AAPL",
    start_date="2000-01-01",
    end_date="2025-06-30",
    model_name="model_general.joblib",
    buy_threshold=None,
    precomputed_features=None
):
    """
    Backtest complet avec métriques stratégiques et Buy & Hold.
    Si precomputed_features est fourni, on l'utilise pour tous les seuils.
    """
    data = yf.Ticker(ticker).history(start=start_date, end=end_date)
    if data.empty:
        print(f"No data for {ticker}")
        return None
    data = data.sort_index()

    # Features
    if precomputed_features is not None:
        feature_df = precomputed_features
    else:
        feature_df = generate_technical_features(data)

    # Load model
    model_ticker = model_name.replace(".joblib", "").split("_")[-1].upper()
    model_instance = BaseModel.load(model_ticker, directory=os.path.join(os.path.dirname(__file__), "models"))
    if model_instance.model is None:
        print(f"Model for {ticker} is not trained.")
        return None

    feature_names = model_instance.features

    # Dataset preparation
    lagged_features = feature_df.shift(1)
    target = (data["Close"].shift(-1) > data["Close"]).astype(int)
    next_returns = data["Close"].shift(-1) / data["Close"] - 1

    model_data = lagged_features.copy()
    model_data["target"] = target
    model_data["next_return"] = next_returns
    model_data = model_data.dropna()
    if model_data.empty:
        print("Not enough data after processing.")
        return None

    X = model_data[feature_names]
    y_true = model_data["target"]
    next_returns = model_data["next_return"]

    # Predict probabilities
    proba = model_instance.predict_proba(X)
    if buy_threshold is not None:
        signals = (proba >= buy_threshold)
    else:
        signals = pd.Series(True, index=X.index)

    if signals.sum() == 0:
        print("No BUY signals generated with current threshold.")
        return None

    trade_returns = next_returns[signals]

    # Performance metrics
    win_rate = (trade_returns > 0).mean()
    avg_return_per_trade = trade_returns.mean()
    std_return = trade_returns.std()
    profit_factor = trade_returns[trade_returns > 0].sum() / (abs(trade_returns[trade_returns < 0].sum()) + 1e-8)
    total_return = (1 + trade_returns).prod() - 1
    annualized_return = (1 + total_return) ** (252 / len(trade_returns)) - 1 if len(trade_returns) > 0 else 0
    directional_accuracy = (y_true[signals] == 1).mean()
    cumulative_returns = (1 + trade_returns).cumprod()
    peak = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    sharpe_ratio = (avg_return_per_trade / std_return) if std_return > 0 else 0

    # Buy & Hold
    bh_returns = data["Close"].pct_change().dropna()
    bh_total_return = (1 + bh_returns).prod() - 1
    bh_win_rate = (bh_returns > 0).mean()
    bh_avg_return = bh_returns.mean()

    results = {
        "ticker": ticker,
        "threshold": buy_threshold,
        "signals_count": int(len(trade_returns)),
        "win_rate": float(win_rate),
        "avg_return": float(avg_return_per_trade),
        "profit_factor": float(profit_factor),
        "cumulative_return": float(total_return),
        "annualized_return": float(annualized_return),
        "directional_accuracy": float(directional_accuracy),
        "max_drawdown": float(max_drawdown),
        "sharpe_ratio": float(sharpe_ratio),
        "buy_and_hold_return": float(bh_total_return),
        "buy_and_hold_win_rate": float(bh_win_rate),
        "buy_and_hold_avg_return": float(bh_avg_return),
        "timestamp": datetime.now().isoformat()
    }

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run backtest for a given stock and model.")
    parser.add_argument("--ticker", type=str, required=True, help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--start_date", type=str, default="2015-01-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end_date", type=str, default="2025-06-30", help="End date YYYY-MM-DD")
    parser.add_argument("--buy_threshold", type=float, default=None, help="Buy threshold (0-1)")
    parser.add_argument("--model_name", type=str, required=True, help="Model filename (joblib)")

    args = parser.parse_args()

    results = run_backtest(
        ticker=args.ticker,
        start_date=args.start_date,
        end_date=args.end_date,
        model_name=args.model_name,
        buy_threshold=args.buy_threshold
    )

    if results is not None:
        print("\nBacktest Results:")
        for k, v in results.items():
            print(f"{k}: {v}")

