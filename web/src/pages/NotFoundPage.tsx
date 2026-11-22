import { Link } from 'react-router'

// Shown for any address that doesn't match a page.
export function NotFoundPage() {
  return (
    <section>
      <h1 className="text-3xl font-bold sm:text-4xl">Page not found</h1>
      <p className="mt-2 text-muted">
        There is nothing at this address.{' '}
        <Link to="/" className="underline">
          Go to Today
        </Link>
      </p>
    </section>
  )
}
