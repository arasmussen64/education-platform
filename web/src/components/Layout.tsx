import { useRef } from 'react'
import { Link, NavLink, Outlet, useNavigation } from 'react-router'
import { displayName } from '../auth/authContext.ts'
import { useAuth } from '../auth/useAuth.ts'
import { APP_NAME } from '../config.ts'
import { BackToTop } from './BackToTop.tsx'
import { SaveStatus } from './SaveStatus.tsx'
import { YOU_ARE_HERE } from './styles.ts'

// NavLink tells us whether its link matches the current page, so the
// current page's tab can be highlighted.
function navLinkClass({ isActive }: { isActive: boolean }) {
  const base = 'rounded-md px-3 py-2 text-sm'
  return isActive
    ? `${base} ${YOU_ARE_HERE}`
    : `${base} font-medium text-slate-700 hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-800`
}

// The frame around every page: the app name, the main navigation, who's
// signed in, and the current page (rendered where <Outlet /> is).
export function Layout() {
  // "loading" while the next page's content downloads (e.g. a topic's
  // lesson); the current page fades a little so the click visibly worked.
  const loading = useNavigation().state === 'loading'
  // "Back to top" puts keyboard focus here, so the next Tab is the app name.
  const header = useRef<HTMLElement>(null)
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <header
        ref={header}
        tabIndex={-1}
        className="border-b border-slate-200 outline-none dark:border-slate-800"
      >
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-2 px-4 py-3">
          <Link to="/" className="text-lg font-semibold">
            {APP_NAME}
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <nav aria-label="Main" className="flex gap-1">
              <NavLink to="/" end className={navLinkClass}>
                Today
              </NavLink>
              <NavLink to="/map" className={navLinkClass}>
                Map
              </NavLink>
              <NavLink to="/playground" className={navLinkClass}>
                Playground
              </NavLink>
            </nav>
            <SaveStatus />
            <Account />
          </div>
        </div>
      </header>
      <main
        aria-busy={loading}
        // pb-20 leaves room under the last line for the "Back to top" button.
        className={`mx-auto max-w-5xl px-4 pt-8 pb-20 transition-opacity ${loading ? 'opacity-60' : ''}`}
      >
        <Outlet />
      </main>
      <BackToTop focusTarget={() => header.current} />
    </div>
  )
}

/**
 * "Sign in", or the signed-in learner's name, which links to their account
 * page, with a "Sign out" button.
 */
function Account() {
  const auth = useAuth()
  if (auth.status === 'loading') return null
  if (auth.status === 'signed-out') {
    return (
      <NavLink to="/sign-in" className={navLinkClass}>
        Sign in
      </NavLink>
    )
  }
  return (
    <div className="flex items-center gap-1 text-sm">
      <NavLink to="/account" className={navLinkClass}>
        {/* Screen readers hear where the link goes, not only a name. */}
        <span className="sr-only">Your account:</span> {displayName(auth.user)}
      </NavLink>
      <button
        type="button"
        onClick={() => {
          auth.signOut().catch(() => {
            // If signing out fails, the header still shows the name, which is
            // the honest state, so there's nothing else to do here.
          })
        }}
        className="rounded-md px-3 py-2 font-medium text-slate-700 hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        Sign out
      </button>
    </div>
  )
}
