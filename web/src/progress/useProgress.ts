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
import {
  type Attempt,
  type FollowUp,
  openFollowUps,
} from '../followups/followUps.ts'
import {
  fetchAttempts,
  localAttempt,
  mergeAttempts,
} from '../followups/history.ts'
import {
  loadSkillIndex,
  openItemsOf,
  type SkillIndex,
} from '../followups/skillIndex.ts'
import {
  progressOf,
  type TopicProgress,
  withOpenFollowUps,
} from './progress.ts'

export type ProgressState =
  | { status: 'signed-out' }
  | { status: 'loading' }
  | { status: 'failed'; retry: () => void }
  | {
      status: 'ready'
      /** Each topic's progress, with its skills still being relearned. */
      progress: Map<string, TopicProgress>
      /** The graded history the progress was worked out from. */
      attempts: Attempt[]
      /** The mistakes coming back (ADR-0011), from that same history. */
      followUps: FollowUp[]
    }

/** What the server sent, and for whom, so another learner never sees it. */
type Fetched = {
  userId: string
  history: { attempts: Attempt[]; index: SkillIndex } | 'failed'
}

/**
 * The signed-in learner's progress on these topics. The history is read
 * from the server once; after that, a check passed on this device counts
 * straight away, with no reload.
 *
 * The follow-ups come from the same history, with the skill index
 * (followups/skillIndex.ts), so a topic isn't Mastered while one of its
 * skills is being relearned. They're only as complete as the history `load`
 * reads: all of it by default.
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
    // Both at once: the index downloads while the server answers.
    Promise.all([load(), loadSkillIndex()]).then(
      ([attempts, index]) => {
        if (active) setFetched({ userId, history: { attempts, index } })
      },
      () => {
        if (active) setFetched({ userId, history: 'failed' })
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
    if (fetched.history === 'failed') return { status: 'failed', retry }
    // Checks from this visit may not have reached the server yet.
    const local = localRows
      .map(localAttempt)
      .filter((attempt) => attempt !== null)
    const attempts = mergeAttempts(fetched.history.attempts, local)
    const followUps = openFollowUps(
      attempts,
      openItemsOf(fetched.history.index),
    )
    return {
      status: 'ready',
      progress: withOpenFollowUps(progressOf(topics, attempts), followUps),
      attempts,
      followUps,
    }
  }, [auth.status, fetched, userId, retry, localRows, topics])
}
