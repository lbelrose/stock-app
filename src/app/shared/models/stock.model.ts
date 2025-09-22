export interface Stock {
  symbol: string;
  name: string;
}

export interface StockDetail extends Stock {
  close: number;
  open: number;
  high: number;
  low: number;
  volume: number;
  change: number;
  recommendation: string;
  rsi: number;
  macd: number;
  timestamp?: number;
}

export interface StockPrediction {
  ticker: string;
  signal: 'BUY' | 'SELL' | 'HOLD' | 'ERROR';
  confidence: string;
  probability_up: number;
  probability_down: number;
  buy_threshold: number;
  model_type: string;
  timestamp: number;
}
