import sys
import os
import re
import argparse
from pathlib import Path

# Add the 'src' directory to the Python path.
sys.path.insert(0, os.path.abspath('src'))

from api.analysis.train_model import train_model

def retrain_all_models(model_class_name="RandomForestModel", model_kwargs=None):
    model_kwargs = model_kwargs or {}

    model_files = Path("src/api/analysis/models").glob("*.joblib")

    tickers = set()
    for model_file in model_files:
        match = re.match(r"([a-zA-Z0-9]+?)_([A-Z]+)\.joblib", model_file.name)
        if match:
            _, ticker = match.groups()
            tickers.add(ticker)

    if not tickers:
        print("No existing models found to retrain.")
        return

    tickers = sorted(tickers)
    print(f"Found {len(tickers)} models to retrain: {tickers}")

    for ticker in tickers:
        print(f"--- Retraining model for {ticker} with {model_class_name} ---")
        try:
            train_model(ticker=ticker, model_class_name=model_class_name, **model_kwargs)
            print(f"--- Successfully retrained {ticker} ---\n")
        except Exception as e:
            print(f"!!! Failed to retrain {ticker}: {e} !!!\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrain all existing models")
    parser.add_argument(
        '--model_class', type=str, default="RandomForestModel",
        help="The model class to use for retraining"
    )
    # Capture all other unknown args to pass as model kwargs
    args, unknown = parser.parse_known_args()

    model_kwargs = {}
    for i in range(0, len(unknown), 2):
        key = unknown[i].lstrip('--')
        value = unknown[i+1]
        try:
            model_kwargs[key] = int(value)
        except ValueError:
            try:
                model_kwargs[key] = float(value)
            except ValueError:
                model_kwargs[key] = value

    retrain_all_models(model_class_name=args.model_class, model_kwargs=model_kwargs)
