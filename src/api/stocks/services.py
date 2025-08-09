import yfinance as yf
import logging
import numpy as np

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

def search_stocks(query: str):
    """
    Searches for stocks based on a query.
    """
    nasdaq_stocks = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "AMZN", "name": "Amazon.com Inc."},
        {"symbol": "GOOGL", "name": "Alphabet Inc."},
        {"symbol": "META", "name": "Meta Platforms Inc."},
        {"symbol": "TSLA", "name": "Tesla, Inc."},
        {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        {"symbol": "AMD", "name": "Advanced Micro Devices"},
        {"symbol": "INTC", "name": "Intel Corporation"},
        {"symbol": "ORCL", "name": "Oracle Corporation"},
        {"symbol": "CSCO", "name": "Cisco Systems Inc."},
        {"symbol": "ADBE", "name": "Adobe Inc."},
        {"symbol": "NFLX", "name": "Netflix Inc."},
        {"symbol": "PYPL", "name": "PayPal Holdings Inc."},
    ]
    if query:
        query = query.lower()
        return [
            stock for stock in nasdaq_stocks 
            if query in stock['symbol'].lower() or query in stock['name'].lower()
        ][:10]
    return nasdaq_stocks[:10]

def get_cac40_stocks():
    """
    Returns a list of CAC40 stocks.
    """
    return [
        {"symbol": "AI.PA", "name": "Air Liquide"}, {"symbol": "AIR.PA", "name": "Airbus"},
        {"symbol": "ALO.PA", "name": "Alstom"}, {"symbol": "MT.AS", "name": "ArcelorMittal"},
        {"symbol": "CS.PA", "name": "AXA"}, {"symbol": "BNP.PA", "name": "BNP Paribas"},
        {"symbol": "EN.PA", "name": "Bouygues"}, {"symbol": "CAP.PA", "name": "Capgemini"},
        {"symbol": "CA.PA", "name": "Carrefour"}, {"symbol": "ACA.PA", "name": "Crédit Agricole"},
        {"symbol": "BN.PA", "name": "Danone"}, {"symbol": "DSY.PA", "name": "Dassault Systèmes"},
        {"symbol": "EDEN.PA", "name": "Edenred"}, {"symbol": "EL.PA", "name": "EssilorLuxottica"},
        {"symbol": "ERF.PA", "name": "Eurofins Scientific"}, {"symbol": "RMS.PA", "name": "Hermès"},
        {"symbol": "KER.PA", "name": "Kering"}, {"symbol": "OR.PA", "name": "L'Oréal"},
        {"symbol": "LR.PA", "name": "Legrand"}, {"symbol": "MC.PA", "name": "LVMH"},
        {"symbol": "ML.PA", "name": "Michelin"}, {"symbol": "ORA.PA", "name": "Orange"},
        {"symbol": "RI.PA", "name": "Pernod Ricard"}, {"symbol": "PUB.PA", "name": "Publicis"},
        {"symbol": "RNO.PA", "name": "Renault"}, {"symbol": "SAF.PA", "name": "Safran"},
        {"symbol": "SGO.PA", "name": "Saint-Gobain"}, {"symbol": "SAN.PA", "name": "Sanofi"},
        {"symbol": "SU.PA", "name": "Schneider Electric"}, {"symbol": "STLAP.PA", "name": "Stellantis"},
        {"symbol": "STMPA.PA", "name": "STMicroelectronics"}, {"symbol": "TEP.PA", "name": "Teleperformance"},
        {"symbol": "TTE.PA", "name": "TotalEnergies"}, {"symbol": "HO.PA", "name": "Thales"},
        {"symbol": "URW.AS", "name": "Unibail-Rodamco-Westfield"}, {"symbol": "VIE.PA", "name": "Veolia"},
        {"symbol": "DG.PA", "name": "Vinci"}
    ]

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
