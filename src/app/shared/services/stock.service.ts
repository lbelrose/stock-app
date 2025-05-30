import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, catchError, map, tap } from 'rxjs';
import { Stock, StockDetail } from '../models/stock.model';

@Injectable({
  providedIn: 'root'
})
export class StockService {
  private apiUrl = 'http://localhost:5000/api';
  private cachedStocks: Map<string, StockDetail> = new Map();
  
  constructor(private http: HttpClient) {}
  
  searchStocks(query: string): Observable<Stock[]> {
    return this.http.get<Stock[]>(`${this.apiUrl}/search?q=${query}`).pipe(
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
    
    return this.http.get<StockDetail>(`${this.apiUrl}/stock/${symbol}`).pipe(
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
  
  getDefaultStocks(): Observable<Stock[]> {
    return this.searchStocks('');
  }
}