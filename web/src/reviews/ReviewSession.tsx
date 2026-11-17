import { useEffect, useId, useRef, useState } from 'react'
import { Link } from 'react-router'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { CARD } from '../components/styles.ts'
import type { TopicContent } from '../content/types.ts'
import type { NewEvent } from '../events/types.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import type { Attempt } from '../followups/followUps.ts'
import type { TopicProgress } from '../progress/progress.ts'
import {
  kindOf,
  rateSession,
  type SessionAnswer,
  type UsualTimes,
} from './answerTime.ts'
import type { Rating } from './fsrs.ts'
import { replayWithCredits } from './implicit.ts'
import { describeGap, planReview } from './reviews.ts'

type Outcome = {
  rating: Rating
  due: string
  /** Right answers that took far longer than usual (ADR-0009, 2026-11-16). */
  slow: string[]
  /** Whether they made an all-right session Hard. */
  slowed: boolean
}

/** An item's first answer: whether it was right, and how long it took. */
type Answer = { correct: boolean; durationMs: number | null }

/** The session's answers, in the items' order, with each item's kind. */
function sessionAnswers(
  content: TopicContent,
  items: string[],
  answers: Map<string, Answer>,
): SessionAnswer[] {
  return items.map((itemId) => {
    const answer = answers.get(itemId)
    return {
      itemId,
      correct: answer?.correct ?? false,
      durationMs: answer?.durationMs ?? null,
      kind: kindOf(content.recall[itemId] ?? content.exercises[itemId]),
    }
  })
}

/**
 * A session's rating from its items' first answers and their times, and
 * when it's next due.
 */
function rate(
  content: TopicContent,
  items: string[],
  answers: Map<string, Answer>,
  progress: TopicProgress,
  usual: UsualTimes,
): Outcome {
  const { rating, slow, slowed } = rateSession(
    sessionAnswers(content, items, answers),
    usual,
  )
  const at = new Date().toISOString()
  // The implicit reviews that counted before stay counted (ADR-0009,
  // amended 2026-11-16): a review now can't change what came before it.
  const { card } = replayWithCredits(
    progress.learnedAt ?? at,
    [...progress.reviews, { at, rating }],
    progress.credits,
    // The learner's own forgetting curve, when one is fitted.
    progress.card?.personal,
  )
  return { rating, due: card.due, slow, slowed }
}

/** No usual times known: no answer counts as slow. */
const NO_TIMES: UsualTimes = new Map()

/** The one event that saves a finished session (ADR-0009). */
function reviewEvent(
  topicId: string,
  items: string[],
  answers: Map<string, Answer>,
  { rating, slow }: Outcome,
): NewEvent {
  return {
    type: 'review',
    topic_id: topicId,
    item_id: 'review',
    context: 'review',
    correct: rating === 'good',
    data: {
      rating,
      items: items.map((id) => ({
        id,
        correct: answers.get(id)?.correct ?? false,
      })),
      // Only when some right answer was slow: which ones.
      ...(slow.length > 0 ? { slow } : {}),
    },
  }
}

/**
 * One topic's review session (ADR-0009): two items from its review pool,
 * rated from their first attempts, then saved as one `review` event. No
 * hints: the tutor is off during reviews. A session left half-way picks up
 * where it stopped: answers given since the topic fell due still count.
 */
export function ReviewSession({
  content,
  progress,
  attempts,
  now,
  usualTimes = NO_TIMES,
}: {
  content: TopicContent
  /** The learner's progress on this topic, for the card's history. */
  progress: TopicProgress
  /** The whole history, to pick items and find earlier answers. */
  attempts: Attempt[]
  /** When the page opened, in ISO format. */
  now: string
  /**
   * How long the learner usually takes to get each kind of item right
   * (useProgress). Without it, no answer counts as slow.
   */
  usualTimes?: UsualTimes
}) {
  const record = useRecordEvent()
  const headingId = useId()
  const { topic } = content
  // Planned once, when the session starts, so answering one item doesn't
  // change the others.
  const [plan] = useState(() => planReview(content, progress.card, attempts))
  // A review lab can be put off to another review, with no penalty: the
  // learner may be away from the computer that runs it (ADR-0009, amended
  // 2026-11-16). A question takes its place.
  const [labPutOff, setLabPutOff] = useState(false)
  const items = labPutOff ? plan.withoutLab : plan.items
  // When earlier visits answered every item, the session is over as it
  // starts, already rated.
  // Answers from an earlier visit aren't timed: only this visit's are.
  const [carried] = useState(
    () =>
      new Map<string, Answer>(
        [...plan.answered].map(([id, correct]) => [
          id,
          { correct, durationMs: null },
        ]),
      ),
  )
  const [finishedOnArrival] = useState(() =>
    items.length > 0 && carried.size >= items.length
      ? rate(content, items, carried, progress, usualTimes)
      : null,
  )
  const [results, setResults] = useState(carried)
  const [outcome, setOutcome] = useState<Outcome | null>(finishedOnArrival)

  function graded(itemId: string, correct: boolean, durationMs: number | null) {
    // Only the first attempt at each item counts toward the rating.
    if (outcome || results.has(itemId)) return
    const next = new Map(results).set(itemId, { correct, durationMs })
    setResults(next)
    if (next.size < items.length) return
    const finished = rate(content, items, next, progress, usualTimes)
    record(reviewEvent(topic.id, items, next, finished))
    setOutcome(finished)
  }

  // Save a session that was over as it started, once. (The ref stops
  // React's development double run from saving it twice.)
  const savedOnArrival = useRef(false)
  useEffect(() => {
    if (!finishedOnArrival || savedOnArrival.current) return
    savedOnArrival.current = true
    record(reviewEvent(topic.id, items, carried, finishedOnArrival))
  }, [finishedOnArrival, record, topic.id, items, carried])

  return (
    <article aria-labelledby={headingId} className="space-y-3">
      <h3 id={headingId} className="text-lg font-semibold">
        <Link to={`/topic/${topic.id}`} className="underline">
          {topic.title}
        </Link>
      </h3>
      {labPutOff && (
        <p className="text-sm text-slate-600 dark:text-slate-400">
          The lab is put off: a question took its place, and the lab comes back
          at a later review.
        </p>
      )}
      {items.map((itemId, index) => {
        const position = `Review ${index + 1} of ${items.length}`
        const earlier = plan.answered.get(itemId)
        if (earlier !== undefined) {
          return (
            <AnsweredEarlier
              key={itemId}
              position={position}
              correct={earlier}
            />
          )
        }
        const item = (
          <PracticeItem
            key={itemId}
            itemId={itemId}
            content={content}
            context="review"
            position={position}
            onGraded={(correct, durationMs) =>
              graded(itemId, correct, durationMs)
            }
          />
        )
        if (itemId !== plan.lab || results.has(itemId) || outcome) return item
        return (
          <div key={itemId} className="space-y-2">
            <LabChoice onPutOff={() => setLabPutOff(true)} />
            {item}
          </div>
        )
      })}
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block font-medium">
        {outcome ? describeOutcome(outcome, now, items.length) : ''}
      </output>
    </article>
  )
}

/**
 * Says this review has a lab in it, and offers to put it off: the learner
 * may be away from the computer that runs it.
 */
function LabChoice({ onPutOff }: { onPutOff: () => void }) {
  return (
    <p className="text-sm">
      This review has a hands-on lab in place of a quick question: about 10 to
      15 minutes, on the computer where you run the labs. Away from it?{' '}
      <button type="button" onClick={onPutOff} className="underline">
        Do the lab another time
      </button>{' '}
      and answer a question instead. It doesn't count against you.
    </p>
  )
}

/** An item of this review answered on an earlier visit: its answer stands. */
function AnsweredEarlier({
  position,
  correct,
}: {
  position: string
  correct: boolean
}) {
  return (
    <section className={CARD}>
      <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400">
        {position}
      </p>
      <p>
        You answered this one on an earlier visit, and{' '}
        {correct ? 'got it right' : "didn't get it right"}. Your first answer is
        the one that counts, so it stays.
      </p>
    </section>
  )
}

function describeOutcome(
  { rating, due, slow, slowed }: Outcome,
  now: string,
  count: number,
): string {
  const next = describeGap(now, due)
  if (rating === 'good') {
    return `Good: ${count === 1 ? 'right' : 'all right'}. Next review ${next}.`
  }
  if (slowed) {
    // Right, but slowly: the memory is there and starting to fade.
    const which = count === 1 ? 'it' : slow.length === count ? 'they' : 'one'
    return `Hard: ${count === 1 ? 'right' : 'all right'}, but ${which} took much longer than you usually need. Next review ${next}, a little sooner, while it's still there to strengthen.`
  }
  if (rating === 'hard') {
    return `Hard: some right, some not. Next review ${next}, sooner than it would have been.`
  }
  return `Again: none right this time. This topic is relearning: it comes back ${next}, and the mistakes come back as fresh questions.`
}
