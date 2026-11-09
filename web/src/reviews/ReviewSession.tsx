import { useId, useState } from 'react'
import { Link } from 'react-router'
import { PracticeItem } from '../components/PracticeItem.tsx'
import type { TopicContent } from '../content/types.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import type { Attempt } from '../followups/followUps.ts'
import type { TopicProgress } from '../progress/progress.ts'
import { type Rating, replayCard } from './fsrs.ts'
import { chooseReviewItems, describeGap, ratingOf } from './reviews.ts'

type Outcome = { rating: Rating; due: string }

/**
 * One topic's review session (ADR-0009): two items from its review pool,
 * rated from their first attempts, then saved as one `review` event. No
 * hints: the tutor is off during reviews.
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
  /** The whole history, to pick items answered longest ago. */
  attempts: Attempt[]
  /** When the page opened, in ISO format. */
  now: string
}) {
  const record = useRecordEvent()
  const headingId = useId()
  // Chosen once, when the session starts, so answering one item doesn't
  // change the others.
  const [items] = useState(() => chooseReviewItems(content, attempts))
  const [results, setResults] = useState<Map<string, boolean>>(new Map())
  const [outcome, setOutcome] = useState<Outcome | null>(null)
  const { topic } = content

  function graded(itemId: string, correct: boolean) {
    // Only the first attempt at each item counts toward the rating.
    if (outcome || results.has(itemId)) return
    const next = new Map(results).set(itemId, correct)
    setResults(next)
    if (next.size < items.length) return

    const rating = ratingOf(items.map((id) => next.get(id) ?? false))
    const at = new Date().toISOString()
    record({
      type: 'review',
      topic_id: topic.id,
      item_id: 'review',
      context: 'review',
      correct: rating === 'good',
      data: {
        rating,
        items: items.map((id) => ({ id, correct: next.get(id) ?? false })),
      },
    })
    const card = replayCard(progress.learnedAt ?? at, [
      ...progress.reviews,
      { at, rating },
    ])
    setOutcome({ rating, due: card.due })
  }

  return (
    <article aria-labelledby={headingId} className="space-y-3">
      <h3 id={headingId} className="text-lg font-semibold">
        <Link to={`/topic/${topic.id}`} className="underline">
          {topic.title}
        </Link>
      </h3>
      {items.map((itemId, index) => (
        <PracticeItem
          key={itemId}
          itemId={itemId}
          content={content}
          context="review"
          position={`Review ${index + 1} of ${items.length}`}
          onGraded={(correct) => graded(itemId, correct)}
        />
      ))}
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block font-medium">
        {outcome ? describeOutcome(outcome, now, items.length) : ''}
      </output>
    </article>
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
