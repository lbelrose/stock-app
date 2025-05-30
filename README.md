# Paris Stock Tracker

A real-time stock tracking application for the Paris Stock Exchange using Angular 19, Python, and TradingView API.

## Features

- Real-time stock quotes from Euronext Paris
- Interactive stock charts with multiple timeframes
- Stock search functionality
- Watchlist management
- Technical indicators (RSI, MACD)
- Responsive design for all devices

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
pip install -r api/requirements.txt
```

## Development

Run the development server:
```bash
npm run dev
```

This will start both:
- Angular frontend at `http://localhost:4200`
- Python API at `http://localhost:5000`

## Project Structure

```
├── api/                    # Python backend
│   ├── app.py             # Flask application
│   └── requirements.txt    # Python dependencies
├── src/                    # Angular frontend
│   ├── app/               # Application components
│   │   ├── features/      # Feature modules
│   │   └── shared/        # Shared components
│   └── assets/            # Static assets
└── package.json           # Node.js dependencies
```

## Technologies

- Angular 19
- TailwindCSS
- Python Flask
- TradingView Technical Analysis Library
- Chart.js

## License

MIT