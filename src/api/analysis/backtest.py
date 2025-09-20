import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.model_selection import TimeSeriesSplit
import joblib
import os
from datetime import datetime


def load_model_and_features(model_name="buy_signal_classifier_general.joblib"):
    """
    Loads a specified trained model and its feature list.
    """
    model_path = os.path.join(os.path.dirname(__file__), 'models', model_name)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Run train_model.py first.")

    payload = joblib.load(model_path)
    return payload['model'], payload['features']


def generate_features_for_backtest(df):
    """
    Generates the same 12 features as in training and services.
    """
    close = df['Close']
    volume = df['Volume']

    # Initialize DataFrame
    feats = pd.DataFrame(index=df.index)

    # 1. Returns
    feats['return_1d'] = close.pct_change(1)
    feats['return_5d'] = close.pct_change(5)

    for lag in [1, 2, 3]:
        feats[f'return_lag_{lag}'] = feats['return_1d'].shift(lag)

    # 2. Volume
    feats['volume_sma_20'] = volume.rolling(20).mean()
    feats['volume_ratio'] = volume / feats['volume_sma_20'].replace(0, 1e-10)
    feats['volume_lag_1'] = volume.shift(1)
    feats['volume_lag_2'] = volume.shift(2)
    feats['volume_ratio_lag_1'] = feats['volume_lag_1'] / feats['volume_sma_20'].replace(0, 1e-10)
    feats['volume_ratio_lag_2'] = feats['volume_lag_2'] / feats['volume_sma_20'].replace(0, 1e-10)

    # 3. Trend
    sma_10 = close.rolling(10).mean()
    feats['close_sma10_ratio'] = close / sma_10.replace(0, 1e-10)

    # 4. Volatility
    feats['volatility_20'] = feats['return_1d'].rolling(20).std()

    # 5. RSI
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    feats['rsi_lag_1'] = rsi.shift(1)

    return feats


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
    feature_df = generate_features_for_backtest(data)

    # 3. Load model
    model, feature_names = load_model_and_features(model_name)
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

    # 5. Predict probabilities
    proba = model.predict_proba(X)[:, 1]  # Probability of "Up"
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
    # Backtest the specialized Airbus model on AIR.PA
    print("--- Backtesting Specialized Model on AIR.PA ---")
    run_backtest(ticker="AIR.PA", buy_threshold=0.52, model_name="buy_signal_classifier_airbus.joblib")

