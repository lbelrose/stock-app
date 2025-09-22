import { Component, OnInit, OnDestroy, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Subject, takeUntil, tap } from 'rxjs';
import { StockService } from '../../shared/services/stock.service';
import { WatchlistService } from '../../shared/services/watchlist.service';
import { StockDetail, StockPrediction } from '../../shared/models/stock.model';
import { StockChartComponent } from './stock-chart/stock-chart.component';

@Component({
  selector: 'app-stock-detail',
  standalone: true,
  imports: [CommonModule, StockChartComponent, RouterLink],
  templateUrl: './stock-detail.component.html',
  styleUrls: ['./stock-detail.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class StockDetailComponent implements OnInit, OnDestroy {
  symbol = signal('');
  stock = signal<StockDetail | null>(null);
  prediction = signal<StockPrediction | null>(null);
  predictionMessage = signal<string | null>(null);
  loading = signal(true);
  trainingLoading = signal(false); // New loading state for training
  error = signal('');
  isInWatchlist = signal(false);
  
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
        this.symbol.set(symbol);
        this.loadStockData(symbol);
      } else {
        this.error.set('Stock symbol not provided');
        this.loading.set(false);
      }
    });
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  
  loadStockData(symbol: string): void {
    this.loading.set(true);
    this.error.set('');
    this.prediction.set(null);
    this.predictionMessage.set(null);
    
    this.stockService.getStockDetail(symbol).pipe(
      takeUntil(this.destroy$),
      tap(() => {
        this.stockService.getPrediction(symbol).pipe(
          takeUntil(this.destroy$)
        ).subscribe(response => {
          if (response.status && (response.status === 'training_started' || response.status === 'training_in_progress')) {
            this.predictionMessage.set(response.message);
            this.prediction.set(null);
          } else {
            this.prediction.set(response);
            this.predictionMessage.set(null);
          }
        });
      })
    ).subscribe({
      next: (data) => {
        this.stock.set(data);
        this.isInWatchlist.set(this.watchlistService.isInWatchlist(symbol));
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(`Failed to load data for ${symbol}. ${err.message}`);
        this.loading.set(false);
      }
    });
  }

  triggerModelTraining(): void {
    const symbol = this.symbol();
    if (!symbol) return;

    this.trainingLoading.set(true);
    this.predictionMessage.set('Training model...');
    this.error.set('');

    this.stockService.trainModel(symbol).pipe(
      takeUntil(this.destroy$)
    ).subscribe({
      next: (response) => {
        this.predictionMessage.set(response.message);
        this.trainingLoading.set(false);
        // Optionally, reload prediction after a delay to check for new model
        setTimeout(() => this.loadStockData(symbol), 5000); 
      },
      error: (err) => {
        this.error.set(`Failed to trigger model training: ${err.message}`);
        this.trainingLoading.set(false);
        this.predictionMessage.set(null);
      }
    });
  }
  
  toggleWatchlist(): void {
    const currentStock = this.stock();
    if (!currentStock) return;
    
    if (this.isInWatchlist()) {
      this.watchlistService.removeFromWatchlist(currentStock.symbol);
    } else {
      this.watchlistService.addToWatchlist(currentStock);
    }
    this.isInWatchlist.update(value => !value);
  }
  
  getRecommendationClass(recommendation: string): string {
    if (recommendation === 'STRONG_BUY' || recommendation === 'BUY') {
      return 'badge-positive';
    } else if (recommendation === 'STRONG_SELL' || recommendation === 'SELL') {
      return 'badge-negative';
    } else {
      return 'bg-neutral-100 text-neutral-700';
    }
  }

  getPredictionClass(signal: string): string {
    if (signal === 'BUY') {
      return 'badge-positive';
    } else if (signal === 'SELL') {
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
