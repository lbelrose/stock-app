import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { StockSearchComponent } from '../stock-search/stock-search.component';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, StockSearchComponent],
  template: `
    <header class="bg-white shadow-sm">
      <div class="container mx-auto px-4 py-4">
        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
          <div class="flex items-center">
            <a routerLink="/" class="text-2xl font-bold text-primary-600">
              Nasdaq Stock Tracker
            </a>
          </div>
          
          <app-stock-search class="w-full md:w-96"></app-stock-search>
          
          <nav class="flex items-center space-x-6">
            <a routerLink="/" routerLinkActive="text-primary-600 font-medium" [routerLinkActiveOptions]="{exact: true}" class="text-neutral-700 hover:text-primary-600 transition-colors">
              Dashboard
            </a>
            <a routerLink="/watchlist" routerLinkActive="text-primary-600 font-medium" class="text-neutral-700 hover:text-primary-600 transition-colors">
              Watchlist
            </a>
          </nav>
        </div>
      </div>
    </header>
  `
})
export class HeaderComponent {}