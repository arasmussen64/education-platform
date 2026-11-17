import {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  useSyncExternalStore,
} from 'react'
import { useAuth } from '../auth/useAuth.ts'
import {
  fetchStepsOpened,
  localStepsOpened,
} from '../checkpoints/stepsOpened.ts'
import { getTopic } from '../content/content.ts'
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
import { type UsualTimes, usualTimes } from '../reviews/answerTime.ts'
import {
  progressOf,
  type StepsOpened,
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
      /**
       * How long the learner usually takes to get each kind of item right,
       * so a review can tell a slow right answer (ADR-0009, amended
       * 2026-11-16).
       */
      usualTimes: UsualTimes
    }

/** What the server sent, and for whom, so another learner never sees it. */
type Fetched = {
  userId: string
  history:
    | {
        attempts: Attempt[]
        index: SkillIndex
        /** When they opened a checkpoint's steps (ADR-0012). */
        stepsOpened: StepsOpened[]
      }
    | 'failed'
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
 * one from useCallback). The times the learner opened a checkpoint's steps
 * are read alongside it: they decide whether its main build still counts.
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
    // All three at once: the index downloads while the server answers. All
    // or nothing: without the openings, the page can't tell whether a
    // checkpoint's main build counts.
    Promise.all([load(), loadSkillIndex(), fetchStepsOpened()]).then(
      ([attempts, index, stepsOpened]) => {
        if (active) {
          setFetched({ userId, history: { attempts, index, stepsOpened } })
        }
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
    // Nor may the steps opened on this visit. Only the first opening of
    // each checkpoint's steps matters, so one seen twice changes nothing.
    const stepsOpened = [
      ...fetched.history.stepsOpened,
      ...localRows.map(localStepsOpened).filter((opened) => opened !== null),
    ]
    const itemsOf = openItemsOf(fetched.history.index)
    const followUps = openFollowUps(attempts, itemsOf)
    return {
      status: 'ready',
      progress: withOpenFollowUps(
        // Any bundled topic can give what it builds on implicit review
        // credit (ADR-0009, amended 2026-11-16), so look them all up.
        progressOf(topics, attempts, stepsOpened, getTopic),
        followUps,
      ),
      attempts,
      followUps,
      usualTimes: usualTimes(attempts, itemsOf),
    }
  }, [auth.status, fetched, userId, retry, localRows, topics])
}
