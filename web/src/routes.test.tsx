import { render, screen } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { describe, expect, it } from 'vitest'
import { APP_NAME } from './config.ts'
import { routes } from './routes.tsx'

// Renders the real app routes as if the browser were at `path`.
function renderAt(path: string) {
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  render(<RouterProvider router={router} />)
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

  it('shows the topic map at /map', () => {
    renderAt('/map')
    expect(
      screen.getByRole('heading', { name: 'Topic map' }),
    ).toBeInTheDocument()
  })

  it('shows the requested topic at /topic/:topicId', () => {
    renderAt('/topic/py.variables')
    expect(
      screen.getByRole('heading', { name: 'py.variables' }),
    ).toBeInTheDocument()
  })

  it('shows a not-found page for unknown addresses', () => {
    renderAt('/no-such-page')
    expect(
      screen.getByRole('heading', { name: 'Page not found' }),
    ).toBeInTheDocument()
  })
})
