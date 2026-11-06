import type { RouteObject } from 'react-router'
import { Layout } from './components/Layout.tsx'
import { MapPage } from './pages/MapPage.tsx'
import { NotFoundPage } from './pages/NotFoundPage.tsx'
import { SignInPage } from './pages/SignInPage.tsx'
import { TodayPage } from './pages/TodayPage.tsx'
import { TopicPage } from './pages/TopicPage.tsx'

// Every page in the app and its address. All pages render inside <Layout>,
// which adds the header and navigation. Tests reuse this list with an
// in-memory router, so they exercise the same routes as the real app.
//
// Pages with a code editor are loaded only when visited ("lazy"), so the
// editor's code isn't downloaded until a page needs it.
export const routes: RouteObject[] = [
  {
    element: <Layout />,
    // Shown while a lazy page's code loads when the app first opens on it.
    hydrateFallbackElement: (
      <p className="p-8 text-slate-500 dark:text-slate-400">Loading…</p>
    ),
    children: [
      { index: true, element: <TodayPage /> },
      { path: 'map', element: <MapPage /> },
      { path: 'topic/:topicId', element: <TopicPage /> },
      { path: 'sign-in', element: <SignInPage /> },
      {
        path: 'playground',
        lazy: async () => {
          const { PlaygroundPage } = await import('./pages/PlaygroundPage.tsx')
          return { Component: PlaygroundPage }
        },
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
