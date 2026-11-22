import { useEffect } from 'react'
import { useRouteError } from 'react-router'
import { BUTTON } from '../components/styles.ts'

// Shown inside the layout when a page fails to load. The usual cause: the app
// was updated while it was open, so the old version's page files are gone.
// Reloading fetches the new version.
export function ErrorPage() {
  const error = useRouteError()

  useEffect(() => {
    // Keep the details for whoever opens the browser's developer console.
    console.error(error)
  }, [error])

  return (
    <section className="space-y-3">
      <h1 className="text-3xl font-bold sm:text-4xl">Something went wrong</h1>
      <p className="text-muted">
        This page couldn't load. If the app was updated since you opened it,
        reloading fixes it.
      </p>
      <button
        type="button"
        onClick={() => window.location.reload()}
        className={BUTTON}
      >
        Reload the page
      </button>
    </section>
  )
}
