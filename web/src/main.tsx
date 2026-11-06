import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'
import { AuthProvider } from './auth/AuthProvider.tsx'
import { EventsProvider } from './events/EventsProvider.tsx'
import './index.css'
import { getPythonRunner } from './python/runner.ts'
import { routes } from './routes.tsx'

// The router reads the address bar and shows the matching page from routes.tsx.
const router = createBrowserRouter(routes)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <EventsProvider>
        <RouterProvider router={router} />
      </EventsProvider>
    </AuthProvider>
  </StrictMode>,
)

// Start loading Python in the background (about 10 MB, cached after the first
// visit), so it's ready by the time a code editor needs it (v1 spec, F4).
function preloadPython() {
  getPythonRunner()
    .start()
    .catch(() => {
      // Nothing to do here: each code editor shows its own message.
    })
}

if ('requestIdleCallback' in window) {
  window.requestIdleCallback(preloadPython)
} else {
  setTimeout(preloadPython, 1000)
}
