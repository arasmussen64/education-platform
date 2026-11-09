import type { Attempt } from '../followups/followUps.ts'

// Deliberate practice, added up (roadmap, Phase 2; docs/learning-science.md):
// the time spent on graded answers, Checks of code, explanations and reviews,
// not time with the site open. An attempt's duration runs from the learner's
// first touch of the item, or their previous attempt at it, to this one
// (useAttemptTimer), so reading the lesson above never counts.

/**
 * The most one attempt can count. A longer gap means the learner walked
 * away with the page open, and that isn't practice.
 */
export const MAX_ATTEMPT_MS = 30 * 60 * 1000

/** The hours worth marking on the way to 10,000. */
export const MILESTONE_HOURS = [
  1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000,
]

const MINUTE_MS = 60 * 1000
const HOUR_MS = 60 * MINUTE_MS
const WEEK_MS = 7 * 24 * HOUR_MS

export type PracticeTime = {
  /** All deliberate practice so far. */
  totalMs: number
  /** The part of it in the last seven days. */
  recentMs: number
  /** How many attempts had a duration to count. */
  attempts: number
}

/** What one attempt counts for: its duration, capped; nothing if unknown. */
export function countedMs(attempt: Attempt): number {
  const ms = attempt.duration_ms
  if (ms == null || !Number.isFinite(ms) || ms <= 0) return 0
  return Math.min(ms, MAX_ATTEMPT_MS)
}

/** The practice time in these attempts, as of `now` (ISO format). */
export function practiceTime(attempts: Attempt[], now: string): PracticeTime {
  const weekAgo = new Date(now).getTime() - WEEK_MS
  let totalMs = 0
  let recentMs = 0
  let counted = 0
  for (const attempt of attempts) {
    const ms = countedMs(attempt)
    if (ms === 0) continue
    counted += 1
    totalMs += ms
    if (new Date(attempt.occurred_at).getTime() >= weekAgo) recentMs += ms
  }
  return { totalMs, recentMs, attempts: counted }
}

/** The next milestone to reach, and how far off it is; null past the last. */
export function nextMilestone(
  totalMs: number,
): { hours: number; remainingMs: number } | null {
  const hours = MILESTONE_HOURS.find((each) => each * HOUR_MS > totalMs)
  if (hours === undefined) return null
  return { hours, remainingMs: hours * HOUR_MS - totalMs }
}

/** "2 hours 15 minutes", "1 hour", "15 minutes" or "under a minute". */
export function formatDuration(ms: number): string {
  const minutes = Math.floor(ms / MINUTE_MS)
  if (minutes < 1) return 'under a minute'
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  const parts: string[] = []
  if (hours > 0) parts.push(`${hours} ${hours === 1 ? 'hour' : 'hours'}`)
  if (rest > 0) parts.push(`${rest} ${rest === 1 ? 'minute' : 'minutes'}`)
  return parts.join(' ')
}

/** "10 hours", "1 hour", with thousands separated: "10,000 hours". */
export function formatHours(hours: number): string {
  return `${hours.toLocaleString('en-US')} ${hours === 1 ? 'hour' : 'hours'}`
}
