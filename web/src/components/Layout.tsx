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
  const base = 'rounded-full px-3.5 py-1.5 text-sm'
  return isActive
    ? `${base} ${YOU_ARE_HERE}`
    : `${base} font-medium text-ink hover:bg-line`
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
    <div className="min-h-screen bg-paper text-ink">
      <header
        ref={header}
        tabIndex={-1}
        // Stays at the top while the page scrolls, a little see-through,
        // so the way around is always one click away.
        className="sticky top-0 z-30 border-b border-line bg-paper/85 backdrop-blur outline-none"
      >
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-2 px-4 py-2.5">
          <Link
            to="/"
            className="flex items-center gap-2 font-display text-xl font-bold"
          >
            <Mark />
            {APP_NAME}
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <nav
              aria-label="Main"
              className="flex gap-1 rounded-full border border-line bg-card p-1"
            >
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
 * The app's mark: the favicon's switchback trail, lime on pine. It only
 * decorates the name beside it, so screen readers skip it.
 */
function Mark() {
  return (
    <svg viewBox="0 0 32 32" aria-hidden="true" className="h-7 w-7 shrink-0">
      <rect width="32" height="32" rx="8" fill="#1b2620" />
      <path
        d="M8 26 L24 21 L9 15 L23 10 L12 5"
        fill="none"
        stroke="#a3e635"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
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
        className="rounded-full px-3.5 py-1.5 font-medium text-muted hover:bg-line hover:text-ink"
      >
        Sign out
      </button>
    </div>
  )
}
