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
import { getTopic, topicIdsOf, tracks } from '../content/content.ts'
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
  afterResets,
  fetchResets,
  latestResets,
  localResets,
  type Resets,
  sinceFreshStart,
  type TrackReset,
} from '../resets/resets.ts'
import { type UsualTimes, usualTimes } from '../reviews/answerTime.ts'
import {
  type PersonalCurve,
  personalCurve,
  withPersonalCurve,
} from '../reviews/personal.ts'
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
      /**
       * The graded history the progress was worked out from: everything
       * except a started-over track's attempts from before its newest
       * reset (ADR-0029).
       */
      attempts: Attempt[]
      /**
       * Every graded attempt, track resets or not. Practice time, weeks
       * practised and the daily review limit count what the learner really
       * did. Only starting everything over cuts it short: then it holds
       * the attempts since (ADR-0029, amended 2026-11-22).
       */
      allAttempts: Attempt[]
      /** The newest time each track was started over, by track id. */
      resets: Resets
      /** The mistakes coming back (ADR-0011), from that same history. */
      followUps: FollowUp[]
      /**
       * How long the learner usually takes to get each kind of item right,
       * so a review can tell a slow right answer (ADR-0009, amended
       * 2026-11-16).
       */
      usualTimes: UsualTimes
      /**
       * The learner's own forgetting curve, fitted to every review once
       * there are enough (ADR-0009, amended 2026-11-16). The cards above
       * are scheduled by it. It describes the learner's memory, not a
       * track, so starting a track over keeps it (ADR-0029).
       */
      personalCurve: PersonalCurve
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
        /** When they started a track over (ADR-0029). */
        resets: TrackReset[]
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
    // All at once: the index downloads while the server answers. All or
    // nothing: without the openings, the page can't tell whether a
    // checkpoint's main build counts, and without the resets it would count
    // what the learner chose to start over.
    Promise.all([
      load(),
      loadSkillIndex(),
      fetchStepsOpened(),
      fetchResets(),
    ]).then(
      ([attempts, index, stepsOpened, resets]) => {
        if (active) {
          setFetched({
            userId,
            history: { attempts, index, stepsOpened, resets },
          })
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
    const resets = latestResets(fetched.history.resets, localResets(localRows))
    // Starting everything over counts nothing at all from before it: not
    // the hours, the weeks or the forgetting curve either.
    const allAttempts = sinceFreshStart(
      mergeAttempts(fetched.history.attempts, local),
      resets,
    )
    // A track started over counts nothing from before its newest reset
    // (ADR-0029). With no reset, these are the very same lists.
    const attempts = afterResets(allAttempts, resets)
    // Nor may the steps opened on this visit. Only the first opening of
    // each checkpoint's steps matters, so one seen twice changes nothing.
    const allStepsOpened = sinceFreshStart(
      [
        ...fetched.history.stepsOpened,
        ...localRows.map(localStepsOpened).filter((opened) => opened !== null),
      ],
      resets,
    )
    const stepsOpened = afterResets(allStepsOpened, resets)
    const itemsOf = openItemsOf(fetched.history.index)
    const followUps = openFollowUps(attempts, itemsOf)
    // Every bundled topic's progress, not only the ones asked for: the
    // personal forgetting curve is fitted to all of the learner's reviews,
    // and any topic can give what it builds on implicit review credit
    // (ADR-0009, amended 2026-11-16).
    const bundled = withBundled(topics)
    const all = progressOf(bundled, attempts, stepsOpened, getTopic)
    // The curve and the usual answer times describe the learner, not a
    // track, so they're worked out from every attempt, from before a
    // track's reset too (ADR-0029).
    const curve = personalCurve(
      attempts === allAttempts
        ? all
        : progressOf(bundled, allAttempts, allStepsOpened, getTopic),
    )
    return {
      status: 'ready',
      progress: withOpenFollowUps(
        withPersonalCurve(all, curve.multiplier),
        followUps,
      ),
      attempts,
      allAttempts,
      resets,
      followUps,
      usualTimes: usualTimes(allAttempts, itemsOf),
      personalCurve: curve,
    }
  }, [auth.status, fetched, userId, retry, localRows, topics])
}

/** The topics asked for, then every other topic bundled with the app. */
function withBundled(topics: Topic[]): Topic[] {
  const asked = new Set(topics.map((topic) => topic.id))
  const others = tracks()
    .flatMap(topicIdsOf)
    .filter((id) => !asked.has(id))
    .map((id) => getTopic(id))
    .filter((topic) => topic !== undefined)
  return [...topics, ...others]
}
