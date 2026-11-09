// Review sessions (ADR-0009, v1 spec F11): which topics are due, which
// items to ask, and how a session is rated.
import { STAGES } from '../content/stages.ts'
import type { Topic, TopicContent } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import { lastAttempted } from '../followups/followUps.ts'
import type { TopicProgress } from '../progress/progress.ts'
import { type Card, type Rating, retrievabilityAt } from './fsrs.ts'

/** At most this many topic reviews a day (ADR-0009). */
export const DAILY_REVIEW_LIMIT = 20
/** A review session asks this many items from the topic's review pool. */
export const ITEMS_PER_REVIEW = 2

export type DueReview = {
  topic: Topic
  card: Card
  /** The chance the topic is still remembered, 0 to 1. */
  retrievability: number
}

/**
 * The topics whose review is due at `now`, most forgotten first, up to the
 * daily limit. `topics` are the ones that can be opened, in track order;
 * checkpoints never have cards.
 */
export function dueReviews(
  topics: Topic[],
  progress: Map<string, TopicProgress>,
  now: string,
  limit = DAILY_REVIEW_LIMIT,
): DueReview[] {
  const due: DueReview[] = []
  for (const topic of topics) {
    if (topic.kind !== 'topic') continue
    const card = progress.get(topic.id)?.card
    if (!card || card.due > now) continue
    due.push({ topic, card, retrievability: retrievabilityAt(card, now) })
  }
  return due.sort((a, b) => a.retrievability - b.retrievability).slice(0, limit)
}

/**
 * The predicted chance of still remembering a Learned topic, as a whole
 * percentage, for the map (roadmap: "the living map"). 100 right after a
 * review, drifting down until the next one is due at the 90% target.
 */
export function memoryPercent(card: Card, now: string): number {
  return Math.round(100 * retrievabilityAt(card, now))
}

/** Whether an item asks for code or a prediction, rather than a choice. */
function isCodeOrPredict(content: TopicContent, itemId: string): boolean {
  const type = content.recall[itemId]?.type
  if (type === 'predict_output' || type === 'parsons') return true
  const exercise = content.exercises[itemId]
  return exercise !== undefined && exercise.stage !== 'worked_example'
}

/**
 * The items for a review session: two from the topic's review pool, at
 * least one of them code or predict-the-output (ADR-0009). Items answered
 * longest ago come first, so a session doesn't repeat the previous one's
 * items while the pool has others.
 */
export function chooseReviewItems(
  content: TopicContent,
  attempts: Attempt[],
  count = ITEMS_PER_REVIEW,
): string[] {
  const pool = content.topic.review_pool.filter((id) => {
    const exercise = content.exercises[id]
    if (exercise) return STAGES[exercise.stage].followUp
    return content.recall[id] !== undefined
  })
  const last = lastAttempted(attempts, content.topic.id)
  const byAge = [...pool].sort(
    (a, b) =>
      (last.get(a) ?? '').localeCompare(last.get(b) ?? '') ||
      a.localeCompare(b),
  )
  const chosen: string[] = []
  const codeFirst = byAge.find((id) => isCodeOrPredict(content, id))
  if (codeFirst) chosen.push(codeFirst)
  for (const id of byAge) {
    if (chosen.length >= count) break
    if (!chosen.includes(id)) chosen.push(id)
  }
  return chosen
}

/**
 * How a session is rated from its items' first attempts (ADR-0009): all
 * correct is Good, some correct is Hard, none is Again.
 */
export function ratingOf(results: boolean[]): Rating {
  const correct = results.filter(Boolean).length
  if (correct === results.length && results.length > 0) return 'good'
  return correct > 0 ? 'hard' : 'again'
}

/** "tomorrow", "in 3 days", or "in about 2 months". */
export function describeGap(from: string, to: string): string {
  const days = Math.round((Date.parse(to) - Date.parse(from)) / 86_400_000)
  if (days <= 1) return 'tomorrow'
  if (days < 45) return `in ${days} days`
  const months = Math.round(days / 30)
  return `in about ${months} month${months === 1 ? '' : 's'}`
}
