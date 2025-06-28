import { Component, Input, OnChanges, ViewChild, ElementRef } from '@angular/core';
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
  template: `
    <div class="mt-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-semibold">Price Chart</h3>
        <div class="flex gap-2">
          <div class="flex gap-2">
            <button *ngFor="let period of periods" 
                    (click)="setPeriod(period.value)"
                    [ngClass]="selectedPeriod === period.value ? 'bg-primary-100 text-primary-700' : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'"
                    class="px-3 py-1 rounded-md text-sm font-medium transition-colors">
              {{ period.label }}
            </button>
          </div>
          <div class="flex gap-2">
            <button *ngFor="let interval of intervals" 
                    (click)="setInterval(interval.value)"
                    [ngClass]="selectedInterval === interval.value ? 'bg-primary-100 text-primary-700' : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'"
                    class="px-3 py-1 rounded-md text-sm font-medium transition-colors">
              {{ interval.label }}
            </button>
          </div>
        </div>
      </div>
      
      <div class="chart-container">
        <canvas #chartCanvas></canvas>
      </div>
    </div>
  `
})
export class StockChartComponent implements OnChanges {
  @Input() stock!: StockDetail;
  @ViewChild('chartCanvas', { static: true }) chartCanvas!: ElementRef;
  
  private chart: Chart | null = null;
  private historicalData: any[] = [];
  
  periods = [
    { label: '1D', value: '1d' },
    { label: '7D', value: '7d' },
    { label: '1M', value: '1mo' },
    { label: '1Y', value: '1y' }
  ];

  intervals = [
    { label: '1m', value: '1m' },
    { label: '5m', value: '5m' },
    { label: '15m', value: '15m' },
    { label: '30m', value: '30m' },
    { label: '1h', value: '1h' }
  ];
  
  selectedPeriod = '1d'; 
  selectedInterval = '15m'; 
  
  constructor(private stockService: StockService) {}
  
  ngOnChanges(): void {
    if (this.stock) {
      this.fetchAndCreateChart();
    }
  }
  
  setPeriod(period: string): void {
    this.selectedPeriod = period;
    this.fetchAndCreateChart();
  }

  setInterval(interval: string): void {
    this.selectedInterval = interval;
    this.fetchAndCreateChart();
  }
  
  private fetchAndCreateChart(): void {
    if (!this.stock) return;

    this.stockService.getStockHistory(this.stock.symbol, this.selectedPeriod, this.selectedInterval).subscribe({
      next: (data) => {
        this.historicalData = data;
        this.createChart();
      },
      error: (err) => {
        console.error(`Error fetching historical data for ${this.stock.symbol} with period ${this.selectedPeriod} and interval ${this.selectedInterval}:`, err);
        this.historicalData = []; // Clear data on error
        this.createChart(); // Re-create chart with empty data
      }
    });
  }
  
  private createChart(): void {
    if (!this.stock) return;
    
    // If chart already exists, destroy it
    if (this.chart) {
      this.chart.destroy();
    }
    
    // Get the context for the chart
    const ctx = this.chartCanvas.nativeElement.getContext('2d');
    
    // Determine labels and data based on historicalData and selectedInterval
    let labels: string[] = [];
    let data: number[] = [];

    if (this.historicalData.length > 0) {
      labels = this.historicalData.map(item => {
        const date = new Date(item.datetime);
        if (this.selectedPeriod === '1d') {
          return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
        } else if (this.selectedPeriod === '7d' || this.selectedPeriod === '1mo') {
          return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
        } else if (this.selectedPeriod === '1y') {
          return date.toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' });
        }
        return date.toLocaleDateString('fr-FR'); // Default fallback
      });
      data = this.historicalData.map(item => item.close);
    }
    
    // Create the chart
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