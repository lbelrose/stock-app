import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def generate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a minimal set of robust features focused on momentum, volume, and trend.
    Designed to detect favorable days for buying.
    """
    ti_df = df.copy()
    close = ti_df['Close']
    volume = ti_df['Volume']

    # 1. Momentum & Returns
    ti_df['return_1d'] = close.pct_change(1)
    ti_df['return_5d'] = close.pct_change(5)

    # Lagged returns (predictor of continuation)
    for lag in [1, 2, 3]:
        ti_df[f'return_lag_{lag}'] = ti_df['return_1d'].shift(lag)

    # 2. Volume Analysis
    ti_df['volume_sma_20'] = volume.rolling(20).mean()
    ti_df['volume_ratio'] = volume / ti_df['volume_sma_20'].replace(0, 1e-10)
    for lag in [1, 2]:
        ti_df[f'volume_lag_{lag}'] = volume.shift(lag)
        ti_df[f'volume_ratio_lag_{lag}'] = ti_df[f'volume_lag_{lag}'] / ti_df['volume_sma_20'].replace(0, 1e-10)

    # 3. Trend & Relative Position
    ti_df['sma_10'] = close.rolling(10).mean()
    ti_df['close_sma10_ratio'] = close / ti_df['sma_10'].replace(0, 1e-10)

    # 4. Volatility
    ti_df['volatility_20'] = ti_df['return_1d'].rolling(20).std()

    # 5. RSI (momentum extremum)
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, 1e-10)
    ti_df['rsi'] = 100 - (100 / (1 + rs))
    ti_df['rsi_lag_1'] = ti_df['rsi'].shift(1)

    return ti_df


import argparse

def train_model(tickers, model_name):
    """
    Trains a classifier on a list of tickers and saves it under a specific model_name.
    """
    print(f"Starting training for model '{model_name}' with tickers: {tickers}")
    all_model_data = []

    for ticker in tickers:
        print(f"Fetching and processing data for {ticker}...")
        try:
            stock_ticker = yf.Ticker(ticker)
            data = stock_ticker.history(start="2015-01-01", end="2024-12-31")

            if data.empty:
                print(f"No data found for {ticker}. Skipping.")
                continue

            # Ensure chronological order
            data = data.sort_index(ascending=True)

            # Generate features
            raw_features = generate_technical_indicators(data)

            # Target: 1 if tomorrow's close > today's close (good day to have bought)
            target = (data['Close'].shift(-1) > data['Close']).astype(int)

            # Lag features by one day (no leakage)
            lagged_features = raw_features.shift(1)
            model_df = lagged_features.copy()
            model_df['target'] = target

            # Clean and append
            model_df = model_df.dropna()
            if not model_df.empty:
                all_model_data.append(model_df)
            else:
                print(f"No data available for {ticker} after processing.")

        except Exception as e:
            print(f"Could not process data for {ticker}: {e}")

    if not all_model_data:
        print("No data available for training after processing all tickers. Exiting.")
        return

    # Combine all dataframes
    combined_df = pd.concat(all_model_data).sort_index(ascending=True)
    print(f"Combined data from {len(tickers)} tickers, resulting in {len(combined_df)} total samples.")

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
    missing = [f for f in selected_features if f not in combined_df.columns]
    if missing:
        print(f"Error: Missing features: {missing}")
        return

    X = combined_df[selected_features]
    y = combined_df['target']

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

    # Model: focus on probability calibration and generalization
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,               # Limit depth to reduce overfitting
        min_samples_split=20,      # Require more samples to split
        min_samples_leaf=10,       # Larger leaves = smoother predictions
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Down (0)", "Up (1)"])
    cm = confusion_matrix(y_test, y_pred)

    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(report)
    print("Confusion Matrix:")
    print(cm)

    # Feature importance
    importances = model.feature_importances_
    importance_df = pd.DataFrame({
        'feature': X.columns,
        'importance': importances
    }).sort_values('importance', ascending=False)

    print("\nFeature Importance:")
    print(importance_df)

    # Save model
    output_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, model_name)
    model_payload = {
        'model': model,
        'features': selected_features,
        'target': 'next_day_price_increase',
        'lagged': True
    }

    joblib.dump(model_payload, model_path)
    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a buy signal classifier for a specific stock ticker.")
    parser.add_argument(
        '--ticker',
        type=str,
        required=True,
        help="The stock ticker symbol to train the model on (e.g., 'AAPL', 'MSFT')."
    )
    args = parser.parse_args()

    ticker = args.ticker.upper()
    model_filename = f"buy_signal_classifier_{ticker.lower().replace('.pa', '')}.joblib"
    
    train_model(tickers=[ticker], model_name=model_filename)