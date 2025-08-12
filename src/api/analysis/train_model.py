
import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score

# --- Feature Generation (Simplified from Alphon) ---

def generate_technical_indicators(df: pd.DataFrame, price_col: str = 'Close', volume_col: str = 'Volume') -> pd.DataFrame:
    """
    Generates a set of common technical indicators.
    """
    ti_df = df.copy()

    # Ensure numeric types
    for col in [price_col, volume_col]:
        if col in ti_df.columns:
            ti_df[col] = pd.to_numeric(ti_df[col], errors='coerce')

    # Simple Moving Averages (SMA)
    ti_df['sma_10'] = ti_df[price_col].rolling(window=10).mean()
    ti_df['sma_50'] = ti_df[price_col].rolling(window=50).mean()

    # Exponential Moving Averages (EMA)
    ti_df['ema_10'] = ti_df[price_col].ewm(span=10, adjust=False).mean()
    ti_df['ema_20'] = ti_df[price_col].ewm(span=20, adjust=False).mean()

    # Relative Strength Index (RSI)
    delta = ti_df[price_col].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    ti_df['rsi'] = 100 - (100 / (1 + rs))

    # Moving Average Convergence Divergence (MACD)
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

# --- Model Training ---

def train_model():
    """
    Main function to train and save the Random Forest model.
    """
    # 1. Data Acquisition
    print("Fetching data for AAPL...")
    ticker = "AAPL"
    # Explicitly create a Ticker object first
    aapl_ticker = yf.Ticker(ticker)
    data = aapl_ticker.history(start="2015-01-01", end="2024-12-31")
    if data.empty:
        print(f"No data found for {ticker}. Exiting.")
        return

    # 2. Feature Engineering
    print("Generating technical indicators...")
    features_df = generate_technical_indicators(data)

    # 3. Target Definition
    # We want to predict the return of the next day.
    features_df['target'] = features_df['Close'].pct_change().shift(-1)

    # 4. Data Cleaning
    # Drop rows with NaN values created by indicators or target shifting
    features_df = features_df.dropna()

    if features_df.empty:
        print("Not enough data after feature generation. Exiting.")
        return

    # 5. Model Training
    print("Training Random Forest model...")
    
    # Define features (X) and target (y)
    # We exclude the original OHLCV columns and the target itself from the features
    features_to_exclude = ['Open', 'High', 'Low', 'Close', 'Volume', 'target']
    X = features_df.drop(columns=features_to_exclude)
    y = features_df['target']

    # Time-series split for cross-validation
    tscv = TimeSeriesSplit(n_splits=5)

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)

    # Train the model on the full dataset
    model.fit(X, y)
    
    print("Model training complete.")

    # Evaluate the model (on the last split for a quick check)
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
    
    last_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    last_model.fit(X_train, y_train)
    predictions = last_model.predict(X_test)
    r2 = r2_score(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    print(f"Evaluation on last time-series split: R-squared = {r2:.4f}, MSE = {mse:.6f}")


    # 6. Save the Model
    output_dir = os.path.join(os.path.dirname(__file__), 'models')
    model_path = os.path.join(output_dir, 'random_forest_model.joblib')
    
    # Save the columns used for training, very important for prediction
    model_payload = {
        'model': model,
        'features': list(X.columns)
    }
    
    joblib.dump(model_payload, model_path)
    print(f"Model and feature list saved to {model_path}")

if __name__ == "__main__":
    train_model()
