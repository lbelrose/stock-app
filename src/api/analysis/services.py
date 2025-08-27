import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os


def generate_prediction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates the same technical indicators used during training.
    """
    price_col = 'Close'
    volume_col = 'Volume'
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
    ti_df['rsi'] = 100 - (100 / (1 + rs)))

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


class PredictionService:
    _model = None
    _features = None

    @classmethod
    def _load_model(cls):
        """
        Lazy-loads the trained model and feature list.
        """
        if cls._model is None:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'random_forest_classifier.joblib')
            if not os.path.exists(model_path):
                raise FileNotFoundError("Model file not found. Run train_model.py first.")

            payload = joblib.load(model_path)
            cls._model = payload['model']
            cls._features = payload['features']

            if not isinstance(cls._model, RandomForestClassifier):
                raise TypeError("Loaded model is not a RandomForestClassifier.")

        return cls._model, cls._features

    @classmethod
    def get_prediction(cls, ticker: str) -> dict:
        """
        Generates a trading signal (BUY/SELL/HOLD) for the given ticker.
        """
        model, feature_names = cls._load_model()

        # Fetch data
        stock_data = yf.Ticker(ticker).history(period="250d")
        if stock_data.empty:
            raise ValueError(f"No data available for {ticker}.")

        # Ensure chronological order
        stock_data = stock_data.sort_index(ascending=True)

        # Generate features
        raw_features = generate_prediction_features(stock_data)

        # Lag features by one day
        lagged_features = raw_features.shift(1)
        last_row = lagged_features.iloc[[-1]][feature_names]

        # Check for missing values
        if last_row.isnull().values.any():
            missing_cols = last_row.columns[last_row.isnull().any()].tolist()
            raise ValueError(f"Missing values in features: {missing_cols}. Insufficient history.")

        # Predict probabilities
        proba = model.predict_proba(last_row)[0]
        p_up = proba[1]
        p_down = proba[0]

        # Decision logic
        threshold = 0.55
        if p_up > threshold:
            signal = "BUY"
            confidence = min(0.99, (p_up - 0.5) / 0.5)
        elif p_down > threshold:
            signal = "SELL"
            confidence = min(0.99, (p_down - 0.5) / 0.5)
        else:
            signal = "HOLD"
            confidence = max(0.0, 1.0 - abs(p_up - 0.5) * 2)

        confidence = max(0.0, min(1.0, confidence))

        return {
            "ticker": ticker,
            "signal": signal,
            "confidence": f"{confidence:.2f}",
            "probability_up": f"{p_up:.4f}",
            "probability_down": f"{p_down:.4f}",
            "model_status": "active",
            "timestamp": pd.Timestamp.now(tz='UTC').isoformat()
        }