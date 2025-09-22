import { Component, OnInit, OnDestroy, signal, ChangeDetectionStrategy } from '@angular/core';
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
  templateUrl: './stock-search.component.html',
  styleUrls: ['./stock-search.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class StockSearchComponent implements OnInit, OnDestroy {
  searchQuery = signal('');
  searchResults = signal<Stock[]>([]);
  showResults = signal(false);
  
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
      this.searchResults.set(results);
      this.showResults.set(true);
    });
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  
  search(): void {
    if (this.searchQuery().length > 1) {
      this.searchSubject.next(this.searchQuery());
    } else {
      this.searchResults.set([]);
      this.showResults.set(false);
    }
  }
  
  selectStock(stock: Stock): void {
    this.searchQuery.set('');
    this.searchResults.set([]);
    this.showResults.set(false);
    this.router.navigate(['/stock', stock.symbol]);
  }
}