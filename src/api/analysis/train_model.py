import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def generate_technical_indicators(df: pd.DataFrame, price_col: str = 'Close', volume_col: str = 'Volume') -> pd.DataFrame:
    """
    Generates technical indicators using historical data.
    """
    ti_df = df.copy()

    for col in [price_col, volume_col]:
        ti_df[col] = pd.to_numeric(ti_df[col], errors='coerce')

    ti_df['sma_10'] = ti_df[price_col].rolling(window=10).mean()
    ti_df['sma_50'] = ti_df[price_col].rolling(window=50).mean()

    ti_df['ema_10'] = ti_df[price_col].ewm(span=10, adjust=False).mean()
    ti_df['ema_20'] = ti_df[price_col].ewm(span=20, adjust=False).mean()

    delta = ti_df[price_col].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, 1e-10)
    ti_df['rsi'] = 100 - (100 / (1 + rs))

    exp1 = ti_df[price_col].ewm(span=12, adjust=False).mean()
    exp2 = ti_df[price_col].ewm(span=26, adjust=False).mean()
    ti_df['macd'] = exp1 - exp2
    ti_df['macd_signal'] = ti_df['macd'].ewm(span=9, adjust=False).mean()

    ti_df['bollinger_mid'] = ti_df[price_col].rolling(window=20).mean()
    ti_df['bollinger_std'] = ti_df[price_col].rolling(window=20).std()
    ti_df['bollinger_upper'] = ti_df['bollinger_mid'] + (ti_df['bollinger_std'] * 2)
    ti_df['bollinger_lower'] = ti_df['bollinger_mid'] - (ti_df['bollinger_std'] * 2)

    ti_df['volatility_20d'] = ti_df[price_col].pct_change().rolling(window=20).std()

    return ti_df


def train_model():
    """
    Trains a Random Forest classifier to predict if the next day's close price will be higher.
    Uses lagged features to prevent data leakage.
    """
    print("Starting model training...")

    ticker = "AAPL"
    print(f"Fetching data for {ticker}...")
    aapl_ticker = yf.Ticker(ticker)
    data = aapl_ticker.history(start="2015-01-01", end="2024-12-31")

    if data.empty:
        print(f"No data found for {ticker}. Exiting.")
        return

    # Ensure chronological order
    data = data.sort_index(ascending=True)

    print(f"Data covers {data.index[0]} to {data.index[-1]}")

    # Generate features
    raw_features = generate_technical_indicators(data)

    # Target: 1 if tomorrow's close > today's close
    target = (data['Close'].shift(-1) > data['Close']).astype(int)

    # Lag features by one day to prevent leakage
    lagged_features = raw_features.shift(1)
    model_df = lagged_features.copy()
    model_df['target'] = target

    # Clean
    model_df = model_df.dropna()
    if model_df.empty:
        print("No data available after feature generation and lagging.")
        return

    # Define features
    features_to_exclude = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'target']
    feature_columns = [col for col in model_df.columns if col not in features_to_exclude]
    X = model_df[feature_columns]
    y = model_df['target']

    print(f"Features used: {list(X.columns)}")
    print(f"Dataset size: {len(X)} samples")

    # Validate index order
    if not X.index.equals(y.index):
        raise ValueError("Feature and target indices do not match.")
    if not X.index.is_monotonic_increasing:
        raise ValueError("Index is not sorted in ascending order.")

    # Model training with proper train/test split
    tscv = TimeSeriesSplit(n_splits=5)
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

    print("Performing time-series cross-validation...")
    for fold, (train_index, test_index) in enumerate(tscv.split(X)):
        if fold == tscv.n_splits - 1:  # Only use the last split for final evaluation
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            break

    print(f"Training size: {len(X_train)}, Test size: {len(X_test)}")

    # Fit only on training data
    model.fit(X_train, y_train)

    # Predict on test data
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Down (0)", "Up (1)"])
    cm = confusion_matrix(y_test, y_pred)

    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(report)
    print("Confusion Matrix:")
    print(cm)

    # Save model
    output_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, 'random_forest_classifier.joblib')
    model_payload = {
        'model': model,
        'features': list(X.columns),
        'lagged': True
    }

    joblib.dump(model_payload, model_path)
    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    train_model()