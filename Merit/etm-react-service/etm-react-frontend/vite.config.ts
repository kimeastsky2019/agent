import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/dt/',
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: [
      'agent.gngmeta.com',
      'localhost',
      '.gngmeta.com',
    ],
    proxy: {
      '/api': {
        target: 'http://etengine:3000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
