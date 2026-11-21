import { Link } from 'react-router'
import { SECONDARY_BUTTON } from '../components/styles.ts'
import { getTopic } from '../content/content.ts'
import type { Attempt } from '../followups/followUps.ts'
import {
  type Band,
  describeRate,
  FEWEST_TRIES,
  recentDifficulty,
  TARGET_RATE,
  topicDifficulty,
  topicsOffTarget,
} from './difficulty.ts'
import type { ProgressState } from './useProgress.ts'

const TARGET = `${Math.round(100 * TARGET_RATE)}%`

/** What each band means for the learner, and what to do about it. */
const ADVICE: Record<Band, string> = {
  'about-right':
    'That is in the range where learning goes fastest: hard enough to stretch you, with enough right answers to build on. Nothing to change.',
  easy: 'That is on the easy side. Practice that is nearly always right teaches less than it feels like it does. Where a topic feels easy, take "Check what you know" at the start of its practice, or go straight to "Prove it now", and spend the time on the proofs.',
  hard: 'That is on the hard side: mistakes are piling up faster than they can be fixed. Slow down. Finish each part of a lesson before its practice, study the worked examples, and do the mistakes that come back on the Today page.',
}

const BAND_WORDS: Record<Band, string> = {
  'about-right': 'about right',
  easy: 'easy for you',
  hard: 'hard for you',
}

/** How many topics the list names. */
const TOPICS_SHOWN = 5

/**
 * "How hard it's been" on the Account page (ADR-0030, progress/
 * difficulty.ts): the share of recent quick questions the learner got right
 * first time, against the 85% that learning is thought to go fastest at,
 * and the topics furthest from it. A guide for the learner, and for whoever
 * writes the questions; it changes no grade.
 */
export function DifficultySummary({ progress }: { progress: ProgressState }) {
  return (
    <section aria-labelledby="difficulty" className="space-y-3">
      <h2 id="difficulty" className="text-xl font-semibold">
        How hard it's been
      </h2>
      <p className="text-muted">
        Practice teaches most when you get about {TARGET} of the questions right
        on your first try: a little over one miss in seven. Much more than that
        and it's too easy to teach you much; much less and there's too little to
        build on.
      </p>
      <Figures progress={progress} />
    </section>
  )
}

function Figures({ progress }: { progress: ProgressState }) {
  if (progress.status === 'failed') {
    return (
      <p>Your answers couldn't load, so this can't be worked out right now.</p>
    )
  }
  if (progress.status !== 'ready')
    return <p>Working it out from your answers…</p>
  const recent = recentDifficulty(progress.attempts)
  if (!recent) {
    return (
      <p>
        Too few first tries to say yet: this needs {FEWEST_TRIES} quick
        questions answered in lessons and practice.
      </p>
    )
  }
  const off = topicsOffTarget(progress.attempts).slice(0, TOPICS_SHOWN)
  return (
    <>
      <p>
        Of your last {recent.tries} quick questions in lessons and practice, you
        got <span className="font-medium">{describeRate(recent)}</span>.{' '}
        {ADVICE[recent.band]}
      </p>
      {off.length > 0 && (
        <div className="space-y-1">
          <p className="font-medium">The topics furthest from {TARGET}:</p>
          <ul className="list-disc space-y-1 pl-6">
            {off.map(({ topicId, difficulty }) => (
              <li key={topicId}>
                <Link to={`/topic/${topicId}`} className="underline">
                  {getTopic(topicId)?.title ?? topicId}
                </Link>
                : {describeRate(difficulty)}, {BAND_WORDS[difficulty.band]}.
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  )
}

/**
 * In a topic's practice, once enough of its quick questions have been
 * tried: a note when they've been easy or hard for this learner, with the
 * one thing to do about it. Nothing shows in between, which is most of the
 * time.
 */
export function DifficultyNote({
  topicId,
  attempts,
  onProve,
  onLesson,
}: {
  topicId: string
  attempts: Attempt[]
  /** Opens the proofs. */
  onProve: () => void
  /** Opens the lesson's first part. */
  onLesson: () => void
}) {
  const difficulty = topicDifficulty(attempts, topicId)
  if (!difficulty || difficulty.band === 'about-right') return null
  const easy = difficulty.band === 'easy'
  return (
    <aside
      aria-label="How hard this topic has been"
      className="space-y-2 rounded-lg border border-line bg-sunken p-4"
    >
      <p>
        <span className="font-medium">
          So far here: {describeRate(difficulty)}.
        </span>{' '}
        {easy
          ? 'These are easy for you. If the rest of the practice looks the same, you may not need it: the proofs are what count.'
          : `That is well under the ${TARGET} where practice teaches most, which often means the lesson went by too fast, not that you can't do this. Going back over it now will make the rest of the practice worth more.`}
      </p>
      <button
        type="button"
        onClick={easy ? onProve : onLesson}
        className={SECONDARY_BUTTON}
      >
        {easy ? 'Go to the proofs' : 'Back to the lesson'}
      </button>
    </aside>
  )
}
