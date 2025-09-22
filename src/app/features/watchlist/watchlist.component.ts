import { Component, OnInit, OnDestroy, signal, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';
import { WatchlistService } from '../../shared/services/watchlist.service';
import { StockCardComponent } from '../../shared/components/stock-card/stock-card.component';
import { StockDetail } from '../../shared/models/stock.model';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-watchlist',
  standalone: true,
  imports: [CommonModule, StockCardComponent, RouterLink],
  templateUrl: './watchlist.component.html',
  styleUrls: ['./watchlist.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class WatchlistComponent implements OnInit, OnDestroy {
  watchlist = signal<StockDetail[]>([]);
  
  private destroy$ = new Subject<void>();
  
  constructor(private watchlistService: WatchlistService) {}
  
  ngOnInit(): void {
    this.watchlistService.watchlist$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(watchlist => {
      this.watchlist.set(watchlist);
    });
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
