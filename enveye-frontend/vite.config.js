import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  base: '/static/',   // ✅ THIS is the important line we are adding
  plugins: [react()],
})
