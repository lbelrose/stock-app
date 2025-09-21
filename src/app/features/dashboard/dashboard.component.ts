import { Component, OnInit, HostListener, signal, ChangeDetectionStrategy } from '@angular/core';
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
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DashboardComponent implements OnInit {
  stocks = signal<StockDetail[]>([]);
  loading = signal(true);
  error = signal('');
  currentExchange = signal<'nasdaq' | 'cac40'>('nasdaq');
  currentPage = signal(1);
  pageSize: number = 9; // Adjust based on your desired number of cards per load
  isLoadingMore = signal(false);
  hasMoreStocks = signal(true);
  allStocksLoaded = signal(false);
  
  constructor(private stockService: StockService, private marketService: MarketService) {}
  
  ngOnInit(): void {
    const savedExchange = localStorage.getItem('dashboardExchangePreference');
    if (savedExchange === 'nasdaq' || savedExchange === 'cac40') {
      this.currentExchange.set(savedExchange);
    }
    this.loadStocks();
  }

  @HostListener('window:scroll', ['$event'])
  onScroll(event: any): void {
    // Check if user is near the bottom of the page
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 500 && !this.isLoadingMore() && this.hasMoreStocks()) {
      this.loadStocks(true);
    }
  }

  switchExchange(exchange: 'nasdaq' | 'cac40'): void {
    this.currentExchange.set(exchange);
    localStorage.setItem('dashboardExchangePreference', exchange);
    this.currentPage.set(1);
    this.stocks.set([]); // Clear existing stocks
    this.hasMoreStocks.set(true);
    this.allStocksLoaded.set(false);
    this.loadStocks();
  }
  
  loadStocks(isScrolling: boolean = false): void {
    if (!this.hasMoreStocks() || this.isLoadingMore()) {
      return;
    }

    if (isScrolling) {
      this.isLoadingMore.set(true);
    } else {
      this.loading.set(true);
      this.error.set('');
    }
    
    this.marketService.getStocks(this.currentExchange().toUpperCase(), this.currentPage(), this.pageSize).pipe(
      catchError(() => {
        this.error.set('Failed to load stock list. Please try again later.');
        this.loading.set(false);
        this.isLoadingMore.set(false);
        this.hasMoreStocks.set(false);
        return of([]);
      })
    ).subscribe(stocks => {
      if (stocks.length === 0) {
        this.hasMoreStocks.set(false);
        this.allStocksLoaded.set(true);
        this.loading.set(false);
        this.isLoadingMore.set(false);
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
          this.error.set('Failed to load stock details. Please try again later.');
          this.loading.set(false);
          this.isLoadingMore.set(false);
          this.hasMoreStocks.set(false);
          return of([]);
        })
      ).subscribe(stockDetails => {
        this.stocks.update(currentStocks => [...currentStocks, ...stockDetails]);
        this.currentPage.update(page => page + 1);
        this.hasMoreStocks.set(stockDetails.length === this.pageSize);
        this.allStocksLoaded.set(!this.hasMoreStocks());
        this.loading.set(false);
        this.isLoadingMore.set(false);
      });
    });
  }
}