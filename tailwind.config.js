/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#E6F0FF',
          100: '#CCE0FF',
          200: '#99C2FF',
          300: '#66A3FF',
          400: '#3385FF',
          500: '#0052CC',
          600: '#0047B3',
          700: '#003D99',
          800: '#003380',
          900: '#002966',
        },
        positive: {
          50: '#E6F7F0',
          100: '#CCEEE0',
          200: '#99DEC2',
          300: '#66CDA3',
          400: '#36B37E',
          500: '#2E9F6F',
          600: '#268C60',
          700: '#1F7951',
          800: '#196642',
          900: '#135333',
        },
        negative: {
          50: '#FFEBE6',
          100: '#FFD7CC',
          200: '#FFAF99',
          300: '#FF8766',
          400: '#FF5630',
          500: '#E64C2B',
          600: '#CC4326',
          700: '#B33920',
          800: '#99301B',
          900: '#802817',
        },
        neutral: {
          50: '#F7F9FC',
          100: '#EEF2F7',
          200: '#DDE5EF',
          300: '#CCD8E6',
          400: '#B7C9DE',
          500: '#A2BAD6',
          600: '#8DA8CC',
          700: '#7896C2',
          800: '#6383B9',
          900: '#4E71AF',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
      },
    },
  },
  plugins: [],
}