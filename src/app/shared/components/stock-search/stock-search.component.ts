import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, debounceTime, distinctUntilChanged, switchMap, takeUntil } from 'rxjs';

import { StockService } from '../../services/stock.service';
import { Stock } from '../../models/stock.model';

@Component({
  selector: 'app-stock-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="relative">
      <div class="relative">
        <input
          type="text"
          [(ngModel)]="searchQuery"
          (input)="search()"
          placeholder="Search stocks..."
          class="input pr-10"
        />
        <span class="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-400">
          <!-- Simple search icon -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
      </div>
      
      <!-- Search results dropdown -->
      @if (showResults && searchResults.length > 0) {
        <div class="absolute z-10 mt-1 w-full bg-white rounded-md shadow-lg max-h-96 overflow-y-auto animate-fade-in">
          <ul class="py-1">
            @for (stock of searchResults; track stock.symbol) {
              <li (click)="selectStock(stock)" class="px-4 py-2 hover:bg-neutral-100 cursor-pointer transition-colors">
                <div class="font-medium">{{ stock.symbol }}</div>
                <div class="text-sm text-neutral-600">{{ stock.name }}</div>
              </li>
            }
          </ul>
        </div>
      }
    </div>
  `
})
export class StockSearchComponent implements OnInit, OnDestroy {
  searchQuery = '';
  searchResults: Stock[] = [];
  showResults = false;
  
  private searchSubject = new Subject<string>();
  private destroy$ = new Subject<void>();
  
  constructor(
    private stockService: StockService,
    private router: Router
  ) {}
  
  ngOnInit(): void {
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(query => this.stockService.searchStocks(query)),
      takeUntil(this.destroy$)
    ).subscribe(results => {
      this.searchResults = results;
      this.showResults = true;
    });
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  
  search(): void {
    if (this.searchQuery.length > 1) {
      this.searchSubject.next(this.searchQuery);
    } else {
      this.searchResults = [];
      this.showResults = false;
    }
  }
  
  selectStock(stock: Stock): void {
    this.searchQuery = '';
    this.searchResults = [];
    this.showResults = false;
    this.router.navigate(['/stock', stock.symbol]);
  }
}