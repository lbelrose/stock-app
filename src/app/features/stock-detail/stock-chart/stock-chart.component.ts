import { Component, Input, ViewChild, ElementRef, signal, effect, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { StockDetail } from '../../../shared/models/stock.model';
import { StockService } from '../../../shared/services/stock.service';

// Register Chart.js components
Chart.register(...registerables);

@Component({
  selector: 'app-stock-chart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './stock-chart.component.html',
  styleUrls: ['./stock-chart.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class StockChartComponent {
  @Input({ required: true }) stock!: StockDetail;
  @ViewChild('chartCanvas', { static: true }) chartCanvas!: ElementRef;
  
  private chart: Chart | null = null;
  
  readonly periods = [
    { label: '1D', value: '1d' },
    { label: '7D', value: '7d' },
    { label: '1M', value: '1mo' },
    { label: '1Y', value: '1y' }
  ];

  readonly intervals = [
    { label: '1m', value: '1m' },
    { label: '5m', value: '5m' },
    { label: '15m', value: '15m' },
    { label: '30m', value: '30m' },
    { label: '1h', value: '1h' }
  ];
  
  selectedPeriod = signal('1d'); 
  selectedInterval = signal('15m'); 
  
  constructor(private stockService: StockService) {
    effect(() => {
      const stock = this.stock;
      const period = this.selectedPeriod();
      const interval = this.selectedInterval();
      
      if (stock) {
        this.fetchAndCreateChart(stock.symbol, period, interval);
      }
    });
  }
  
  private fetchAndCreateChart(symbol: string, period: string, interval: string): void {
    this.stockService.getStockHistory(symbol, period, interval).subscribe({
      next: (data) => {
        this.createChart(data);
      },
      error: (err) => {
        console.error(`Error fetching historical data for ${symbol} with period ${period} and interval ${interval}:`, err);
        this.createChart([]); // Re-create chart with empty data
      }
    });
  }
  
  private createChart(historicalData: any[]): void {
    if (!this.stock) return;
    
    if (this.chart) {
      this.chart.destroy();
    }
    
    const ctx = this.chartCanvas.nativeElement.getContext('2d');
    
    let labels: string[] = [];
    let data: number[] = [];

    if (historicalData.length > 0) {
      labels = historicalData.map(item => {
        const date = new Date(item.datetime);
        const period = this.selectedPeriod();
        if (period === '1d') {
          return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
        } else if (period === '7d' || period === '1mo') {
          return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
        } else if (period === '1y') {
          return date.toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' });
        }
        return date.toLocaleDateString('fr-FR');
      });
      data = historicalData.map(item => item.close);
    }
    
    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: this.stock.symbol,
          data: data,
          borderColor: this.stock.change >= 0 ? '#36B37E' : '#FF5630',
          backgroundColor: this.stock.change >= 0 ? 'rgba(54, 179, 126, 0.1)' : 'rgba(255, 86, 48, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.3,
          pointRadius: 0,
          pointHoverRadius: 5,
          pointHitRadius: 10,
          pointHoverBackgroundColor: this.stock.change >= 0 ? '#36B37E' : '#FF5630',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: (context) => {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  label += new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(context.parsed.y);
                }
                return label;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              maxTicksLimit: 8,
              maxRotation: 0
            }
          },
          y: {
            position: 'right',
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
              callback: (value) => {
                return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', minimumFractionDigits: 2 }).format(value as number);
              }
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    });
  }
}
