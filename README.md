# TradeMind

A real-time stock tracking application for the Nasdaq and CAC40 Stock Exchanges, with a focus on AI-driven analysis and alerts. This application uses Angular 19, Python, and yfinance.

## Features

- Real-time stock quotes from Nasdaq and CAC40
- Interactive stock charts with multiple timeframes
- Stock search functionality
- Watchlist management
- Technical indicators (RSI, MACD)
- Responsive design for all devices

## Future Features

- AI-powered analysis of stock data
- Real-time buy/sell opportunity alerts

## Prerequisites

- Node.js 18.x or higher
- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Install Node.js dependencies:
```bash
npm install
```

2. Install Python dependencies:
```bash
pip install -r src/api/requirements.txt
```

## Development

Run the development server:
```bash
npm run dev
```

This will start both:
- Angular frontend at `http://localhost:4200`
- Python API at `http://localhost:5000`

Run Python tests:
```bash
pytest src/api/
```

## Project Structure

```
├── pyproject.toml              # Project configuration for tools like pytest
├── src/                        # Angular frontend
│   ├── api/                    # Python backend
│   │   ├── stocks/             # Stocks feature module
│   │   │   ├── routes.py       # Blueprint for stock routes
│   │   │   ├── services.py     # Business logic for stocks
│   │   │   └── tests/          # Tests for the stocks module
│   │   ├── analysis/           # Analysis feature module (AI predictions)
│   │   │   ├── routes.py       # Blueprint for analysis routes
│   │   │   ├── services.py     # Business logic for analysis
│   │   │   ├── train_model.py  # Script to train the AI model
│   │   │   └── models/         # Trained AI models
│   │   ├── markets/            # Market data module
│   │   │   ├── __init__.py
│   │   │   ├── services.py     # Logic to load market data from CSVs
│   │   │   └── models/         # CSV files for markets (e.g., NASDAQ.csv, CAC40.csv)
│   │   ├── api.py              # Flask application factory
│   │   └── requirements.txt    # Python dependencies
│   ├── app/                    # Application components
│   │   ├── features/           # Feature modules
│   │   └── shared/             # Shared components
│   └── assets/                 # Static assets
└── package.json                # Node.js dependencies
```

## Technologies

- Angular 19
- TailwindCSS
- Python Flask
- yfinance
- Chart.js

## License

MIT