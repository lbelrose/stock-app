from flask import Flask, jsonify, request
from flask_cors import CORS
from tradingview_ta import TA_Handler, Interval, Exchange
import logging

app = Flask(__name__)
CORS(app)

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="america",
            exchange="NASDAQ",
            interval=Interval.INTERVAL_1_DAY
        )
        analysis = handler.get_analysis()
        
        return jsonify({
            'symbol': symbol,
            'name': symbol,  # The API doesn't provide the full name, so we use the symbol as a fallback
            'close': analysis.indicators['close'],
            'open': analysis.indicators['open'],
            'high': analysis.indicators['high'],
            'low': analysis.indicators['low'],
            'volume': analysis.indicators['volume'],
            'change': analysis.indicators['change'],
            'recommendation': analysis.summary['RECOMMENDATION'],
            'rsi': analysis.indicators['RSI'],
            'macd': analysis.indicators['MACD.macd'],
        })
    except Exception as e:
        logging.error(f"Error fetching data for {symbol}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_stocks():
    # This is a simplified example with a predefined list of NASDAQ stocks
    # In a real application, you would have a database or use an API to get this data
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)