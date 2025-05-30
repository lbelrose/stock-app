import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';
import { WatchlistService } from '../../shared/services/watchlist.service';
import { StockCardComponent } from '../../shared/components/stock-card/stock-card.component';
import { StockDetail } from '../../shared/models/stock.model';

@Component({
  selector: 'app-watchlist',
  standalone: true,
  imports: [CommonModule, StockCardComponent],
  template: `
    <div class="mb-8">
      <h1 class="text-3xl font-bold">Your Watchlist</h1>
      <p class="text-neutral-600">Track your favorite stocks from the Paris Stock Exchange.</p>
    </div>
    
    @if (watchlist.length > 0) {
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        @for (stock of watchlist; track stock.symbol) {
          <app-stock-card [stock]="stock"></app-stock-card>
        }
      </div>
    } @else {
      <div class="bg-white rounded-lg shadow-md p-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-neutral-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
        </svg>
        <h2 class="text-2xl font-semibold mb-2">Your watchlist is empty</h2>
        <p class="text-neutral-600 mb-6">Add stocks to your watchlist to track them here.</p>
        <a routerLink="/" class="btn btn-primary">Explore Stocks</a>
      </div>
    }
  `
})
export class WatchlistComponent implements OnInit, OnDestroy {
  watchlist: StockDetail[] = [];
  
  private destroy$ = new Subject<void>();
  
  constructor(private watchlistService: WatchlistService) {}
  
  ngOnInit(): void {
    this.watchlistService.watchlist$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(watchlist => {
      this.watchlist = watchlist;
    });
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}