from flask import Blueprint, jsonify
from . import services

markets_bp = Blueprint('markets', __name__, url_prefix='/api')

@markets_bp.route('/markets/<market>', methods=['GET'])
def get_stocks(market):
    stocks = services.get_stocks(market)
    return jsonify(stocks)
