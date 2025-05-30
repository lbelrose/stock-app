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