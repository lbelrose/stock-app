import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StockService } from '../../shared/services/stock.service';
import { StockCardComponent } from '../../shared/components/stock-card/stock-card.component';
import { StockDetail } from '../../shared/models/stock.model';
import { catchError, forkJoin, map, of } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, StockCardComponent],
  template: `
    <div class="mb-8">
      <h1 class="text-3xl font-bold">Nasdaq Stock Exchange</h1>
      <p class="text-neutral-600">Track the latest stock movements from the Euronext Nasdaq exchange.</p>
    </div>
    
    @if (loading) {
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
            No stocks found. Try searching for a specific company.
          </div>
        }
      </div>
    }
  `
})
export class DashboardComponent implements OnInit {
  stocks: StockDetail[] = [];
  loading = true;
  error = '';
  
  constructor(private stockService: StockService) {}
  
  ngOnInit(): void {
    this.loadFeaturedStocks();
  }
  
  loadFeaturedStocks(): void {
    this.loading = true;
    this.error = '';
    
    // Get featured stock symbols
    this.stockService.getDefaultStocks().pipe(
      map(stocks => stocks.slice(0, 9)), // Limit to first 9 stocks
      catchError(() => {
        this.error = 'Failed to load stock list. Please try again later.';
        return of([]);
      })
    ).subscribe(stocks => {
      if (stocks.length === 0) {
        this.loading = false;
        return;
      }
      
      // Load details for each stock
      const stockRequests = stocks.map(stock => 
        this.stockService.getStockDetail(stock.symbol).pipe(
          catchError(() => of(null))
        )
      );
      
      forkJoin(stockRequests).pipe(
        map(results => results.filter(stock => stock !== null) as StockDetail[]),
        catchError(() => {
          this.error = 'Failed to load stock details. Please try again later.';
          return of([]);
        })
      ).subscribe(stockDetails => {
        this.stocks = stockDetails;
        this.loading = false;
      });
    });
  }
}