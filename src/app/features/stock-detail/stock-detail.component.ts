import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { StockService } from '../../shared/services/stock.service';
import { WatchlistService } from '../../shared/services/watchlist.service';
import { StockDetail } from '../../shared/models/stock.model';
import { StockChartComponent } from './stock-chart/stock-chart.component';

@Component({
  selector: 'app-stock-detail',
  standalone: true,
  imports: [CommonModule, StockChartComponent],
  template: `
    <div class="mb-6">
      <div class="flex items-center gap-2 text-neutral-500 mb-2">
        <a routerLink="/" class="hover:text-primary-600 transition-colors">Dashboard</a>
        <span>›</span>
        <span>{{ symbol }}</span>
      </div>
    </div>
    
    @if (loading) {
      <div class="animate-pulse space-y-6">
        <div class="h-8 bg-neutral-100 rounded w-1/4"></div>
        <div class="h-16 bg-neutral-100 rounded w-1/3"></div>
        <div class="h-80 bg-neutral-100 rounded w-full"></div>
        <div class="h-12 bg-neutral-100 rounded w-full"></div>
      </div>
    } @else if (error) {
      <div class="p-4 bg-negative-50 border border-negative-200 rounded-md text-negative-700">
        {{ error }}
      </div>
    } @else if (stock) {
      <div class="bg-white rounded-lg shadow-md p-6 mb-8 animate-fade-in">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h1 class="text-3xl font-bold mb-1">{{ stock.name }}</h1>
            <p class="text-neutral-600">{{ stock.symbol }}</p>
          </div>
          <button (click)="toggleWatchlist()" class="btn" [ngClass]="isInWatchlist ? 'btn-primary' : 'btn-secondary'">
            <span class="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              {{ isInWatchlist ? 'In Watchlist' : 'Add to Watchlist' }}
            </span>
          </button>
        </div>
        
        <div class="flex items-baseline gap-3 mb-8">
          <span class="text-4xl font-bold">{{ stock.close | number:'1.2-2' }}€</span>
          <span [ngClass]="stock.change >= 0 ? 'price-up' : 'price-down'" class="text-xl font-medium">
            {{ stock.change | number:'1.2-2' }}%
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              @if (stock.change >= 0) {
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              } @else {
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              }
            </svg>
          </span>
        </div>
        
        <app-stock-chart [stock]="stock"></app-stock-chart>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mt-8">
          <div class="bg-neutral-50 p-4 rounded-lg">
            <p class="text-neutral-500 text-sm mb-1">Open</p>
            <p class="text-xl font-medium">{{ stock.open | number:'1.2-2' }}€</p>
          </div>
          <div class="bg-neutral-50 p-4 rounded-lg">
            <p class="text-neutral-500 text-sm mb-1">High</p>
            <p class="text-xl font-medium">{{ stock.high | number:'1.2-2' }}€</p>
          </div>
          <div class="bg-neutral-50 p-4 rounded-lg">
            <p class="text-neutral-500 text-sm mb-1">Low</p>
            <p class="text-xl font-medium">{{ stock.low | number:'1.2-2' }}€</p>
          </div>
          <div class="bg-neutral-50 p-4 rounded-lg">
            <p class="text-neutral-500 text-sm mb-1">Volume</p>
            <p class="text-xl font-medium">{{ formatVolume(stock.volume) }}</p>
          </div>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-3 gap-6 mt-6">
          <div class="bg-neutral-50 p-4 rounded-lg">
            <p class="text-neutral-500 text-sm mb-1">RSI</p>
            <p class="text-xl font-medium">{{ stock.rsi | number:'1.1-1' }}</p>
            <p class="text-neutral-500 text-xs mt-1">
              @if (stock.rsi > 70) {
                Overbought
              } @else if (stock.rsi < 30) {
                Oversold
              } @else {
                Neutral
              }
            </p>
          </div>
          <div class="bg-neutral-50 p-4 rounded-lg">
            <p class="text-neutral-500 text-sm mb-1">MACD</p>
            <p class="text-xl font-medium">{{ stock.macd | number:'1.2-2' }}</p>
          </div>
          <div class="bg-neutral-50 p-4 rounded-lg">
            <p class="text-neutral-500 text-sm mb-1">Recommendation</p>
            <span [ngClass]="getRecommendationClass()" class="badge text-sm px-3 py-1">
              {{ formatRecommendation(stock.recommendation) }}
            </span>
          </div>
        </div>
      </div>
    }
  `
})
export class StockDetailComponent implements OnInit, OnDestroy {
  symbol = '';
  stock: StockDetail | null = null;
  loading = true;
  error = '';
  isInWatchlist = false;
  
  private destroy$ = new Subject<void>();
  
  constructor(
    private route: ActivatedRoute,
    private stockService: StockService,
    private watchlistService: WatchlistService
  ) {}
  
  ngOnInit(): void {
    this.route.paramMap.pipe(
      takeUntil(this.destroy$)
    ).subscribe(params => {
      const symbol = params.get('symbol');
      if (symbol) {
        this.symbol = symbol;
        this.loadStockData(symbol);
      } else {
        this.error = 'Stock symbol not provided';
        this.loading = false;
      }
    });
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  
  loadStockData(symbol: string): void {
    this.loading = true;
    this.error = '';
    
    this.stockService.getStockDetail(symbol).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (data) => {
        this.stock = data;
        this.isInWatchlist = this.watchlistService.isInWatchlist(symbol);
        this.loading = false;
      },
      error: (err) => {
        this.error = `Failed to load data for ${symbol}. ${err.message}`;
        this.loading = false;
      }
    });
  }
  
  toggleWatchlist(): void {
    if (!this.stock) return;
    
    if (this.isInWatchlist) {
      this.watchlistService.removeFromWatchlist(this.stock.symbol);
    } else {
      this.watchlistService.addToWatchlist(this.stock);
    }
    this.isInWatchlist = !this.isInWatchlist;
  }
  
  getRecommendationClass(): string {
    if (!this.stock) return '';
    
    const rec = this.stock.recommendation;
    if (rec === 'STRONG_BUY' || rec === 'BUY') {
      return 'badge-positive';
    } else if (rec === 'STRONG_SELL' || rec === 'SELL') {
      return 'badge-negative';
    } else {
      return 'bg-neutral-100 text-neutral-700';
    }
  }
  
  formatRecommendation(rec: string): string {
    return rec.replace('_', ' ');
  }
  
  formatVolume(volume: number): string {
    if (volume >= 1000000) {
      return (volume / 1000000).toFixed(1) + 'M';
    } else if (volume >= 1000) {
      return (volume / 1000).toFixed(1) + 'K';
    }
    return volume.toString();
  }
}