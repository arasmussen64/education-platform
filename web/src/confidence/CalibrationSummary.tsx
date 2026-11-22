import { useContext, useEffect, useState, useSyncExternalStore } from 'react'
import { EventLogContext } from '../events/eventLogContext.ts'
import {
  fetchResets,
  freshStart,
  latestResets,
  localResets,
} from '../resets/resets.ts'
import {
  calibration,
  FEWEST_ANSWERS,
  fetchRatedAnswers,
  levelSentence,
  localRatedAnswers,
  mergeRated,
  type RatedAnswer,
} from './confidence.ts'

type State =
  | { status: 'loading' }
  | { status: 'failed' }
  | { status: 'ready'; answers: RatedAnswer[] }

/**
 * How well the learner's confidence matches their answers (ADR-0028): for
 * each level they've used enough, how often they were right. Read from
 * their own answer events, saved and still on this device. Knowing what you
 * know is a skill, and the numbers are how a learner sees it. Answers from
 * before the learner started everything over aren't counted (ADR-0029).
 */
export function CalibrationSummary() {
  const log = useContext(EventLogContext)
  const [state, setState] = useState<State>({ status: 'loading' })
  // Starting everything over on this page, a moment ago, counts at once:
  // the effect below runs again when this time changes.
  const localRows = useSyncExternalStore(log.subscribe, log.getLocalRows)
  const startedHere = freshStart(latestResets(localResets(localRows)))

  useEffect(() => {
    let current = true
    fetchResets()
      .then(async (saved) => {
        const since = freshStart(
          latestResets(saved, localResets(log.getLocalRows())),
        )
        return { since, saved: await fetchRatedAnswers(since) }
      })
      .then(({ since, saved }) => {
        const here = localRatedAnswers(log.getLocalRows(), since)
        if (current)
          setState({ status: 'ready', answers: mergeRated(saved, here) })
      })
      .catch((error: unknown) => {
        console.error(
          'Reading answers for the calibration summary failed',
          error,
        )
        if (current) setState({ status: 'failed' })
      })
    return () => {
      current = false
    }
  }, [log, startedHere])

  return (
    <section aria-labelledby="calibration" className="space-y-3">
      <h2 id="calibration" className="text-xl font-semibold">
        How sure you are, and how often you're right
      </h2>
      <p className="text-muted">
        Before each quick question is checked, you say how sure you are. Here's
        how that compares with your answers. When the two match, you know what
        you know, and what to review.
      </p>
      {/* Announced when the answers have been read. A div, not <output>,
          because it may hold a list. */}
      <div aria-live="polite">
        <Summary state={state} />
      </div>
    </section>
  )
}

function Summary({ state }: { state: State }) {
  if (state.status === 'loading') return <>Reading your answers…</>
  if (state.status === 'failed') {
    return (
      <>
        Your answers couldn't be read. Check your connection, then reload the
        page.
      </>
    )
  }
  const sentences = calibration(state.answers)
    .map(levelSentence)
    .filter((sentence) => sentence !== null)
  if (sentences.length === 0) {
    return (
      <>
        Not enough answers yet: this needs at least {FEWEST_ANSWERS} at one
        level. Answer a few more questions, saying honestly how sure you are.
      </>
    )
  }
  return (
    <ul className="list-disc space-y-1 pl-6">
      {sentences.map((sentence) => (
        <li key={sentence}>{sentence}</li>
      ))}
    </ul>
  )
}
