// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'

// // https://vitejs.dev/config/
// export default defineConfig({
//   plugins: [react()],
// })

////////////////////////////////////////////////////////////////////////

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy WebSocket requests
      '/ws': {
        target: 'ws://localhost:8765',  // Your local WebSocket server
        ws: true,                       // Enable WebSocket proxying
        changeOrigin: true,
        secure: false,
      }
    }
  }
})