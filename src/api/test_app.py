import pytest
from unittest.mock import patch, MagicMock
from .app import create_app
import pandas as pd
from datetime import datetime

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_stock_data_success(client):
    with patch('yfinance.Ticker') as mock_ticker:
        # Mock historical data as a pandas DataFrame
        mock_hist_data = {
            'Open': [140.0, 149.0, 150.0],
            'High': [142.0, 151.0, 151.0],
            'Low': [139.0, 148.0, 148.0],
            'Close': [145.0, 145.0, 150.0],
            'Volume': [900000, 1100000, 1000000]
        }
        mock_hist_df = pd.DataFrame(mock_hist_data, index=pd.to_datetime(['2025-06-25', '2025-06-26', '2025-06-27']))
        
        mock_ticker.return_value.history.return_value = mock_hist_df

        # Mock info data
        mock_ticker.return_value.info = {'longName': 'Apple Inc.', 'recommendationKey': 'BUY'}

        response = client.get('/api/stock/AAPL')
        assert response.status_code == 200
        data = response.get_json()
        assert data['symbol'] == 'AAPL'
        assert data['name'] == 'Apple Inc.'
        assert 'close' in data
        assert 'change' in data
        assert 'rsi' in data # Check for RSI and MACD
        assert 'macd' in data

def test_get_stock_data_no_data(client):
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker.return_value.history.return_value = pd.DataFrame() # Simulate empty DataFrame

        response = client.get('/api/stock/UNKNOWN')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'No data found for UNKNOWN' in data['error']

def test_get_stock_history_success(client):
    with patch('yfinance.Ticker') as mock_ticker:
        # Mock historical data with proper DatetimeIndex
        mock_hist_data = {
            'Open': [100, 103],
            'High': [105, 107],
            'Low': [99, 102],
            'Close': [103, 106],
            'Volume': [1000, 1200]
        }
        mock_hist_df = pd.DataFrame(mock_hist_data, index=pd.to_datetime([
            '2025-06-27 09:30:00',
            '2025-06-27 09:45:00'
        ]))
        
        mock_ticker.return_value.history.return_value = mock_hist_df

        response = client.get('/api/stock/AAPL/history?period=1d&interval=15m')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]['datetime'] == '2025-06-27 09:30:00'
        assert data[0]['close'] == 103
        assert data[1]['datetime'] == '2025-06-27 09:45:00'
        assert data[1]['close'] == 106

def test_get_stock_history_no_data(client):
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker.return_value.history.return_value = pd.DataFrame() # Simulate empty DataFrame

        response = client.get('/api/stock/UNKNOWN/history?period=1d&interval=15m')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'No historical data for UNKNOWN with period=1d and interval=15m' in data['error']

def test_search_stocks_query(client):
    response = client.get('/api/search?q=apple')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(stock['symbol'] == 'AAPL' for stock in data)

def test_search_stocks_no_query(client):
    response = client.get('/api/search')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert len(data) <= 10 # Should return first 10 default stocks
