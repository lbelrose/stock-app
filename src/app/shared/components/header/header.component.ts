import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { StockSearchComponent } from '../stock-search/stock-search.component';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, StockSearchComponent],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {}