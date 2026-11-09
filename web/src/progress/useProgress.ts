import {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
} from 'react'
import { useAuth } from '../auth/useAuth.ts'
import type { Topic } from '../content/types.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import type { Attempt } from '../followups/followUps.ts'
import {
  fetchAttempts,
  localAttempt,
  mergeAttempts,
} from '../followups/history.ts'
import { progressOf, type TopicProgress } from './progress.ts'

export type ProgressState =
  | { status: 'signed-out' }
  | { status: 'loading' }
  | { status: 'failed'; retry: () => void }
  | {
      status: 'ready'
      progress: Map<string, TopicProgress>
      /** The graded history the progress was worked out from. */
      attempts: Attempt[]
    }

/** What the server sent, and for whom, so another learner never sees it. */
type Fetched = { userId: string; attempts: Attempt[] | 'failed' }

/**
 * The signed-in learner's progress on these topics. The history is read
 * from the server once; after that, a check passed on this device counts
 * straight away, with no reload.
 *
 * `load` reads the history. It's an effect dependency, so it must keep the
 * same identity from one render to the next (a module-level function, or
 * one from useCallback).
 */
export function useProgress(
  topics: Topic[],
  load: () => Promise<Attempt[]> = fetchAttempts,
): ProgressState {
  const auth = useAuth()
  const log = useContext(EventLogContext)
  const localRows = useSyncExternalStore(log.subscribe, log.getLocalRows)
  const userId = auth.status === 'signed-in' ? auth.user.id : null
  const [fetched, setFetched] = useState<Fetched | null>(null)
  const [tries, setTries] = useState(0)

  useEffect(() => {
    if (!userId) return
    let active = true
    load().then(
      (attempts) => {
        if (active) setFetched({ userId, attempts })
      },
      () => {
        if (active) setFetched({ userId, attempts: 'failed' })
      },
    )
    return () => {
      active = false
    }
  }, [userId, load, tries])

  const retry = useCallback(() => {
    setFetched(null)
    setTries((count) => count + 1)
  }, [])

  return useMemo<ProgressState>(() => {
    if (auth.status === 'signed-out') return { status: 'signed-out' }
    if (fetched === null || fetched.userId !== userId) {
      return { status: 'loading' }
    }
    if (fetched.attempts === 'failed') return { status: 'failed', retry }
    // Checks from this visit may not have reached the server yet.
    const local = localRows
      .map(localAttempt)
      .filter((attempt) => attempt !== null)
    const attempts = mergeAttempts(fetched.attempts, local)
    return { status: 'ready', progress: progressOf(topics, attempts), attempts }
  }, [auth.status, fetched, userId, retry, localRows, topics])
}
