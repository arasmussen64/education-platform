/// <reference types="vitest/config" />
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'
import { APP_NAME } from './src/config.ts'

// Adds the product name as the page <title>, so the name only ever has to be
// changed in src/config.ts (ADR-0006).
function appTitle(): Plugin {
  return {
    name: 'app-title',
    transformIndexHtml() {
      return [{ tag: 'title', children: APP_NAME, injectTo: 'head' }]
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), appTitle()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
