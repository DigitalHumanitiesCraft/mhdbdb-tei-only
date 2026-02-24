/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './korpus.html',
    './playground/index.html',
    './lemma/index.html',
    './testing/test.html',
    './assets/js/**/*.js',
    './playground/js/**/*.js',
    './lemma/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f1f5fd',
          100: '#e2ebfa',
          200: '#c0d3f4',
          300: '#96b3ec',
          400: '#6690e3',
          500: '#3b75d8',
          600: '#265cc4',
          700: '#1f4aa2',
          800: '#1e3e80',
          900: '#1c3568',
        },
      },
    },
  },
  plugins: [],
};
