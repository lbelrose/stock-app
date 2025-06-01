from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import logging

app = Flask(__name__)
CORS(app)

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history()
        
        if hist.empty:
            return jsonify({'error': f'No data found for {symbol}'}), 404
            
        # Get the last row of historical data
        last_quote = hist.iloc[-1]
        
        # Calculate daily change
        prev_close = hist.iloc[-2]['Close'] if len(hist) > 1 else last_quote['Close']
        change = ((last_quote['Close'] - prev_close) / prev_close) * 100
        
        # Get basic info
        info = ticker.info
        
        return jsonify({
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'close': last_quote['Close'],
            'open': last_quote['Open'],
            'high': last_quote['High'],
            'low': last_quote['Low'],
            'volume': last_quote['Volume'],
            'change': change,
            'recommendation': get_recommendation(info),
            'rsi': calculate_rsi(hist['Close']),
            'macd': calculate_macd(hist['Close'])
        })
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_stocks():
    # This is a simplified example with a predefined list of NASDAQ stocks
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
        {"symbol": "INTC", "name": "Intel Corporation"}
    ]

    query = request.args.get('q', '').lower()
    if query:
        results = [stock for stock in nasdaq_stocks if query in stock['symbol'].lower() or query in stock['name'].lower()]
        return jsonify(results[:10])  # Limit to 10 results
    
    return jsonify(nasdaq_stocks[:10])  # Return first 10 if no query

def calculate_rsi(prices, periods=14):
    import numpy as np
    
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    
    # Calculate RS and RSI
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50

def calculate_macd(prices, fast=12, slow=26, signal=9):
    # Calculate EMAs
    fast_ema = prices.ewm(span=fast, adjust=False).mean()
    slow_ema = prices.ewm(span=slow, adjust=False).mean()
    
    # Calculate MACD line
    macd_line = fast_ema - slow_ema
    
    return float(macd_line.iloc[-1])

def get_recommendation(info):
    # Simplified recommendation logic based on available metrics
    recommendation = info.get('recommendationKey', '').upper()
    if recommendation:
        return recommendation
    
    # Default to NEUTRAL if no recommendation is available
    return 'NEUTRAL'

if __name__ == '__main__':
    app.run(debug=True, port=5000)