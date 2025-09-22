import { Component, Input, OnChanges, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { StockDetail } from '../../models/stock.model';
import { WatchlistService } from '../../services/watchlist.service';

@Component({
  selector: 'app-stock-card',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './stock-card.component.html',
  styleUrls: ['./stock-card.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class StockCardComponent implements OnChanges {
  @Input({ required: true }) stock!: StockDetail;
  isInWatchlist = signal(false);
  
  constructor(private watchlistService: WatchlistService) {}
  
  ngOnChanges(): void {
    this.checkWatchlistStatus();
  }
  
  checkWatchlistStatus(): void {
    this.isInWatchlist.set(this.watchlistService.isInWatchlist(this.stock.symbol));
  }
  
  toggleWatchlist(): void {
    if (this.isInWatchlist()) {
      this.watchlistService.removeFromWatchlist(this.stock.symbol);
    } else {
      this.watchlistService.addToWatchlist(this.stock);
    }
    this.isInWatchlist.update(value => !value);
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