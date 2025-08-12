
import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os

# --- Feature Generation ---

def generate_prediction_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates the same technical indicators used for training.
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
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
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

# --- Prediction Service ---

class PredictionService:
    _model = None
    _features = None

    @classmethod
    def _load_model(cls):
        """Loads the model from the joblib file."""
        if cls._model is None:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'random_forest_model.joblib')
            if not os.path.exists(model_path):
                raise FileNotFoundError("Model file not found. Please train the model first.")
            
            payload = joblib.load(model_path)
            cls._model = payload['model']
            cls._features = payload['features']
        return cls._model, cls._features

    @classmethod
    def get_prediction(cls, ticker: str) -> dict:
        """
        Generates a prediction for a given stock ticker.
        """
        model, features = cls._load_model()

        # 1. Fetch recent data
        stock_data = yf.Ticker(ticker).history(period="100d")
        if stock_data.empty:
            raise ValueError(f"Could not fetch data for {ticker}")

        # 2. Generate features
        features_df = generate_prediction_features(stock_data)

        # 3. Prepare the last row for prediction
        last_row = features_df.iloc[[-1]]
        if last_row.isnull().values.any():
            # Not enough data, try to get more history
            stock_data = yf.Ticker(ticker).history(period="200d")
            features_df = generate_prediction_features(stock_data)
            last_row = features_df.iloc[[-1]]
            if last_row.isnull().values.any():
                raise ValueError("Not enough data to generate a prediction even with extended history.")

        # Ensure the columns are in the same order as during training
        input_data = last_row[features]

        # 4. Predict
        prediction = model.predict(input_data)[0]

        # 5. Interpret the prediction
        if prediction > 0.0005:
            signal = "BUY"
            confidence = min(0.99, 0.5 + (prediction / 0.01))
        elif prediction < -0.0005:
            signal = "SELL"
            confidence = min(0.99, 0.5 + (abs(prediction) / 0.01))
        else:
            signal = "HOLD"
            confidence = 1.0 - (abs(prediction) / 0.0005)

        return {
            "ticker": ticker,
            "signal": signal,
            "confidence": f"{confidence:.2f}",
            "predicted_return": f"{prediction:.6f}",
            "model_status": "active"
        }
