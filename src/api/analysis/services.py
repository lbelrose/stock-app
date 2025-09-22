import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from .features import generate_technical_features

import json
import subprocess
import sys

class PredictionService:
    _models = {}  # Cache for loaded models
    _training_processes = {} # Track running training processes
    _optimized_thresholds = {} # Cache for optimized thresholds

    @classmethod
    def _load_optimized_thresholds(cls):
        """Loads optimized thresholds from the JSON file."""
        if cls._optimized_thresholds.keys(): # Already loaded
            return

        thresholds_path = os.path.join(os.path.dirname(__file__), 'optimized_thresholds.json')
        try:
            with open(thresholds_path, 'r') as f:
                cls._optimized_thresholds = json.load(f)
            print(f"Successfully loaded optimized thresholds from {thresholds_path}")
        except FileNotFoundError:
            print(f"Warning: Optimized thresholds file not found at {thresholds_path}. Using default values.")
            cls._optimized_thresholds = {}
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {thresholds_path}. Using default values.")
            cls._optimized_thresholds = {}

    @classmethod
    def _get_model_path(cls, ticker: str) -> (str, str):
        """Returns the paths for the specialist and general models."""
        normalized_ticker = ticker.lower().replace('.pa', '')
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        specialist_name = f"buy_signal_classifier_{normalized_ticker}.joblib"
        general_name = "buy_signal_classifier_general.joblib"
        return os.path.join(model_dir, specialist_name), os.path.join(model_dir, general_name)

    @classmethod
    def _load_model(cls, model_path: str):
        """Loads a model from a given path and caches it."""
        model_name = os.path.basename(model_path)
        if model_name in cls._models:
            payload = cls._models[model_name]
        else:
            print(f"Loading model from disk: {model_name}")
            payload = joblib.load(model_path)
            cls._models[model_name] = payload
        
        return payload['model'], payload['features']

    @classmethod
    def get_prediction(cls, ticker: str) -> dict:
        """
        Handles the logic of retrieving a prediction.
        - If a specialist model exists, use it.
        - If not, trigger a background training process and notify the user.
        - If a training process is already running, notify the user.
        - If training fails (model still doesn't exist on next request), use the general model as a fallback.
        """
        cls._load_optimized_thresholds() # Ensure thresholds are loaded
        specialist_path, general_path = cls._get_model_path(ticker)

        if os.path.exists(specialist_path):
            model, features = cls._load_model(specialist_path)
            return cls._generate_prediction_for_model(ticker, model, features)

        # Check if training is already in progress
        if ticker in cls._training_processes:
            proc = cls._training_processes[ticker]
            if proc.poll() is None: # Process is still running
                return {
                    "status": "training_in_progress",
                    "message": f"A specialist model for {ticker} is still being generated. Please try again in a moment."
                }
            else: # Process finished
                del cls._training_processes[ticker]
                # Re-check if the model was created successfully
                if os.path.exists(specialist_path):
                    model, features = cls._load_model(specialist_path)
                    return cls._generate_prediction_for_model(ticker, model, features)
                else: # Training finished but failed to create a model
                    stdout, stderr = proc.communicate()
                    print(f"Training for {ticker} finished but no model was created. STDOUT: {stdout.decode().strip()}, STDERR: {stderr.decode().strip()}. Falling back to general model.")
                    if os.path.exists(general_path):
                        model, features = cls._load_model(general_path)
                        return cls._generate_prediction_for_model(ticker, model, features, model_type="general (fallback)")
                    else:
                         raise FileNotFoundError("Specialist model training failed and the general fallback model is also missing.")

        # If no model and no training in progress, start training
        print(f"Specialist model for {ticker} not found. Starting background training.")
        python_executable = sys.executable # Use the same python interpreter
        command = [
            python_executable,
            "src/api/analysis/train_model.py",
            "--ticker", ticker
        ]
        
        # Start the process in the background
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=project_root)
        cls._training_processes[ticker] = proc

        return {
            "status": "training_started",
            "message": f"A specialist model for {ticker} is being generated. Please try again in a few minutes."
        }

    @classmethod
    def _generate_prediction_for_model(cls, ticker: str, model, feature_names: list, model_type="specialist") -> dict:
        """
        The core prediction logic, separated to be reusable.
        """
        stock_data = yf.Ticker(ticker).history(period="250d")
        if stock_data.empty:
            raise ValueError(f"No data available for {ticker}.")

        stock_data = stock_data.sort_index(ascending=True)
        raw_features = generate_technical_features(stock_data)
        lagged_features = raw_features.shift(1)
        last_row = lagged_features.iloc[[-1]][feature_names]

        if last_row.isnull().values.any():
            missing_cols = last_row.columns[last_row.isnull().any()].tolist()
            raise ValueError(f"Missing values in features: {missing_cols}. Not enough history.")

        proba = model.predict_proba(last_row)[0]
        p_up, p_down = proba[1], proba[0]

        # Get optimized or default thresholds
        ticker_thresholds = cls._optimized_thresholds.get(ticker.split(".")[0], {})
        buy_threshold = ticker_thresholds.get('optimal_buy_threshold', 0.55)
        sell_threshold = ticker_thresholds.get('optimal_sell_threshold', 0.65) # Assuming a sell threshold might exist

        if p_up > buy_threshold:
            signal = "BUY"
            confidence = min(0.99, (p_up - 0.5) / 0.5)
        elif p_down > sell_threshold:
            signal = "SELL"
            confidence = min(0.99, (p_down - 0.5) / 0.5)
        else:
            signal = "HOLD"
            confidence = 1.0 - abs(p_up - 0.5) * 2

        return {
            "ticker": ticker,
            "signal": signal,
            "confidence": f"{max(0.0, min(1.0, confidence)):.2f}",
            "probability_up": f"{p_up:.4f}",
            "probability_down": f"{p_down:.4f}",
            "buy_threshold": buy_threshold,
            "model_type": model_type,
            "timestamp": pd.Timestamp.now(tz='UTC').isoformat()
        }
    