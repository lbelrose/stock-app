import os
import subprocess
import json
import re
import numpy as np
import sys


def optimize_thresholds(ticker_arg=None, model_dir="src/api/analysis/models", backtest_script="src/api/analysis/backtest.py", output_file="src/api/analysis/optimized_thresholds.json"):
    """
    Optimizes the buy threshold for each model by running backtests and
    selecting the threshold that yields the highest cumulative return.
    If a ticker is provided, only optimizes for that ticker.
    """
    if ticker_arg:
        # Construct the expected model filename based on the ticker
        model_files = [f"buy_signal_classifier_{ticker_arg.lower()}.joblib"]
        if not os.path.exists(os.path.join(model_dir, model_files[0])):
            print(f"Model file for ticker {ticker_arg} not found. Exiting.")
            return
    else:
        model_files = [f for f in os.listdir(model_dir) if f.endswith('.joblib')]

    # Load existing thresholds
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            optimized_thresholds = json.load(f)
    else:
        optimized_thresholds = {}

    threshold_range = np.arange(0.50, 0.71, 0.01) # Test thresholds from 0.50 to 0.70

    for model_file in model_files:
        model_name = model_file
        # Extract ticker from model name (e.g., buy_signal_classifier_amzn.joblib -> amzn)
        match = re.match(r"buy_signal_classifier_([a-zA-Z0-9.]+)\.joblib", model_name)
        if match:
            ticker = match.group(1).upper()
        else:
            print(f"Could not extract ticker from model file: {model_name}. Skipping.")
            continue

        print(f"Optimizing threshold for {ticker} using model {model_name}...")
        best_threshold = None
        max_cumulative_return = -np.inf

        for threshold in threshold_range:
            print(f"  Testing threshold: {threshold:.2f}")
            
            python_executable = sys.executable # Use the same python interpreter
            command = [
                sys.executable, "-m", "src.api.analysis.backtest",
                "--ticker", ticker,
                "--start_date", "2025-01-01", # Use a broad historical range for optimization
                "--end_date", "2025-06-30",
                "--buy_threshold", f"{threshold:.2f}",
                "--model_name", model_name
            ]
            
            process = subprocess.run(command, capture_output=True, text=True, cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
            
            # Extract cumulative return from output
            cumulative_return_match = re.search(r"Cumulative Return \(strategy\): [0-9.-]+ \(([0-9.-]+)%\)", process.stdout)
            
            if cumulative_return_match:
                cumulative_return_str = cumulative_return_match.group(1)
                try:
                    cumulative_return = float(cumulative_return_str)
                    if cumulative_return > max_cumulative_return:
                        max_cumulative_return = cumulative_return
                        best_threshold = threshold
                except ValueError:
                    print(f"    Could not parse cumulative return: {cumulative_return_str}")
            else:
                print(f"    Could not find cumulative return in backtest output for threshold {threshold:.2f}.")
                # print(process.stdout) # Uncomment for debugging backtest output

        if best_threshold is not None:
            optimized_thresholds[ticker] = {
                "model_name": model_name,
                "optimal_buy_threshold": float(f"{best_threshold:.2f}"),
                "max_cumulative_return_percent": float(f"{max_cumulative_return:.2f}")
            }
            print(f"Optimal threshold for {ticker}: {best_threshold:.2f} (Cumulative Return: {max_cumulative_return:.2f}%)")
        else:
            print(f"No optimal threshold found for {ticker}.")

    with open(output_file, 'w') as f:
        json.dump(optimized_thresholds, f, indent=4)
    print(f"Optimized thresholds saved to {output_file}")

if __name__ == "__main__":
    optimize_thresholds()
