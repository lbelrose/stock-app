import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { StockDetail } from '../models/stock.model';

@Injectable({
  providedIn: 'root'
})
export class WatchlistService {
  private watchlistKey = 'nasdaq_stock_watchlist';
  private watchlistSubject = new BehaviorSubject<StockDetail[]>([]);
  
  constructor() {
    this.loadWatchlist();
  }
  
  get watchlist$(): Observable<StockDetail[]> {
    return this.watchlistSubject.asObservable();
  }
  
  private loadWatchlist(): void {
    try {
      const storedWatchlist = localStorage.getItem(this.watchlistKey);
      if (storedWatchlist) {
        const watchlist = JSON.parse(storedWatchlist);
        this.watchlistSubject.next(watchlist);
      }
    } catch (error) {
      console.error('Error loading watchlist:', error);
      this.watchlistSubject.next([]);
    }
  }
  
  private saveWatchlist(watchlist: StockDetail[]): void {
    try {
      localStorage.setItem(this.watchlistKey, JSON.stringify(watchlist));
      this.watchlistSubject.next(watchlist);
    } catch (error) {
      console.error('Error saving watchlist:', error);
    }
  }
  
  addToWatchlist(stock: StockDetail): void {
    const currentWatchlist = this.watchlistSubject.getValue();
    
    if (!this.isInWatchlist(stock.symbol)) {
      const updatedWatchlist = [...currentWatchlist, stock];
      this.saveWatchlist(updatedWatchlist);
    }
  }
  
  removeFromWatchlist(symbol: string): void {
    const currentWatchlist = this.watchlistSubject.getValue();
    const updatedWatchlist = currentWatchlist.filter(item => item.symbol !== symbol);
    this.saveWatchlist(updatedWatchlist);
  }
  
  isInWatchlist(symbol: string): boolean {
    const currentWatchlist = this.watchlistSubject.getValue();
    return currentWatchlist.some(item => item.symbol === symbol);
  }
}