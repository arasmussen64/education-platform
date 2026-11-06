/// <reference types="vitest/config" />
import { execSync } from 'node:child_process'
import mdx from '@mdx-js/rollup'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'
import { parse as parseYaml } from 'yaml'
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

// Turns the YAML content files (../content) into plain data while building, so
// the browser never needs a YAML parser.
function contentYaml(): Plugin {
  return {
    name: 'content-yaml',
    transform(source, id) {
      if (!id.split('?')[0].endsWith('.yaml')) return null
      return {
        code: `export default ${JSON.stringify(parseYaml(source))}`,
        map: null,
      }
    },
  }
}

// The git commit being built. It's saved with every learner event, so each
// answer can be matched to the exact content it was given (ADR-0008).
function gitCommit(): string {
  try {
    return execSync('git rev-parse HEAD', {
      stdio: ['ignore', 'pipe', 'ignore'],
    })
      .toString()
      .trim()
  } catch {
    // No git: Cloudflare's builds also name the commit in a variable.
    return process.env.WORKERS_CI_COMMIT_SHA ?? 'unknown'
  }
}

// https://vite.dev/config/
export default defineConfig({
  define: {
    // Replaced with the commit wherever the app's code says __CONTENT_BUILD__.
    __CONTENT_BUILD__: JSON.stringify(gitCommit()),
  },
  plugins: [
    // Lessons are MDX: Markdown with components like <Intro> and <Resource>.
    { enforce: 'pre', ...mdx() },
    react({ include: /\.(mdx|js|jsx|ts|tsx)$/ }),
    tailwindcss(),
    contentYaml(),
    appTitle(),
  ],
  resolve: {
    // Compiled lessons import React, but they live in ../content, where a
    // normal lookup would never reach web/node_modules. This makes every
    // import of React come from the app's own copy.
    dedupe: ['react', 'react-dom'],
  },
  server: {
    // The app bundles the shared Python harness (../harness) and the
    // content (../content), so the dev server may read the repo root.
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
