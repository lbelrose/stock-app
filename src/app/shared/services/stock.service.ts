import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, catchError, map, tap } from 'rxjs';
import { Stock, StockDetail, StockPrediction } from '../models/stock.model';

@Injectable({
  providedIn: 'root'
})
export class StockService {
  private apiUrl = 'http://localhost:5000/api';
  private cachedStocks: Map<string, StockDetail> = new Map();
  
  constructor(private http: HttpClient) {}
  
  searchStocks(query: string): Observable<Stock[]> {
    const urlQuery = query ? `?q=${query}` : '';
    return this.http.get<Stock[]>(`${this.apiUrl}/stocks/search${urlQuery}`).pipe(
      catchError(() => of([]))
    );
  }
  
  getStockDetail(symbol: string): Observable<StockDetail> {
    // Check cache first, but don't return cached data older than 5 minutes
    const cached = this.cachedStocks.get(symbol);
    const now = Date.now();
    
    if (cached && cached['timestamp'] && now - cached['timestamp'] < 5 * 60 * 1000) {
      return of(cached);
    }
    
    return this.http.get<StockDetail>(`${this.apiUrl}/stocks/${symbol}`).pipe(
      map(stock => ({
        ...stock,
        timestamp: Date.now() // Add timestamp for cache expiry check
      })),
      tap(stock => this.cachedStocks.set(symbol, stock)),
      catchError(error => {
        console.error(`Error fetching stock ${symbol}:`, error);
        throw new Error(`Unable to fetch data for ${symbol}`);
      })
    );
  }
  
  getMarketStocks(market: string): Observable<Stock[]> {
    return this.http.get<Stock[]>(`${this.apiUrl}/stocks/market/${market}`).pipe(
      catchError(() => of([]))
    );
  }

  getStockHistory(symbol: string, period: string = '1d', interval: string = '15m'): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/stocks/${symbol}/history?period=${period}&interval=${interval}`).pipe(
      catchError(error => {
        console.error(`Error fetching historical data for ${symbol}:`, error);
        throw new Error(`Unable to fetch historical data for ${symbol}`);
      })
    );
  }

  getPrediction(symbol: string): Observable<StockPrediction> {
    return this.http.get<StockPrediction>(`${this.apiUrl}/analysis/${symbol}`).pipe(
      catchError(error => {
        console.error(`Error fetching prediction for ${symbol}:`, error);
        // Return a default "error" prediction object
        return of({ 
          ticker: symbol, 
          signal: 'ERROR', 
          confidence: '0.00', 
          model_status: 'offline' 
        } as StockPrediction);
      })
    );
  }
}