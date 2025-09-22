
from flask import Blueprint, jsonify, request
from .services import AnalysisService

analysis_bp = Blueprint('analysis_bp', __name__, url_prefix='/api')

@analysis_bp.route('/analysis/train/<string:ticker>', methods=['POST'])
def train_stock_model(ticker):
    """
    Triggers the training of a prediction model for a given stock ticker.
    Optional: model_class_name and model_kwargs can be passed in the request body.
    """
    try:
        data = request.get_json(silent=True) or {}
        model_class_name = data.get('model_class_name', 'RandomForestModel')
        model_kwargs = data.get('model_kwargs', {})
        
        result = AnalysisService.train_model_generic(ticker.upper(), model_class_name, **model_kwargs)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@analysis_bp.route('/analysis/predict/<string:ticker>', methods=['GET'])
def predict_stock_generic(ticker):
    """
    Provides a buy/sell/hold prediction for a given stock ticker using the generic prediction script.
    """
    try:
        prediction = AnalysisService.get_prediction_generic(ticker.upper())
        return jsonify(prediction)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Keep the old route for compatibility, but redirect to the new generic one
@analysis_bp.route('/analysis/<string:ticker>', methods=['GET'])
def predict_stock_old(ticker):
    return predict_stock_generic(ticker)

