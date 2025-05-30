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
    # This is a simplified example with a predefined list of Paris stocks
    # In a real application, you would have a database or use an API to get this data
    paris_stocks = [
        {"symbol": "AC.PA", "name": "Accor SA"},
        {"symbol": "AI.PA", "name": "Air Liquide SA"},
        {"symbol": "AIR.PA", "name": "Airbus SE"},
        {"symbol": "ALO.PA", "name": "Alstom SA"},
        {"symbol": "BN.PA", "name": "Danone SA"},
        {"symbol": "BNP.PA", "name": "BNP Paribas SA"},
        {"symbol": "CA.PA", "name": "Carrefour SA"},
        {"symbol": "CAP.PA", "name": "Capgemini SE"},
        {"symbol": "CS.PA", "name": "AXA SA"},
        {"symbol": "DG.PA", "name": "Vinci SA"},
        {"symbol": "ENGI.PA", "name": "Engie SA"},
        {"symbol": "GLE.PA", "name": "Société Générale SA"},
        {"symbol": "KER.PA", "name": "Kering SA"},
        {"symbol": "LR.PA", "name": "Legrand SA"},
        {"symbol": "MC.PA", "name": "LVMH Moët Hennessy Louis Vuitton SE"},
        {"symbol": "ML.PA", "name": "Michelin SCA"},
        {"symbol": "OR.PA", "name": "L'Oréal SA"},
        {"symbol": "ORA.PA", "name": "Orange SA"},
        {"symbol": "RI.PA", "name": "Pernod Ricard SA"},
        {"symbol": "RMS.PA", "name": "Hermès International SCA"},
        {"symbol": "SAF.PA", "name": "Safran SA"},
        {"symbol": "SAN.PA", "name": "Sanofi SA"},
        {"symbol": "SGO.PA", "name": "Compagnie de Saint-Gobain SA"},
        {"symbol": "SU.PA", "name": "Schneider Electric SE"},
        {"symbol": "VIE.PA", "name": "Veolia Environnement SA"},
        {"symbol": "VIV.PA", "name": "Vivendi SE"},
    ]

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
        {"symbol": "ORCL", "name": "Oracle Corporation"}
    ]

    query = request.args.get('q', '').lower()
    if query:
        results = [stock for stock in nasdaq_stocks if query in stock['symbol'].lower() or query in stock['name'].lower()]
        return jsonify(results[:10])  # Limit to 10 results
    
    return jsonify(nasdaq_stocks[:10])  # Return first 10 if no query

if __name__ == '__main__':
    app.run(debug=True, port=5000)