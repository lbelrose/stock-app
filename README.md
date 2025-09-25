# TradeMind

A real-time stock tracking application for the Nasdaq and CAC40 Stock Exchanges, featuring AI-driven trend analysis. This application is built with Angular 21, Python Flask, and yfinance.

## Key Features

- **Market Data:** Real-time stock quotes from both Nasdaq and CAC40 exchanges.
- **AI-Powered Analysis:** Predicts stock trends (up/down) using a Machine Learning model trained on technical indicators.
- **Interactive Charts:** Visualize historical data across multiple timeframes (1D, 7D, 1M, 1Y) and intervals (1m, 5m, 15m, 30m, 1h).
- **Watchlist Management:** Keep track of your favorite stocks.
- **Stock Search:** Easily find any stock from the available markets.
- **Responsive Design:** Fully functional on both desktop and mobile devices.

## Prerequisites

- Node.js 18.x or higher
- Python 3.8 or higher
- pip (Python package manager)

## Installation

1.  Install Node.js dependencies:
    ```bash
    npm install
    ```

2.  Install Python dependencies:
    ```bash
    pip install -r src/api/requirements.txt
    ```

## Development

Run the development server for both frontend and backend:
```bash
npm run dev
```
This will start:
- Angular frontend at `http://localhost:4200`
- Python API at `http://localhost:5000`

## Tests

Run the Python backend tests:
```bash
pytest src/api/
```

## Project Structure
```
├── src/
│   ├── api/                    # Python backend (Flask)
│   │   ├── analysis/           # Analysis & Prediction module
│   │   │   ├── models/         # Trained AI models (.joblib)
│   │   │   ├── routes.py       # API routes for analysis
│   │   │   ├── services.py     # Business logic for predictions
│   │   │   └── train_model.py  # Model training script
│   │   ├── markets/            # Market data module
│   │   │   ├── models/         # Market data files (CSV)
│   │   │   ├── routes.py       # API routes for market lists
│   │   │   └── services.py     # Logic for reading market data
│   │   ├── stocks/             # Stock data module
│   │   │   ├── routes.py       # API routes for stock data
│   │   │   ├── services.py     # Logic for fetching stock data
│   │   │   └── tests/          # Unit tests for stock services
│   │   ├── api.py              # Flask application factory
│   │   └── requirements.txt    # Python dependencies
│   ├── app/                    # Angular frontend
│   │   ├── features/           # Feature modules
│   │   │   ├── dashboard/      # Dashboard component
│   │   │   └── stock-detail/   # Stock detail component
│   │   └── shared/             # Shared components, services, models
│   │       ├── components/     # Reusable UI components
│   │       ├── models/         # TypeScript models
│   │       └── services/       # Angular services
│   └── ...
└── package.json
```

## Technologies

- Angular 21
- TailwindCSS
- Python Flask
- yfinance
- Scikit-learn
- Chart.js

## License

MIT

## Scripts de Maintenance

Le projet inclut des scripts utilitaires à la racine pour faciliter la maintenance des modèles de Machine Learning.

### `retrain_all.py`

Ce script recherche tous les modèles `.joblib` existants dans `src/api/analysis/models`, extrait leurs tickers, et relance leur entraînement complet. Après chaque entraînement, il déclenche automatiquement l'optimisation du seuil d'achat.

**Usage :**
```bash
python retrain_all.py
```
C'est utile pour mettre à jour tous les modèles en une seule commande après des modifications de la logique d'entraînement ou des features.

### `evaluate_performance.py`

Ce script évalue la performance de tous les modèles pour lesquels un seuil optimal a été défini. Il exécute un backtest sur une période "hors échantillon" (définie dans le script, par défaut `2025-07-01` au `2025-09-23`) et affiche un tableau récapitulatif des performances.

**Usage :**
```bash
python evaluate_performance.py
```

**Exemple de sortie :**
```
--- Performance Summary ---
Ticker  Threshold  Return (%)  Return B&H (%)  Max Drawdown (%)  Win Rate (%)  Trades
   AIR       0.51        4.57            2.93             -4.19         47.83      23
  AMZN       0.58        1.13           -2.77              0.00        100.00       1
   GLE       0.59        0.00            0.00              0.00          0.00       0
  NVDA       0.52       -7.16            3.23            -10.78         41.67      24
    SU       0.51        3.90            5.88             -2.74         55.56      18
  TSLA       0.56       -1.13           40.85             -2.12         50.00       2
```