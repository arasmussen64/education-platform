/// <reference types="vitest/config" />
import { execSync } from 'node:child_process'
import { glob, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import mdx from '@mdx-js/rollup'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, normalizePath, type Plugin } from 'vite'
import { parse as parseYaml } from 'yaml'
import { limiter } from './src/tooling/limiter.ts'
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

// The app imports every exercise's starter, solution and tests, and the
// Python harness, as text (`?raw`): about 1,800 files. Vite's own loader opens
// them all at the same moment while building. Cloudflare's build machine only
// lets one program hold so many files open at once, and on 2026-11-11 the
// content grew past that: the live site's build failed with "EMFILE: too many
// open files". This reads the same files a few at a time instead. What ends
// up in the app is the same.
//
// Build only. The dev server and the tests read a file when a page asks for
// it, so they never open thousands together.
function rawFilesAFewAtATime(): Plugin {
  const aFewAtATime = limiter(32)
  const folders = ['../content/', '../harness/'].map((folder) =>
    normalizePath(fileURLToPath(new URL(folder, import.meta.url))),
  )
  return {
    name: 'raw-files-a-few-at-a-time',
    apply: 'build',
    // Before Vite's own loader, which would otherwise take these files.
    enforce: 'pre',
    async load(id) {
      const [file, query = ''] = id.split('?')
      const isRaw = /(^|&)raw(&|$)/.test(query)
      if (!isRaw || !folders.some((folder) => file.startsWith(folder))) {
        return null
      }
      const text = await aFewAtATime(() => readFile(file, 'utf-8'))
      return {
        code: `export default ${JSON.stringify(text)}`,
        map: { mappings: '' },
        // The file is Python or shell, but what this returns is JavaScript.
        moduleType: 'js',
      }
    },
  }
}

// The skill index (src/followups/skillIndex.ts): every question's and
// exercise's skills, stage and test skills, gathered from ../content into one
// small module, `virtual:skill-index`. Mistakes coming back, and so Mastered
// (ADR-0011), need only these, so the app needn't download whole topics to
// find them. It reads the same files content.ts loads, a few at a time like
// the raw files above, and src/followups/skillIndex.test.ts checks that it
// matches the full content.
function skillIndex(): Plugin {
  const moduleId = 'virtual:skill-index'
  // The "\0" tells other plugins this module isn't a file (Rollup's custom).
  const resolvedId = `\0${moduleId}`
  const topicsFolder = fileURLToPath(
    new URL('../content/topics/', import.meta.url),
  )
  // Reading some 1,600 files takes about a second, so it starts as soon as
  // the build, dev server or tests start, and the first page to ask for the
  // index doesn't wait for all of it.
  let reading: ReturnType<typeof readSkillIndex> | null = null
  const read = () => (reading ??= readSkillIndex(topicsFolder))
  return {
    name: 'skill-index',
    buildStart() {
      // If it fails, the page that asks for the index says why (load).
      read().catch(() => {})
    },
    resolveId(source) {
      return source === moduleId ? resolvedId : null
    },
    async load(id) {
      if (id !== resolvedId) return null
      try {
        return `export default ${JSON.stringify(await read())}`
      } catch (error) {
        reading = null
        throw error
      }
    },
    configureServer(server) {
      // A question added, changed or removed changes the index, so the dev
      // server builds it again the next time a page asks for it.
      server.watcher.on('all', (_event, file) => {
        if (!file.endsWith('.yaml')) return
        reading = null
        const index = server.moduleGraph.getModuleById(resolvedId)
        if (index) server.moduleGraph.invalidateModule(index)
      })
    },
  }
}

/** The part of a question's or exercise's file that the skill index keeps. */
type IndexedItem = {
  skills: string[]
  stage?: string
  test_skills?: Record<string, string[]>
}

/** Every topic's questions and exercises, by topic ID, then item ID. */
async function readSkillIndex(topicsFolder: string) {
  const aFewAtATime = limiter(32)
  const files: string[] = []
  // The same files as content.ts's recallFiles and exerciseFiles.
  for await (const file of glob(
    ['*/recall/*.yaml', '*/exercises/*/exercise.yaml'],
    { cwd: topicsFolder },
  )) {
    files.push(file)
  }
  const items = await Promise.all(
    files.sort().map(async (file) => {
      const text = await aFewAtATime(() =>
        readFile(join(topicsFolder, file), 'utf-8'),
      )
      const data = parseYaml(text) as Partial<IndexedItem> & { id: string }
      // The folder is the topic's ID ("\\" on Windows, "/" elsewhere).
      const [topicId = ''] = file.split(/[\\/]/)
      const item: IndexedItem = { skills: data.skills ?? [] }
      if (data.stage) item.stage = data.stage
      if (Object.keys(data.test_skills ?? {}).length > 0) {
        item.test_skills = data.test_skills
      }
      return { topicId, itemId: data.id, item }
    }),
  )
  const index: Record<string, Record<string, IndexedItem>> = {}
  for (const { topicId, itemId, item } of items) {
    index[topicId] ??= {}
    index[topicId][itemId] = item
  }
  return index
}

// The lessons (../content) and the Python harness (../harness) live outside
// web/, where the dev server doesn't look for new files by itself. Watching
// them means a newly added lesson, question or exercise shows up on the dev
// server straight away, without a restart.
function watchOutsideFolders(): Plugin {
  return {
    name: 'watch-outside-folders',
    configureServer(server) {
      for (const folder of ['../content', '../harness']) {
        server.watcher.add(fileURLToPath(new URL(folder, import.meta.url)))
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
    rawFilesAFewAtATime(),
    skillIndex(),
    watchOutsideFolders(),
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
