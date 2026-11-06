import type { RouteObject } from 'react-router'
import { Layout } from './components/Layout.tsx'
import { ErrorPage } from './pages/ErrorPage.tsx'
import { MapPage } from './pages/MapPage.tsx'
import { NotFoundPage } from './pages/NotFoundPage.tsx'
import { SignInPage } from './pages/SignInPage.tsx'
import { topicLoader } from './pages/topicLoader.ts'

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
      {
        // If a page fails to load, the error shows inside the layout, so the
        // header and navigation still work.
        errorElement: <ErrorPage />,
        children: [
          {
            index: true,
            // Today can show practice questions with a code editor, so it
            // loads only when visited, like the topic pages.
            lazy: async () => {
              const { TodayPage } = await import('./pages/TodayPage.tsx')
              return { Component: TodayPage }
            },
          },
          { path: 'map', element: <MapPage /> },
          {
            path: 'topic/:topicId',
            // The topic's content and the page's code download at the same
            // time.
            loader: topicLoader,
            lazy: async () => {
              const { TopicPage } = await import('./pages/TopicPage.tsx')
              return { Component: TopicPage }
            },
          },
          { path: 'sign-in', element: <SignInPage /> },
          {
            path: 'playground',
            lazy: async () => {
              const { PlaygroundPage } =
                await import('./pages/PlaygroundPage.tsx')
              return { Component: PlaygroundPage }
            },
          },
          { path: '*', element: <NotFoundPage /> },
        ],
      },
    ],
  },
]
