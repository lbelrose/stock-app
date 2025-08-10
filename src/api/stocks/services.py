import yfinance as yf
import logging
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# --- Caching Mechanism ---
_nasdaq_stocks_cache = {
    "timestamp": None,
    "data": []
}
_cac40_stocks_cache = {
    "timestamp": None,
    "data": []
}
CACHE_DURATION = timedelta(hours=24)

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

def get_nasdaq_stocks():
    """
    Fetches the list of NASDAQ-listed stocks from the official NASDAQ FTP server.
    Uses a 24-hour cache to avoid excessive downloads.
    """
    now = datetime.now()
    if _nasdaq_stocks_cache["timestamp"] and (now - _nasdaq_stocks_cache["timestamp"] < CACHE_DURATION):
        logging.info("Returning cached NASDAQ stocks.")
        return _nasdaq_stocks_cache["data"]

    logging.info("Fetching fresh NASDAQ stocks.")
    try:
        url = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
        df = pd.read_csv(url, sep='|', skipfooter=1, engine='python')
        df = df[['Symbol', 'Security Name']]
        df.rename(columns={'Security Name': 'name', 'Symbol': 'symbol'}, inplace=True)
        
        # Filter out test stocks, warrants, and convert to dictionary
        df = df[~df['symbol'].str.contains('\$|\.')]
        all_stocks = df.to_dict('records')
        
        # Ensure symbol and name are valid strings
        stocks = [
            stock for stock in all_stocks 
            if (isinstance(stock.get('symbol'), str) and stock.get('symbol')) and \
               (isinstance(stock.get('name'), str) and stock.get('name'))
        ]
        
        _nasdaq_stocks_cache["data"] = stocks
        _nasdaq_stocks_cache["timestamp"] = now
        logging.info(f"Successfully fetched and cached {len(stocks)} NASDAQ stocks.")
        return stocks
    except Exception as e:
        logging.error(f"Failed to fetch or parse NASDAQ stocks list: {e}")
        return _nasdaq_stocks_cache["data"] if _nasdaq_stocks_cache["data"] else []

def get_cac40_stocks():
    """
    Scrapes the CAC 40 components from the Wikipedia page.
    Uses a 24-hour cache.
    """
    now = datetime.now()
    if _cac40_stocks_cache["timestamp"] and (now - _cac40_stocks_cache["timestamp"] < CACHE_DURATION):
        logging.info("Returning cached CAC40 stocks.")
        return _cac40_stocks_cache["data"]
    
    logging.info("Fetching fresh CAC40 stocks.")
    try:
        url = "https://en.wikipedia.org/wiki/CAC_40"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        if not table:
            logging.error("Could not find the constituents table on Wikipedia.")
            return []

        stocks = []
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) > 2:
                company_name = cells[0].text.strip()
                ticker_symbol = cells[2].text.strip()
                
                # Ensure both are valid strings before proceeding
                if not (isinstance(company_name, str) and company_name and \
                        isinstance(ticker_symbol, str) and ticker_symbol):
                    continue

                if not ticker_symbol.endswith('.PA'):
                    ticker_symbol += '.PA'
                stocks.append({'name': company_name, 'symbol': ticker_symbol})
        
        _cac40_stocks_cache["data"] = stocks
        _cac40_stocks_cache["timestamp"] = now
        logging.info(f"Successfully scraped and cached {len(stocks)} CAC40 stocks.")
        return stocks
    except Exception as e:
        logging.error(f"An error occurred while scraping CAC40 stocks: {e}")
        return _cac40_stocks_cache["data"] if _cac40_stocks_cache["data"] else []

def search_stocks(query: str):
    """
    Searches for stocks based on a query from a combined list of
    dynamically fetched NASDAQ and CAC40 stocks.
    """
    nasdaq_stocks = get_nasdaq_stocks()
    cac40_stocks = get_cac40_stocks()
    combined_stocks = nasdaq_stocks + cac40_stocks
    
    if not query:
        return nasdaq_stocks[:20]

    query = query.lower()
    results = [
        stock for stock in combined_stocks
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