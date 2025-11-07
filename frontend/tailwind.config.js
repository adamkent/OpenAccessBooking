/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // NHS Brand Colors
        'nhs-blue': '#005eb8',
        'nhs-dark-blue': '#003087',
        'nhs-light-blue': '#0072ce',
        'nhs-green': '#009639',
        'nhs-dark-green': '#006747',
        'nhs-purple': '#330072',
        'nhs-pink': '#ae2573',
        'nhs-red': '#da291c',
        'nhs-orange': '#ed8b00',
        'nhs-warm-yellow': '#ffb81c',
        'nhs-yellow': '#fae100',
        
        // NHS Greys
        'nhs-black': '#231f20',
        'nhs-dark-grey': '#425563',
        'nhs-mid-grey': '#768692',
        'nhs-pale-grey': '#e8edee',
        'nhs-white': '#ffffff',
        
        // Status Colors
        'success': '#009639',
        'warning': '#ffb81c',
        'error': '#da291c',
        'info': '#005eb8',
      },
      fontFamily: {
        'sans': ['Inter', 'Arial', 'sans-serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      maxWidth: {
        '8xl': '88rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
