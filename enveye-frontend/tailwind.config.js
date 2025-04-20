/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    'bg-green-100',
    'bg-yellow-100',
    'bg-red-100',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
