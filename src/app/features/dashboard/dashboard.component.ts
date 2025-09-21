import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StockService } from '../../shared/services/stock.service';
import { MarketService } from '../../shared/services/market.service';
import { StockCardComponent } from '../../shared/components/stock-card/stock-card.component';
import { StockDetail } from '../../shared/models/stock.model';
import { catchError, forkJoin, map, of } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, StockCardComponent],
  template: `
    <div class="mb-8">
      <h1 class="text-3xl font-bold">{{ currentExchange === 'nasdaq' ? 'Nasdaq Stock Exchange' : 'CAC40 Stock Exchange' }}</h1>
      <p class="text-neutral-600">Track the latest stock movements.</p>
    </div>

    <div class="mb-4">
      <button (click)="switchExchange('nasdaq')" 
              [ngClass]="{'bg-primary-500 text-white': currentExchange === 'nasdaq', 'bg-white': currentExchange !== 'nasdaq'}"
              class="px-4 py-2 rounded-md mr-2">
        NASDAQ
      </button>
      <button (click)="switchExchange('cac40')" 
              [ngClass]="{'bg-primary-500 text-white': currentExchange === 'cac40', 'bg-white': currentExchange !== 'cac40'}"
              class="px-4 py-2 rounded-md">
        CAC40
      </button>
    </div>
    
    @if (loading && stocks.length === 0) {
      <div class="flex justify-center items-center py-12">
        <div class="animate-pulse flex flex-col items-center">
          <div class="h-12 w-12 rounded-full bg-primary-200 mb-3"></div>
          <div class="h-4 w-24 bg-primary-100 rounded"></div>
        </div>
      </div>
    } @else if (error) {
      <div class="p-4 bg-negative-50 border border-negative-200 rounded-md text-negative-700">
        {{ error }}
      </div>
    } @else {
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        @for (stock of stocks; track stock.symbol) {
          <app-stock-card [stock]="stock"></app-stock-card>
        } @empty {
          <div class="col-span-full text-center py-12 text-neutral-500">
            No stocks found.
          </div>
        }
      </div>
      @if (isLoadingMore) {
        <div class="flex justify-center items-center py-6">
          <div class="animate-pulse flex flex-col items-center">
            <div class="h-8 w-8 rounded-full bg-primary-200 mb-2"></div>
            <div class="h-3 w-16 bg-primary-100 rounded"></div>
          </div>
        </div>
      } @else if (allStocksLoaded && stocks.length > 0) {
        <div class="col-span-full text-center py-6 text-neutral-500">
          Toutes les actions ont été chargées.
        </div>
      }
    }
  `
})
export class DashboardComponent implements OnInit {
  stocks: StockDetail[] = [];
  loading = true;
  error = '';
  currentExchange: 'nasdaq' | 'cac40' = 'nasdaq';
  currentPage: number = 1;
  pageSize: number = 9; // Adjust based on your desired number of cards per load
  isLoadingMore = false;
  hasMoreStocks = true;
  allStocksLoaded = false;
  
  constructor(private stockService: StockService, private marketService: MarketService) {}
  
  ngOnInit(): void {
    const savedExchange = localStorage.getItem('dashboardExchangePreference');
    if (savedExchange === 'nasdaq' || savedExchange === 'cac40') {
      this.currentExchange = savedExchange;
    }
    this.loadStocks();
  }

  @HostListener('window:scroll', ['$event'])
  onScroll(event: any): void {
    // Check if user is near the bottom of the page
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 500 && !this.isLoadingMore && this.hasMoreStocks) {
      this.loadStocks(true);
    }
  }

  switchExchange(exchange: 'nasdaq' | 'cac40'): void {
    this.currentExchange = exchange;
    localStorage.setItem('dashboardExchangePreference', exchange);
    this.currentPage = 1;
    this.stocks = []; // Clear existing stocks
    this.hasMoreStocks = true;
    this.allStocksLoaded = false;
    this.loadStocks();
  }
  
  loadStocks(isScrolling: boolean = false): void {
    if (!this.hasMoreStocks || this.isLoadingMore) {
      return;
    }

    if (isScrolling) {
      this.isLoadingMore = true;
    } else {
      this.loading = true;
      this.error = '';
    }
    
    this.marketService.getStocks(this.currentExchange.toUpperCase(), this.currentPage, this.pageSize).pipe(
      catchError(() => {
        this.error = 'Failed to load stock list. Please try again later.';
        this.loading = false;
        this.isLoadingMore = false;
        this.hasMoreStocks = false;
        return of([]);
      })
    ).subscribe(stocks => {
      if (stocks.length === 0) {
        this.hasMoreStocks = false;
        this.allStocksLoaded = true;
        this.loading = false;
        this.isLoadingMore = false;
        return;
      }
      
      const stockRequests = stocks.map(stock => 
        this.stockService.getStockDetail(stock.symbol).pipe(
          catchError(() => of(null))
        )
      );
      
      forkJoin(stockRequests).pipe(
        map(results => results.filter(stock => stock !== null) as StockDetail[]),
        catchError(() => {
          this.error = 'Failed to load stock details. Please try again later.';
          this.loading = false;
          this.isLoadingMore = false;
          this.hasMoreStocks = false;
          return of([]);
        })
      ).subscribe(stockDetails => {
        this.stocks = [...this.stocks, ...stockDetails];
        this.currentPage++;
        this.hasMoreStocks = stockDetails.length === this.pageSize;
        this.allStocksLoaded = !this.hasMoreStocks;
        this.loading = false;
        this.isLoadingMore = false;
      });
    });
  }
}