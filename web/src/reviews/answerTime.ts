// Answer time in review ratings (ADR-0009, amended 2026-11-16). A review
// session with every item right is Good, unless one of those right answers
// took far longer than this learner usually needs for that kind of item:
// then it's Hard. Getting there slowly is a sign the memory is fading, and
// a Hard brings the next review sooner than a Good would.
//
// Everything is the learner's own history, worked out from the event log
// like the rest of progress. Where there's too little of it, or a time is
// missing, nothing changes: the session is rated as before.
import type { Attempt, ItemFacts, ItemsOf } from '../followups/followUps.ts'
import type { Rating } from './fsrs.ts'
import { ratingOf } from './reviews.ts'

/** A right answer this many times the learner's usual time is slow... */
export const SLOW_FACTOR = 3
/**
 * ...as long as it also took longer than this. A quick check usually takes
 * a learner 10 to 20 seconds, and half a minute over that is reading
 * carefully, not struggling.
 */
export const SLOW_FLOOR_MS = 60_000
/** A kind of item needs this many timed right answers before it's judged. */
export const MIN_TIMED_ANSWERS = 10
/** The usual time is the median of this many most recent right answers. */
export const RECENT_ANSWERS = 50
/**
 * Longer times count as this long: someone who left an item open over lunch
 * didn't take an hour over it (the practice-hours tracker caps the same).
 */
export const LONGEST_COUNTED_MS = 30 * 60_000

/** How long this learner usually takes to get each kind of item right, in ms. */
export type UsualTimes = ReadonlyMap<string, number>

/**
 * The kind of an item, for comparing times: a question's type ("mcq",
 * "parsons"...) or a Python exercise's stage ("code:write"). Labs aren't
 * timed: their time includes building and starting a container, which says
 * nothing about memory. Nor are worked examples, which aren't recall.
 */
export function kindOf(item: ItemFacts | undefined): string | undefined {
  if (!item) return undefined
  if (item.type) return item.type
  if (item.runtime === 'lab') return undefined
  if (!item.stage || item.stage === 'worked_example') return undefined
  return `code:${item.stage}`
}

/** The middle value of a list that isn't empty. */
function median(values: number[]): number {
  const sorted = values.toSorted((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 1
    ? (sorted[middle] ?? 0)
    : ((sorted[middle - 1] ?? 0) + (sorted[middle] ?? 0)) / 2
}

/**
 * How long the learner usually takes to get each kind of item right: the
 * median of their most recent timed right answers (and passing Checks), in
 * any context but the placement test. Kinds with fewer than
 * MIN_TIMED_ANSWERS are left out, so they're never judged slow.
 */
export function usualTimes(attempts: Attempt[], itemsOf: ItemsOf): UsualTimes {
  const byKind = new Map<string, { at: string; ms: number }[]>()
  for (const attempt of attempts) {
    if (attempt.type !== 'answer' && attempt.type !== 'code_check') continue
    if (!attempt.correct || attempt.context === 'placement') continue
    const ms = attempt.duration_ms
    if (typeof ms !== 'number' || !(ms > 0)) continue
    const items = itemsOf(attempt.topic_id)
    const item =
      items && Object.hasOwn(items, attempt.item_id)
        ? items[attempt.item_id]
        : undefined
    const kind = kindOf(item)
    if (!kind) continue
    const list = byKind.get(kind) ?? []
    list.push({ at: attempt.occurred_at, ms: Math.min(ms, LONGEST_COUNTED_MS) })
    byKind.set(kind, list)
  }
  const usual = new Map<string, number>()
  for (const [kind, list] of byKind) {
    if (list.length < MIN_TIMED_ANSWERS) continue
    const recent = list
      .toSorted((a, b) => a.at.localeCompare(b.at))
      .slice(-RECENT_ANSWERS)
    usual.set(kind, median(recent.map(({ ms }) => ms)))
  }
  return usual
}

/** One item of a review session, as it was answered. */
export type SessionAnswer = {
  itemId: string
  correct: boolean
  /** How long it took; null or left out when not known. */
  durationMs?: number | null
  /** kindOf the item; left out for one that isn't timed. */
  kind?: string
}

/** The time above which a right answer of this kind is slow, if it's judged. */
export function slowAfter(
  kind: string | undefined,
  usual: UsualTimes,
): number | undefined {
  const time = kind === undefined ? undefined : usual.get(kind)
  return time === undefined
    ? undefined
    : Math.max(SLOW_FACTOR * time, SLOW_FLOOR_MS)
}

/** The right answers that took far longer than the learner usually needs. */
export function slowAnswers(
  answers: SessionAnswer[],
  usual: UsualTimes,
): string[] {
  return answers
    .filter(({ correct, durationMs, kind }) => {
      const limit = slowAfter(kind, usual)
      return (
        correct &&
        limit !== undefined &&
        typeof durationMs === 'number' &&
        durationMs > limit
      )
    })
    .map(({ itemId }) => itemId)
}

/**
 * A session's rating: all right is Good, some right Hard, none Again
 * (ratingOf), except that all right with a slow answer among them is Hard.
 * Also which right answers were slow, and whether that made it Hard.
 */
export function rateSession(
  answers: SessionAnswer[],
  usual: UsualTimes,
): { rating: Rating; slow: string[]; slowed: boolean } {
  const rating = ratingOf(answers.map(({ correct }) => correct))
  const slow = slowAnswers(answers, usual)
  const slowed = rating === 'good' && slow.length > 0
  return { rating: slowed ? 'hard' : rating, slow, slowed }
}
