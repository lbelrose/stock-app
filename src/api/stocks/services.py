import yfinance as yf
import logging
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import os
from markets.models import get_stocks as get_market_stocks

def get_stock_data(symbol: str):
    """
    Fetches and calculates main data for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        logging.info(f"Fetching data for {symbol}: {ticker}")
        
        hist = ticker.history(period="5d") # Fetch more data for calculations
        
        if hist.empty:
            return None, f"No data found for {symbol}"
            
        last_quote = hist.iloc[-1]
        prev_close = hist.iloc[-2]['Close'] if len(hist) > 1 else last_quote['Close']
        change = ((last_quote['Close'] - prev_close) / prev_close) * 100
        
        info = ticker.info
        
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'close': float(last_quote['Close']),
            'open': float(last_quote['Open']),
            'high': float(last_quote['High']),
            'low': float(last_quote['Low']),
            'volume': int(last_quote['Volume']),
            'change': float(change),
            'recommendation': _get_recommendation(info),
            'rsi': _calculate_rsi(hist['Close']),
            'macd': _calculate_macd(hist['Close'])
        }, None
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {str(e)}")
        return None, str(e)

def get_stock_history(symbol: str, period: str, interval: str):
    """
    Fetches historical data for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return None, f"No historical data for {symbol} with period={period} and interval={interval}"
            
        hist_data = [
            {
                'datetime': index.strftime('%Y-%m-%d %H:%M:%S'),
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            }
            for index, row in hist.iterrows()
        ]
        return hist_data, None
    except Exception as e:
        logging.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return None, str(e)

def get_stocks(market: str = 'NASDAQ'):
    """
    Fetches the list of stocks in a given market.
    """
    if market not in ['NASDAQ', 'CAC40']:
        raise ValueError("Market must be either 'NASDAQ' or 'CAC40'")
    
    try:
        return get_market_stocks(market)
    except FileNotFoundError:
        logging.error(f"Market data file not found for {market}")
        return []

def search_stocks(query: str):
    """
    Searches for stocks based on a query from a combined list of
    dynamically fetched NASDAQ and CAC40 stocks.
    """
    nasdaq_stocks = get_stocks('NASDAQ')
    cac40_stocks = get_stocks('CAC40')
    stocks = nasdaq_stocks + cac40_stocks
    
    if not query:
        return nasdaq_stocks[:20]

    query = query.lower()
    results = [
        stock for stock in stocks
        if query in stock['symbol'].lower() or query in stock['name'].lower()
    ]
    
    return results[:20]

# Helper functions (private)
def _calculate_rsi(prices, periods=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1]
    return float(last_rsi) if not np.isnan(last_rsi) else 50

def _calculate_macd(prices, fast=12, slow=26, signal=9):
    fast_ema = prices.ewm(span=fast, adjust=False).mean()
    slow_ema = prices.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    return float(macd_line.iloc[-1])

def _get_recommendation(info):
    recommendation = info.get('recommendationKey', '').upper()
    return recommendation if recommendation else 'NEUTRAL'