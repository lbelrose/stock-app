import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, catchError } from 'rxjs';
import { Stock } from '../models/stock.model';

@Injectable({
  providedIn: 'root'
})
export class MarketService {
  private apiUrl = 'http://localhost:5000/api';

  constructor(private http: HttpClient) { }

  getStocks(market: string, page: number = 1, limit: number = 20): Observable<Stock[]> {
    return this.http.get<Stock[]>(`${this.apiUrl}/markets/${market}?page=${page}&limit=${limit}`).pipe(
      catchError(() => of([]))
    );
  }
}
