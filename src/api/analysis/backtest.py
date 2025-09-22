import pandas as pd
import numpy as np
import yfinance as yf
import os
from datetime import datetime
import argparse

from features import generate_technical_features
from models.base_model import BaseModel
from models.model_factory import ModelFactory

def run_backtest(ticker="AAPL", start_date="2015-01-01", end_date="2024-12-31", buy_threshold=0.55, model_name="buy_signal_classifier_general.joblib"):
    """
    Runs a backtest on historical data using the trained model.
    Simulates buying at close when signal is strong, selling next day.
    """
    print(f"Starting backtest for {ticker} with model {model_name}...")

    # 1. Fetch data
    data = yf.Ticker(ticker).history(start=start_date, end=end_date)
    if data.empty:
        raise ValueError(f"No data for {ticker}")

    data = data.sort_index(ascending=True)

    # 2. Generate features
    print("Generating features...")
    feature_df = generate_technical_features(data)

    # 3. Load model using the new modular architecture
    # We need to extract the ticker from model_name to load it correctly
    # Assuming model_name format is 'buy_signal_classifier_{ticker}.joblib'
    model_ticker = model_name.replace('buy_signal_classifier_', '').replace('.joblib', '').upper()
    
    # Load the payload (which contains model_class_name, model, features)
    payload = BaseModel.load(model_ticker, directory=os.path.join(os.path.dirname(__file__), 'models'))
    
    # Re-instantiate the specific model class using ModelFactory
    model_instance = ModelFactory.create_model(payload['model_class'], payload['ticker'], payload['features'])
    model_instance.model = payload['model'] # Assign the loaded sklearn model to the instance
    
    feature_names = payload['features']
    print(f"Model loaded. Using {len(feature_names)} features.")

    # 4. Prepare dataset with lag (no future data)
    lagged_features = feature_df.shift(1)  # Predict using J-1 to act at J
    target = (data['Close'].shift(-1) > data['Close']).astype(int)  # 1 if tomorrow > today
    returns_next = data['Close'].pct_change().shift(-1)  # Return from J to J+1

    # Combine
    model_data = lagged_features.copy()
    model_data['target'] = target
    model_data['next_return'] = returns_next
    model_data = model_data.dropna()

    if model_data.empty:
        print("Not enough data after processing.")
        return

    X = model_data[feature_names]
    y_true = model_data['target']
    next_returns = model_data['next_return']

    # 5. Predict probabilities using the model instance
    proba = model_instance.predict_proba(X)  # Probability of "Up"
    signals = (proba >= buy_threshold)

    # 6. Extract trades
    trade_returns = next_returns[signals]
    trade_dates = X.index[signals]

    if len(trade_returns) == 0:
        print("No BUY signals generated with current threshold.")
        return

    # 7. Performance metrics
    win_rate = (trade_returns > 0).mean()
    avg_return_per_trade = trade_returns.mean()
    std_return = trade_returns.std()
    profit_factor = trade_returns[trade_returns > 0].sum() / abs(trade_returns[trade_returns < 0].sum() + 1e-8)
    total_return = (1 + trade_returns).prod() - 1  # Cumulative return
    annualized_return = (1 + total_return) ** (252 / len(trade_returns)) - 1  # Rough annualization

    # Directional Accuracy (for days with BUY signals)
    directional_accuracy = (y_true[signals] == 1).mean() if len(trade_returns) > 0 else 0

    # Max Drawdown
    cumulative_returns = (1 + trade_returns).cumprod()
    if not cumulative_returns.empty:
        peak = cumulative_returns.expanding(min_periods=1).max()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min()
    else:
        max_drawdown = 0.0

    # Sharpe Ratio (assuming risk-free rate = 0 for simplicity)
    risk_free_rate = 0
    if std_return > 0:
        sharpe_ratio = (avg_return_per_trade - risk_free_rate) / std_return
    else:
        sharpe_ratio = 0.0 # Or np.nan, depending on desired behavior

    # 8. Buy & Hold comparison
    bh_returns = next_returns  # Daily buy & hold
    bh_win_rate = (bh_returns > 0).mean()
    bh_avg_return = bh_returns.mean()
    bh_total_return = (1 + bh_returns).prod() - 1

    # 9. Report
    print("\n" + "="*50)
    print("           BACKTEST RESULTS")
    print("="*50)
    print(f"Ticker: {ticker}")
    print(f"Period: {data.index[0].date()} to {data.index[-1].date()}")
    print(f"Threshold: {buy_threshold}")
    print(f"Total BUY signals: {len(trade_returns)}")
    print(f"Win Rate: {win_rate:.2%}")
    print(f"Avg Return per Trade: {avg_return_per_trade:.4f} ({avg_return_per_trade*100:.2f}%)")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Cumulative Return (strategy): {total_return:.4f} ({total_return*100:.2f}%)")
    print(f"Annualized Return: {annualized_return*100:.2f}%")
    print(f"Directional Accuracy (on signals): {directional_accuracy:.2%}")
    print(f"Max Drawdown: {max_drawdown:.2%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print("-" * 50)
    print(f"Buy & Hold - Win Rate: {bh_win_rate:.2%}")
    print(f"Buy & Hold - Avg Return: {bh_avg_return:.4f}")
    print(f"Buy & Hold - Total Return: {bh_total_return*100:.2f}%")
    print("="*50)

    # Optional: Save results
    results = {
        "ticker": ticker,
        "start_date": str(data.index[0].date()),
        "end_date": str(data.index[-1].date()),
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
        "timestamp": datetime.now().isoformat()
    }

    # Save to JSON or CSV (optional)
    results_df = pd.DataFrame([results])
    results_dir = os.path.join(os.path.dirname(__file__), 'backtest_results')
    os.makedirs(results_dir, exist_ok=True)
    results_df.to_csv(os.path.join(results_dir, f'backtest_{ticker}_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'), index=False)

    print(f"Backtest completed and saved.")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run backtest for a given stock and model.")
    parser.add_argument("--ticker", type=str, default="AAPL", help="Stock ticker symbol (e.g., AAPL, AIR.PA)")
    parser.add_argument("--start_date", type=str, default="2015-01-02", help="Start date for backtest (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2024-12-30", help="End date for backtest (YYYY-MM-DD)")
    parser.add_argument("--buy_threshold", type=float, default=0.55, help="Probability threshold for generating a BUY signal")
    parser.add_argument("--model_name", type=str, default="buy_signal_classifier_general.joblib", help="Name of the model file to use (e.g., buy_signal_classifier_general.joblib)")

    args = parser.parse_args()

    print(f"--- Backtesting with model {args.model_name} on {args.ticker} ---")
    run_backtest(ticker=args.ticker, start_date=args.start_date, end_date=args.end_date, buy_threshold=args.buy_threshold, model_name=args.model_name)


