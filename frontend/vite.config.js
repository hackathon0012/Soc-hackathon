import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  envPrefix: 'VITE_', // Expose environment variables starting with VITE_ to the client
  build: {
    chunkSizeWarningLimit: 1600, // Adjust chunk size limit to suppress warning (default is 500kb)
  },
})
