import { Component, Input, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { StockDetail } from '../../models/stock.model';
import { WatchlistService } from '../../services/watchlist.service';

@Component({
  selector: 'app-stock-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="card animate-slide-up">
      <div class="flex justify-between items-start mb-2">
        <div>
          <h3 class="text-xl font-semibold mb-0">
            <a [routerLink]="['/stock', stock.symbol]" class="hover:text-primary-600 transition-colors">
              {{ stock.symbol }}
            </a>
          </h3>
          <p class="text-neutral-600 text-sm">{{ stock.name }}</p>
        </div>
        <button (click)="toggleWatchlist()" class="text-neutral-400 hover:text-primary-500 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" [class.text-primary-500]="isInWatchlist" fill="currentColor" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        </button>
      </div>
      
      <div class="flex justify-between items-end">
        <div>
          <span class="text-2xl font-medium">{{ stock.close | number:'1.2-2' }}€</span>
          <div class="flex items-center mt-1">
            <span [ngClass]="stock.change >= 0 ? 'price-up' : 'price-down'" class="font-medium">
              {{ stock.change | number:'1.2-2' }}%
            </span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" [ngClass]="stock.change >= 0 ? 'price-up' : 'price-down'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              @if (stock.change >= 0) {
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              } @else {
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              }
            </svg>
          </div>
        </div>
        
        <div class="text-right">
          <span [ngClass]="getRecommendationClass()" class="badge">
            {{ stock.recommendation }}
          </span>
          <p class="text-sm text-neutral-500 mt-1">Vol: {{ formatVolume(stock.volume) }}</p>
        </div>
      </div>
      
      <div class="grid grid-cols-2 gap-3 mt-4 text-sm">
        <div>
          <span class="text-neutral-500">Open</span>
          <p>{{ stock.open | number:'1.2-2' }}€</p>
        </div>
        <div>
          <span class="text-neutral-500">High</span>
          <p>{{ stock.high | number:'1.2-2' }}€</p>
        </div>
        <div>
          <span class="text-neutral-500">Low</span>
          <p>{{ stock.low | number:'1.2-2' }}€</p>
        </div>
        <div>
          <span class="text-neutral-500">RSI</span>
          <p>{{ stock.rsi | number:'1.1-1' }}</p>
        </div>
      </div>
    </div>
  `
})
export class StockCardComponent implements OnChanges {
  @Input() stock!: StockDetail;
  isInWatchlist = false;
  
  constructor(private watchlistService: WatchlistService) {}
  
  ngOnChanges(): void {
    this.checkWatchlistStatus();
  }
  
  checkWatchlistStatus(): void {
    this.isInWatchlist = this.watchlistService.isInWatchlist(this.stock.symbol);
  }
  
  toggleWatchlist(): void {
    if (this.isInWatchlist) {
      this.watchlistService.removeFromWatchlist(this.stock.symbol);
    } else {
      this.watchlistService.addToWatchlist(this.stock);
    }
    this.isInWatchlist = !this.isInWatchlist;
  }
  
  getRecommendationClass(): string {
    const rec = this.stock.recommendation;
    if (rec === 'STRONG_BUY' || rec === 'BUY') {
      return 'badge-positive';
    } else if (rec === 'STRONG_SELL' || rec === 'SELL') {
      return 'badge-negative';
    } else {
      return 'bg-neutral-100 text-neutral-700';
    }
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