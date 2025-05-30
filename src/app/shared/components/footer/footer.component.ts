import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  template: `
    <footer class="bg-neutral-800 text-neutral-200 py-8">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="mb-4 md:mb-0">
            <p class="text-sm">
              © 2025 Paris Stock Tracker. All data provided by TradingView.
            </p>
          </div>
          <div class="flex space-x-6">
            <a href="#" class="text-sm hover:text-white transition-colors">Terms</a>
            <a href="#" class="text-sm hover:text-white transition-colors">Privacy</a>
            <a href="#" class="text-sm hover:text-white transition-colors">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  `
})
export class FooterComponent {}