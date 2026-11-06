import { Link } from 'react-router'

// Shown for any address that doesn't match a page.
export function NotFoundPage() {
  return (
    <section>
      <h1 className="text-2xl font-bold">Page not found</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-400">
        There is nothing at this address.{' '}
        <Link to="/" className="underline">
          Go to Today
        </Link>
      </p>
    </section>
  )
}
