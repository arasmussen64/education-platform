import { type ReactNode, useEffect, useState } from 'react'
import { useAuth } from '../auth/useAuth.ts'
import { createEventLog } from './eventLog.ts'
import { EventLogContext } from './eventLogContext.ts'
import { createOutbox } from './outbox.ts'
import { supabaseEventsClient } from './supabaseEvents.ts'
import type { EventsClient } from './sync.ts'

type Props = {
  children: ReactNode
  /** Tests pass fakes; the app uses Supabase and localStorage. */
  client?: EventsClient
  storage?: Storage
}

/**
 * Shares the event log with the whole app, tells it who's signed in, and
 * nudges it to send whatever is waiting when the connection returns.
 */
export function EventsProvider({ children, client, storage }: Props) {
  const auth = useAuth()
  const [log] = useState(() =>
    createEventLog({
      outbox: createOutbox(storage),
      client: () => client ?? supabaseEventsClient(),
      contentBuild: __CONTENT_BUILD__,
    }),
  )

  const userId =
    auth.status === 'loading'
      ? undefined
      : auth.status === 'signed-in'
        ? auth.user.id
        : null
  useEffect(() => {
    log.setUser(userId)
  }, [log, userId])

  useEffect(() => {
    const syncNow = () => void log.sync()
    const syncIfVisible = () => {
      if (document.visibilityState === 'visible') syncNow()
    }
    // The browser says the connection is back, or the learner returned to
    // this tab: a good moment to try again.
    window.addEventListener('online', syncNow)
    document.addEventListener('visibilitychange', syncIfVisible)
    return () => {
      window.removeEventListener('online', syncNow)
      document.removeEventListener('visibilitychange', syncIfVisible)
      log.stop()
    }
  }, [log])

  return <EventLogContext value={log}>{children}</EventLogContext>
}
