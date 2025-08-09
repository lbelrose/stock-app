import pytest
from unittest.mock import patch
import pandas as pd
from .. import services

def test_get_stock_data_success():
    """
    Tests the successful retrieval of stock data.
    """
    with patch('yfinance.Ticker') as mock_ticker:
        # Mock yfinance Ticker object and its methods
        mock_hist_data = {
            'Open': [149.0, 150.0],
            'High': [151.0, 151.0],
            'Low': [148.0, 148.0],
            'Close': [145.0, 150.0],
            'Volume': [1100000, 1000000]
        }
        mock_hist_df = pd.DataFrame(mock_hist_data, index=pd.to_datetime(['2025-06-26', '2025-06-27']))
        
        mock_ticker.return_value.history.return_value = mock_hist_df
        mock_ticker.return_value.info = {'longName': 'Apple Inc.', 'recommendationKey': 'BUY'}

        # Call the service function directly
        data, error = services.get_stock_data('AAPL')

        # Assertions
        assert error is None
        assert data is not None
        assert data['symbol'] == 'AAPL'
        assert data['name'] == 'Apple Inc.'
        assert data['close'] == 150.0
        assert 'rsi' in data
        assert 'macd' in data
        assert data['recommendation'] == 'BUY'

def test_get_stock_data_no_data():
    """
    Tests the case where no data is found for a symbol.
    """
    with patch('yfinance.Ticker') as mock_ticker:
        # Simulate yfinance returning an empty DataFrame
        mock_ticker.return_value.history.return_value = pd.DataFrame()

        data, error = services.get_stock_data('UNKNOWN')

        assert data is None
        assert error is not None
        assert 'No data found for UNKNOWN' in error

def test_get_stock_data_exception():
    """
    Tests the service's error handling when yfinance raises an exception.
    """
    with patch('yfinance.Ticker') as mock_ticker:
        # Simulate an exception from yfinance
        mock_ticker.side_effect = Exception("yfinance failed")

        data, error = services.get_stock_data('FAIL')

        assert data is None
        assert error is not None
        assert 'yfinance failed' in error
