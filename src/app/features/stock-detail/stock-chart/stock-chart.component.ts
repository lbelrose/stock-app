import { Component, Input, OnChanges, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { StockDetail } from '../../../shared/models/stock.model';

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
          <button *ngFor="let period of periods" 
                  (click)="setPeriod(period.value)"
                  [ngClass]="selectedPeriod === period.value ? 'bg-primary-100 text-primary-700' : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'"
                  class="px-3 py-1 rounded-md text-sm font-medium transition-colors">
            {{ period.label }}
          </button>
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
  
  // In a real application, we would fetch historical data for different time periods
  // For demo purposes, we'll generate random data
  periods = [
    { label: '1D', value: 'day' },
    { label: '1W', value: 'week' },
    { label: '1M', value: 'month' },
    { label: '3M', value: 'quarter' },
    { label: '1Y', value: 'year' }
  ];
  
  selectedPeriod = 'day';
  
  ngOnChanges(): void {
    this.createChart();
  }
  
  setPeriod(period: string): void {
    this.selectedPeriod = period;
    this.updateChartData();
  }
  
  private createChart(): void {
    if (!this.stock) return;
    
    // If chart already exists, destroy it
    if (this.chart) {
      this.chart.destroy();
    }
    
    // Get the context for the chart
    const ctx = this.chartCanvas.nativeElement.getContext('2d');
    
    // Create the chart
    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: this.generateTimeLabels(),
        datasets: [{
          label: this.stock.symbol,
          data: this.generatePriceData(),
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
  
  private updateChartData(): void {
    if (!this.chart) return;
    
    // Update chart data based on selected period
    this.chart.data.labels = this.generateTimeLabels();
    this.chart.data.datasets[0].data = this.generatePriceData();
    this.chart.update();
  }
  
  private generateTimeLabels(): string[] {
    // Generate time labels based on selected period
    const labels: string[] = [];
    const now = new Date();
    let format: Intl.DateTimeFormatOptions;
    let count: number;
    
    switch (this.selectedPeriod) {
      case 'day':
        format = { hour: '2-digit', minute: '2-digit' };
        count = 24;
        for (let i = 0; i < count; i++) {
          const date = new Date(now);
          date.setHours(date.getHours() - (count - i));
          labels.push(date.toLocaleTimeString('fr-FR', format));
        }
        break;
      case 'week':
        format = { weekday: 'short' };
        for (let i = 6; i >= 0; i--) {
          const date = new Date(now);
          date.setDate(date.getDate() - i);
          labels.push(date.toLocaleDateString('fr-FR', format));
        }
        break;
      case 'month':
        format = { day: '2-digit', month: 'short' };
        for (let i = 29; i >= 0; i--) {
          const date = new Date(now);
          date.setDate(date.getDate() - i);
          labels.push(date.toLocaleDateString('fr-FR', format));
        }
        break;
      case 'quarter':
        format = { day: '2-digit', month: 'short' };
        for (let i = 0; i < 3; i++) {
          for (let j = 1; j <= 30; j += 10) {
            const date = new Date(now);
            date.setMonth(date.getMonth() - 2 + i);
            date.setDate(j);
            labels.push(date.toLocaleDateString('fr-FR', format));
          }
        }
        break;
      case 'year':
        format = { month: 'short' };
        for (let i = 11; i >= 0; i--) {
          const date = new Date(now);
          date.setMonth(date.getMonth() - i);
          labels.push(date.toLocaleDateString('fr-FR', format));
        }
        break;
    }
    
    return labels;
  }
  
  private generatePriceData(): number[] {
    // Generate price data based on current stock price
    // This is for demo purposes only
    if (!this.stock) return [];
    
    const basePrice = this.stock.close;
    const volatility = basePrice * 0.03; // 3% volatility
    const trend = this.stock.change / 100; // Use current change as trend direction
    
    let dataPoints = 0;
    switch (this.selectedPeriod) {
      case 'day': dataPoints = 24; break;
      case 'week': dataPoints = 7; break;
      case 'month': dataPoints = 30; break;
      case 'quarter': dataPoints = 9; break;
      case 'year': dataPoints = 12; break;
    }
    
    const data: number[] = [];
    let lastPrice = basePrice - (basePrice * trend * 1.5); // Start with a price that will trend toward current price
    
    for (let i = 0; i < dataPoints; i++) {
      const randomChange = (Math.random() - 0.5) * volatility;
      const trendChange = basePrice * trend * (1 / dataPoints);
      lastPrice = lastPrice + randomChange + trendChange;
      lastPrice = Math.max(lastPrice, basePrice * 0.7); // Prevent going too low
      data.push(parseFloat(lastPrice.toFixed(2)));
    }
    
    // Ensure the last point matches the current price
    data[dataPoints - 1] = basePrice;
    
    return data;
  }
}