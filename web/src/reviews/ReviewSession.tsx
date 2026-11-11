import { useEffect, useId, useRef, useState } from 'react'
import { Link } from 'react-router'
import { PracticeItem } from '../components/PracticeItem.tsx'
import { CARD } from '../components/styles.ts'
import type { TopicContent } from '../content/types.ts'
import type { NewEvent } from '../events/types.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import type { Attempt } from '../followups/followUps.ts'
import type { TopicProgress } from '../progress/progress.ts'
import { type Rating, replayCard } from './fsrs.ts'
import { describeGap, planReview, ratingOf } from './reviews.ts'

type Outcome = { rating: Rating; due: string }

/** A session's rating from its items' first answers, and when it's next due. */
function rate(
  items: string[],
  answers: Map<string, boolean>,
  progress: TopicProgress,
): Outcome {
  const rating = ratingOf(items.map((id) => answers.get(id) ?? false))
  const at = new Date().toISOString()
  const card = replayCard(progress.learnedAt ?? at, [
    ...progress.reviews,
    { at, rating },
  ])
  return { rating, due: card.due }
}

/** The one event that saves a finished session (ADR-0009). */
function reviewEvent(
  topicId: string,
  items: string[],
  answers: Map<string, boolean>,
  rating: Rating,
): NewEvent {
  return {
    type: 'review',
    topic_id: topicId,
    item_id: 'review',
    context: 'review',
    correct: rating === 'good',
    data: {
      rating,
      items: items.map((id) => ({ id, correct: answers.get(id) ?? false })),
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
}: {
  content: TopicContent
  /** The learner's progress on this topic, for the card's history. */
  progress: TopicProgress
  /** The whole history, to pick items and find earlier answers. */
  attempts: Attempt[]
  /** When the page opened, in ISO format. */
  now: string
}) {
  const record = useRecordEvent()
  const headingId = useId()
  const { topic } = content
  // Planned once, when the session starts, so answering one item doesn't
  // change the others.
  const [plan] = useState(() => planReview(content, progress.card, attempts))
  const { items } = plan
  // When earlier visits answered every item, the session is over as it
  // starts, already rated.
  const [finishedOnArrival] = useState(() =>
    items.length > 0 && plan.answered.size >= items.length
      ? rate(items, plan.answered, progress)
      : null,
  )
  const [results, setResults] = useState(plan.answered)
  const [outcome, setOutcome] = useState<Outcome | null>(finishedOnArrival)

  function graded(itemId: string, correct: boolean) {
    // Only the first attempt at each item counts toward the rating.
    if (outcome || results.has(itemId)) return
    const next = new Map(results).set(itemId, correct)
    setResults(next)
    if (next.size < items.length) return
    const finished = rate(items, next, progress)
    record(reviewEvent(topic.id, items, next, finished.rating))
    setOutcome(finished)
  }

  // Save a session that was over as it started, once. (The ref stops
  // React's development double run from saving it twice.)
  const savedOnArrival = useRef(false)
  useEffect(() => {
    if (!finishedOnArrival || savedOnArrival.current) return
    savedOnArrival.current = true
    record(
      reviewEvent(topic.id, items, plan.answered, finishedOnArrival.rating),
    )
  }, [finishedOnArrival, record, topic.id, items, plan.answered])

  return (
    <article aria-labelledby={headingId} className="space-y-3">
      <h3 id={headingId} className="text-lg font-semibold">
        <Link to={`/topic/${topic.id}`} className="underline">
          {topic.title}
        </Link>
      </h3>
      {items.map((itemId, index) => {
        const position = `Review ${index + 1} of ${items.length}`
        const earlier = plan.answered.get(itemId)
        return earlier === undefined ? (
          <PracticeItem
            key={itemId}
            itemId={itemId}
            content={content}
            context="review"
            position={position}
            onGraded={(correct) => graded(itemId, correct)}
          />
        ) : (
          <AnsweredEarlier key={itemId} position={position} correct={earlier} />
        )
      })}
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block font-medium">
        {outcome ? describeOutcome(outcome, now, items.length) : ''}
      </output>
    </article>
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
  { rating, due }: Outcome,
  now: string,
  count: number,
): string {
  const next = describeGap(now, due)
  if (rating === 'good') {
    return `Good: ${count === 1 ? 'right' : 'all right'}. Next review ${next}.`
  }
  if (rating === 'hard') {
    return `Hard: some right, some not. Next review ${next}, sooner than it would have been.`
  }
  return `Again: none right this time. This topic is relearning: it comes back ${next}, and the mistakes come back as fresh questions.`
}
