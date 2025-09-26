import json
import subprocess
import re
import pandas as pd

def analyze_all_performances():
    """
    Runs backtests for all models using their optimized thresholds on an out-of-sample period
    and prints a summary of the performance.
    """
    thresholds_file = "src/api/analysis/optimized_thresholds.json"
    start_date = "2025-01-01"
    end_date = "2025-09-23"
    
    try:
        with open(thresholds_file, 'r') as f:
            optimized_thresholds = json.load(f)
    except FileNotFoundError:
        print(f"Error: Thresholds file not found at {thresholds_file}")
        return
        
    results = []
    
    print(f"--- Running Backtests from {start_date} to {end_date} ---")
    
    for ticker, data in optimized_thresholds.items():
        threshold = data['optimal_buy_threshold']
        model_name = data['model_name']
        
        print(f"Testing {ticker} with threshold {threshold}...")
        
        command = [
            "python", "-m", "src.api.analysis.backtest",
            "--ticker", ticker,
            "--start_date", start_date,
            "--end_date", end_date,
            "--buy_threshold", str(threshold),
            "--model_name", model_name
        ]
        
        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        output = process.stdout
        
        # Corrected Regex patterns to match the backtest output
        def extract_metric(pattern, text, is_int=False):
            match = re.search(pattern, text)
            if not match:
                return 0
            value = float(match.group(1))
            return int(value) if is_int else value

        cumulative_return_strategy = extract_metric(r"Cumulative Return \(strategy\): .*? \(([-0-9.]+)\%\)", output)
        cumulative_return_bh = extract_metric(r"Buy & Hold - Total Return: ([-0-9.]+)\%", output)
        max_drawdown_strategy = extract_metric(r"Max Drawdown: ([-0-9.]+)\%", output)
        win_rate = extract_metric(r"Win Rate: ([-0-9.]+)\%", output)
        total_trades = extract_metric(r"Total BUY signals: (\d+)", output, is_int=True)

        results.append({
            "Ticker": ticker,
            "Threshold": threshold,
            "Return (%)": cumulative_return_strategy,
            "Return B&H (%)": cumulative_return_bh,
            "Max Drawdown (%)": max_drawdown_strategy,
            "Win Rate (%)": win_rate,
            "Trades": total_trades
        })

    print("\n--- Performance Summary ---")
    if not results:
        print("No results to display.")
        return
        
    df = pd.DataFrame(results)
    # Set display options to show all columns and rows without truncation
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df.to_string(index=False))

if __name__ == "__main__":
    analyze_all_performances()