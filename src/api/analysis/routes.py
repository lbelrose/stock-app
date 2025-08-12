
from flask import Blueprint, jsonify
from .services import PredictionService

analysis_bp = Blueprint('analysis_bp', __name__, url_prefix='/api')

@analysis_bp.route('/analysis/<string:ticker>', methods=['GET'])
def predict_stock(ticker):
    """
    Provides a buy/sell/hold prediction for a given stock ticker.
    """
    try:
        prediction = PredictionService.get_prediction(ticker.upper())
        return jsonify(prediction)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Generic error for other unexpected issues
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

