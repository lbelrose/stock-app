import sys
import os
import re

# Add the 'src' directory to the Python path.
sys.path.insert(0, os.path.abspath('src'))

from api.analysis.train_model import train_model

def retrain_all_models():
    """
    Finds all existing models, extracts their tickers, and retrains them.
    """
    model_dir = "src/api/analysis/models"
    model_files = [f for f in os.listdir(model_dir) if f.endswith('.joblib')]
    
    tickers = []
    for model_file in model_files:
        # Final corrected regex
        match = re.match(r"buy_signal_classifier_([a-zA-Z0-9_]+).joblib", model_file)
        if match:
            tickers.append(match.group(1).upper())

    if not tickers:
        print("No existing models found to retrain.")
        return

    print(f"Found {len(tickers)} models to retrain: {tickers}")

    for ticker in tickers:
        print(f"--- Retraining model for {ticker} ---")
        try:
            train_model(ticker=ticker, model_class_name="RandomForestModel")
            print(f"--- Successfully retrained model for {ticker} ---\n")
        except Exception as e:
            print(f"!!! Failed to retrain model for {ticker}: {e} !!!\n")

if __name__ == "__main__":
    retrain_all_models()
