import { Link, NavLink, Outlet } from 'react-router'
import { APP_NAME } from '../config.ts'

// NavLink tells us whether its link matches the current page, so the
// current page's tab can be highlighted.
function navLinkClass({ isActive }: { isActive: boolean }) {
  const base = 'rounded-md px-3 py-2 text-sm font-medium'
  return isActive
    ? `${base} bg-slate-900 text-white dark:bg-white dark:text-slate-900`
    : `${base} text-slate-700 hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-800`
}

// The frame around every page: the app name, the main navigation, and the
// current page (rendered where <Outlet /> is).
export function Layout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <header className="border-b border-slate-200 dark:border-slate-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
          <Link to="/" className="text-lg font-semibold">
            {APP_NAME}
          </Link>
          <nav aria-label="Main" className="flex gap-1">
            <NavLink to="/" end className={navLinkClass}>
              Today
            </NavLink>
            <NavLink to="/map" className={navLinkClass}>
              Map
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
