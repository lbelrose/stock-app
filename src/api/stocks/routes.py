from flask import Blueprint, jsonify, request
from . import services

stocks_bp = Blueprint('stocks', __name__, url_prefix='/api')

@stocks_bp.route('/stocks/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    data, error = services.get_stock_data(symbol)
    if error:
        # Distinguish between not found and other server errors
        status_code = 404 if "No data found" in error else 500
        return jsonify({'error': error}), status_code
    return jsonify(data)

@stocks_bp.route('/stocks/<symbol>/history', methods=['GET'])
def get_stock_history(symbol):
    period = request.args.get('period', '1d')
    interval = request.args.get('interval', '15m')
    
    data, error = services.get_stock_history(symbol, period, interval)
    if error:
        status_code = 404 if "No historical data" in error else 500
        return jsonify({'error': error}), status_code
    return jsonify(data)

@stocks_bp.route('/search', methods=['GET'])
def search_stocks():
    query = request.args.get('q', '')
    results = services.search_stocks(query)
    return jsonify(results)

@stocks_bp.route('/stocks/cac40', methods=['GET'])
def get_cac40_stocks():
    stocks = services.get_cac40_stocks()
    return jsonify(stocks)
