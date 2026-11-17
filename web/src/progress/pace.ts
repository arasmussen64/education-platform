import type { Topic } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import { countedMs, MAX_ATTEMPT_MS } from './practiceTime.ts'
import type { TopicProgress } from './progress.ts'

// Honest times. A topic's `estimated_minutes` is the author's guess for the
// whole topic: reading the lesson, practising and proving it. Guesses tend
// to be low, so the Today page compares them with how long the learner's own
// proven topics took, and stretches its time figures when they ran long.
//
// What can be measured, and what can't. An attempt's `duration_ms` counts
// only the time on that question, not reading, so adding those up would
// make every topic look quicker than it was. Instead this measures the time
// a learner spent in a topic: its events grouped into sittings (a gap of
// more than 30 minutes starts a new one), each sitting counted from its
// first event to its last, plus the time spent on that first question. That
// includes reading between questions, but not the reading before the first
// question of a sitting, which leaves no trace. So the measure is a floor:
// the true time is at least this. A floor can show that topics take longer
// than their estimates, never that they take less, so the times are only
// ever stretched, never shrunk.

/** A gap longer than this between two events starts a new sitting. */
export const SITTING_GAP_MS = MAX_ATTEMPT_MS

/** Pacing is shown once this many topics have been proven and measured. */
export const MIN_TOPICS_FOR_PACE = 3

/** Minutes per review question until the learner has answered enough. */
export const DEFAULT_REVIEW_ITEM_MINUTES = 1

/** Review questions answered before their own times are used. */
export const MIN_REVIEW_ITEMS = 5

export type Pace = {
  /**
   * The middle (median) of the proven topics' measured time divided by
   * their estimates, to one decimal place. 1.4 means "about 1.4 times".
   */
  ratio: number
  /** How many proven topics it comes from. */
  topics: number
}

/** The middle value of a non-empty list. */
function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 1
    ? sorted[middle]
    : (sorted[middle - 1] + sorted[middle]) / 2
}

/**
 * The time spent in one topic up to `until`, from its events (sorted or
 * not), counted by sittings as above. Reviews, the placement test and the
 * Today page's questions (the review context) aren't part of learning it.
 */
export function timeInTopic(
  attempts: Attempt[],
  topicId: string,
  until: string,
): number {
  const times = attempts
    .filter(
      (attempt) =>
        attempt.topic_id === topicId &&
        attempt.type !== 'review' &&
        attempt.context !== 'review' &&
        attempt.context !== 'placement' &&
        attempt.occurred_at <= until,
    )
    .sort((a, b) => a.occurred_at.localeCompare(b.occurred_at))
  let total = 0
  let start: Attempt | undefined
  let last = 0
  for (const attempt of times) {
    const at = Date.parse(attempt.occurred_at)
    if (start === undefined || at - last > SITTING_GAP_MS) {
      // A new sitting: it began when the learner started on this question.
      if (start !== undefined) total += last - Date.parse(start.occurred_at)
      total += countedMs(attempt)
      start = attempt
    }
    last = at
  }
  if (start !== undefined) total += last - Date.parse(start.occurred_at)
  return total
}

/**
 * The learner's pace, from the topics they have proven (Learned, or Passed
 * for a checkpoint): null until there are MIN_TOPICS_FOR_PACE of them with
 * time to measure.
 */
export function topicPace(
  topics: Topic[],
  progress: Map<string, TopicProgress>,
  attempts: Attempt[],
): Pace | null {
  const ratios: number[] = []
  for (const topic of topics) {
    const learnedAt = progress.get(topic.id)?.learnedAt
    if (!learnedAt || topic.estimated_minutes <= 0) continue
    const ms = timeInTopic(attempts, topic.id, learnedAt)
    // Proven with nothing to measure (say, all on another device before
    // times were saved): it says nothing about pace.
    if (ms <= 0) continue
    ratios.push(ms / 60_000 / topic.estimated_minutes)
  }
  if (ratios.length < MIN_TOPICS_FOR_PACE) return null
  return {
    ratio: Math.round(median(ratios) * 10) / 10,
    topics: ratios.length,
  }
}

/**
 * An estimate in minutes, stretched to the learner's pace. Only stretched:
 * the measure is a floor (see above), so a pace under 1 leaves it as it is.
 */
export function paced(minutes: number, pace: Pace | null): number {
  if (!pace || pace.ratio <= 1) return minutes
  return Math.round(minutes * pace.ratio)
}

/** Whether the pace changes the times shown at all. */
export function stretches(pace: Pace | null): pace is Pace {
  return pace !== null && pace.ratio > 1
}

/**
 * Minutes per review question, from the learner's own answers in the
 * review context (reviews, and the Today page's mistakes coming back): the
 * median, once there are MIN_REVIEW_ITEMS of them, else a default.
 */
export function reviewItemMinutes(attempts: Attempt[]): number {
  const times = attempts
    .filter((attempt) => attempt.context === 'review')
    .map(countedMs)
    .filter((ms) => ms > 0)
  if (times.length < MIN_REVIEW_ITEMS) return DEFAULT_REVIEW_ITEM_MINUTES
  return median(times) / 60_000
}

/** "about 1.4×" for a ratio. */
export function formatRatio(ratio: number): string {
  return `${ratio.toFixed(1)}×`
}
