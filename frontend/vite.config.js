import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: 'localhost',
    // Fix 404 errors on refresh for SPA routing
    historyApiFallback: true
  },
  // Ensure proper base path handling
  base: '/',
  // Build configuration for SPA
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
})
