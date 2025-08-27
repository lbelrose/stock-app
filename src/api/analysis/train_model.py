import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# --- Feature Generation (Simplified from Alphon) ---

def generate_technical_indicators(df: pd.DataFrame, price_col: str = 'Close', volume_col: str = 'Volume') -> pd.DataFrame:
    """
    Generates a set of common technical indicators for classification.
    """
    ti_df = df.copy()

    # Ensure numeric types
    for col in [price_col, volume_col]:
        if col in ti_df.columns:
            ti_df[col] = pd.to_numeric(ti_df[col], errors='coerce')

    # Simple Moving Averages
    ti_df['sma_10'] = ti_df[price_col].rolling(window=10).mean()
    ti_df['sma_50'] = ti_df[price_col].rolling(window=50).mean()

    # Exponential Moving Averages
    ti_df['ema_10'] = ti_df[price_col].ewm(span=10, adjust=False).mean()
    ti_df['ema_20'] = ti_df[price_col].ewm(span=20, adjust=False).mean()

    # RSI
    delta = ti_df[price_col].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, 1e-10)  # Avoid division by zero
    ti_df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = ti_df[price_col].ewm(span=12, adjust=False).mean()
    exp2 = ti_df[price_col].ewm(span=26, adjust=False).mean()
    ti_df['macd'] = exp1 - exp2
    ti_df['macd_signal'] = ti_df['macd'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    ti_df['bollinger_mid'] = ti_df[price_col].rolling(window=20).mean()
    ti_df['bollinger_std'] = ti_df[price_col].rolling(window=20).std()
    ti_df['bollinger_upper'] = ti_df['bollinger_mid'] + (ti_df['bollinger_std'] * 2)
    ti_df['bollinger_lower'] = ti_df['bollinger_mid'] - (ti_df['bollinger_std'] * 2)

    # Volatility
    ti_df['volatility_20d'] = ti_df[price_col].pct_change().rolling(window=20).std()

    return ti_df


def train_model():
    """
    Main function to train and save the Random Forest classifier.
    Predicts whether the next day's close is higher (1) or lower (0).
    """
    print("🚀 Starting model training...")

    # 1. Data Acquisition
    ticker = "AAPL"
    print(f"📊 Fetching data for {ticker}...")
    aapl_ticker = yf.Ticker(ticker)
    data = aapl_ticker.history(start="2015-01-01", end="2024-12-31")

    if data.empty:
        print(f"❌ No data found for {ticker}. Exiting.")
        return

    # 2. Feature Engineering
    print("🔧 Generating technical indicators...")
    features_df = generate_technical_indicators(data)

    # 3. Target: Binary (1 = price goes up tomorrow, 0 = down or flat)
    features_df['target'] = (features_df['Close'].shift(-1) > features_df['Close']).astype(int)

    # 4. Data Cleaning
    features_df = features_df.dropna()
    if features_df.empty:
        print("❌ Not enough data after feature generation.")
        return

    # 5. Define Features and Target
    features_to_exclude = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'target']
    feature_columns = [col for col in features_df.columns if col not in features_to_exclude]
    X = features_df[feature_columns]
    y = features_df['target']

    print(f"Features: {list(X.columns)}")
    print(f"Dataset size: {len(X)} samples, {X.shape[1]} features")

    # 6. TimeSeriesSplit for Evaluation
    tscv = TimeSeriesSplit(n_splits=5)
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

    # Train on full data
    model.fit(X, y)

    # Evaluate on last split
    print("Evaluating on last time-series split...")
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=["Down (0)", "Up (1)"])
    cm = confusion_matrix(y_test, y_pred)

    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:\n", report)
    print("Confusion Matrix:\n", cm)

    # 7. Save Model + Features
    output_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, 'random_forest_classifier.joblib')
    model_payload = {
        'model': model,
        'features': list(X.columns),  # Important: feature order and names
        'model_type': 'classifier',
        'target': 'next_day_price_increase'
    }

    joblib.dump(model_payload, model_path)
    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    train_model()