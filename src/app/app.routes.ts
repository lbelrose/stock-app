import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent)
  },
  {
    path: 'stock/:symbol',
    loadComponent: () => import('./features/stock-detail/stock-detail.component').then(m => m.StockDetailComponent)
  },
  {
    path: 'watchlist',
    loadComponent: () => import('./features/watchlist/watchlist.component').then(m => m.WatchlistComponent)
  },
  {
    path: '**',
    redirectTo: ''
  }
];