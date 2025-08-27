from flask import Flask
from flask_cors import CORS
from stocks.routes import stocks_bp
from analysis.routes import analysis_bp  # Import the new blueprint
import os
import sys

# Add the parent directory to the path to allow relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def create_api():
    """
    Creates and configures the Flask API.
    """
    app = Flask(__name__)
    CORS(app)

    # Register the blueprint for the stocks API
    app.register_blueprint(stocks_bp)
    app.register_blueprint(analysis_bp)  # Register the analysis blueprint

    return app

# This block allows running the app directly for development
if __name__ == '__main__':
    app = create_api()
    app.run(debug=True, port=5000)