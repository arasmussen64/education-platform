import { render } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { EventsProvider } from '../events/EventsProvider.tsx'
import { routes } from '../routes.tsx'
import { fakeAuth } from './fakeAuth.ts'
import { fakeEventsClient } from './fakeEvents.ts'

/**
 * Renders the real app as if the browser were at `path`, with a fake
 * sign-in service (signed out unless you pass one that's signed in) and a
 * fake server for saving events.
 */
export function renderApp(
  path: string,
  auth = fakeAuth(),
  events = fakeEventsClient(),
) {
  const router = createMemoryRouter(routes, { initialEntries: [path] })
  render(
    <AuthProvider auth={auth}>
      <EventsProvider client={events}>
        <RouterProvider router={router} />
      </EventsProvider>
    </AuthProvider>,
  )
  return { auth, events, router }
}
