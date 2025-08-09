from flask import Flask
from flask_cors import CORS
from .stocks.routes import stocks_bp

def create_app():
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    CORS(app)

    # Register the blueprint for the stocks API
    app.register_blueprint(stocks_bp)

    return app

# This block allows running the app directly for development
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
