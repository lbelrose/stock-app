from flask import Flask
from flask_cors import CORS
from stocks.routes import stocks_bp
from analysis.routes import analysis_bp 
from markets.routes import markets_bp 
import os
import sys


def create_api():
    """
    Creates and configures the Flask API.
    """
    app = Flask(__name__)
    CORS(app)

    # Register the blueprint for the stocks API
    app.register_blueprint(stocks_bp)
    app.register_blueprint(analysis_bp) 
    app.register_blueprint(markets_bp) 

    return app

# This block allows running the app directly for development
if __name__ == '__main__':
    app = create_api()
    app.run(debug=True, port=5000)