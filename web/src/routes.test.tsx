import { screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { APP_NAME } from './config.ts'
import { renderApp } from './test/renderApp.tsx'

// Topic pages contain code runners: use the fake Python and plain-textbox
// editor instead of Pyodide and CodeMirror.
vi.mock('./python/runner.ts', () =>
  import('./test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock(
  './components/CodeEditor.tsx',
  () => import('./test/FakeCodeEditor.tsx'),
)

// Renders the real app routes as if the browser were at `path`.
function renderAt(path: string) {
  renderApp(path)
}

describe('app routes', () => {
  it('shows the app name and the main navigation', () => {
    renderAt('/')
    expect(screen.getByRole('link', { name: APP_NAME })).toBeInTheDocument()
    const nav = screen.getByRole('navigation', { name: 'Main' })
    expect(nav).toHaveTextContent('Today')
    expect(nav).toHaveTextContent('Map')
    expect(nav).toHaveTextContent('Playground')
  })

  it('shows the Today page at /', () => {
    renderAt('/')
    expect(screen.getByRole('heading', { name: 'Today' })).toBeInTheDocument()
  })

  it('shows the topic map at /map, with every module', () => {
    renderAt('/map')
    expect(
      screen.getByRole('heading', { name: 'Topic map' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Module 1: First programs' }),
    ).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Variables' })).toHaveAttribute(
      'href',
      '/topic/py.variables',
    )
  })

  // Topic pages load their code and content first, so these wait for them.
  it('shows the requested topic at /topic/:topicId', async () => {
    renderAt('/topic/py.variables')
    expect(
      await screen.findByRole(
        'heading',
        { level: 1, name: 'Variables' },
        { timeout: 10_000 },
      ),
    ).toBeInTheDocument()
  })

  it('shows a finished topic from content/, with its compiled lesson', async () => {
    renderAt('/topic/py.programs-and-print')
    expect(
      await screen.findByRole(
        'heading',
        { level: 1, name: 'Programs and print' },
        { timeout: 10_000 },
      ),
    ).toBeInTheDocument()
    const learn = screen.getByRole('region', { name: 'Learn' })
    expect(within(learn).getByText('What to watch for')).toBeInTheDocument()
    expect(within(learn).getByTitle(/CS50P Lecture 0/)).toHaveAttribute(
      'src',
      'https://www.youtube-nocookie.com/embed/JP7ITIXGpHk?start=24&end=591&rel=0',
    )
    expect(learn).toHaveTextContent(
      'This clip: 0:24 to 9:51 (about 9 minutes).',
    )
    expect(screen.getByRole('region', { name: 'Practice' })).toHaveTextContent(
      'Practice 6 of 6',
    )
  })

  it("says when a topic doesn't exist", async () => {
    renderAt('/topic/py.nothing')
    expect(
      await screen.findByRole(
        'heading',
        { name: 'Topic not found' },
        { timeout: 10_000 },
      ),
    ).toBeInTheDocument()
  })

  it('shows a not-found page for unknown addresses', () => {
    renderAt('/no-such-page')
    expect(
      screen.getByRole('heading', { name: 'Page not found' }),
    ).toBeInTheDocument()
  })
})
