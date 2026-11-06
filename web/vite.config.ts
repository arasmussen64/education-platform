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
  server: {
    // The app bundles the shared Python harness from ../harness
    // (src/python/harnessFiles.ts), so the dev server may read the repo root.
    fs: { allow: ['..'] },
  },
  worker: {
    // The Python worker loads Pyodide with a dynamic import(), which needs
    // module workers.
    format: 'es',
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
