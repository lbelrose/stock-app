import os
import pandas as pd

def get_stocks(market: str):
    """
    Returns a list of stocks for a given market.
    """
    file_path = os.path.join(os.path.dirname(__file__), 'models', f"{market}.csv")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Market data not found for {market}")

    df = pd.read_csv(file_path, sep=',')
    df.rename(columns={'Name': 'name', 'Symbol': 'symbol'}, inplace=True)
    stocks = df.to_dict('records')
    return stocks
