import pandas as pd

def generate_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates the 12 technical features used in the buy signal model.
    Ensures consistency with training and prediction.
    """
    ti_df = df.copy()
    close = ti_df['Close']
    volume = ti_df['Volume']

    # 1. Returns
    ti_df['return_1d'] = close.pct_change(1)
    ti_df['return_5d'] = close.pct_change(5)

    # Lagged returns
    for lag in [1, 2, 3]:
        ti_df[f'return_lag_{lag}'] = ti_df['return_1d'].shift(lag)

    # 2. Volume
    ti_df['volume_sma_20'] = volume.rolling(20).mean()
    ti_df['volume_ratio'] = volume / ti_df['volume_sma_20'].replace(0, 1e-10)
    ti_df['volume_lag_1'] = volume.shift(1)
    ti_df['volume_lag_2'] = volume.shift(2)
    ti_df['volume_ratio_lag_1'] = ti_df['volume_lag_1'] / ti_df['volume_sma_20'].replace(0, 1e-10)
    ti_df['volume_ratio_lag_2'] = ti_df['volume_lag_2'] / ti_df['volume_sma_20'].replace(0, 1e-10)

    # 3. Trend
    ti_df['sma_10'] = close.rolling(10).mean()
    ti_df['close_sma10_ratio'] = close / ti_df['sma_10'].replace(0, 1e-10)

    # 4. Volatility
    ti_df['volatility_20'] = ti_df['return_1d'].rolling(20).std()

    # 5. RSI
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, 1e-10)
    ti_df['rsi'] = 100 - (100 / (1 + rs))
    ti_df['rsi_lag_1'] = ti_df['rsi'].shift(1)

    return ti_df
