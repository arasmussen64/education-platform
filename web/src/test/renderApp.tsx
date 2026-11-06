import { render } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { routes } from '../routes.tsx'
import { fakeAuth } from './fakeAuth.ts'

/**
 * Renders the real app as if the browser were at `path`, with a fake
 * sign-in service (signed out unless you pass one that's signed in).
 */
export function renderApp(path: string, auth = fakeAuth()) {
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  render(
    <AuthProvider auth={auth}>
      <RouterProvider router={router} />
    </AuthProvider>,
  )
  return { auth, router }
}
