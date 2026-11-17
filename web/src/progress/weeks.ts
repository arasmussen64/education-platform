import { type Day, dayOf } from '../days.ts'
import type { Attempt } from '../followups/followUps.ts'

// Consistency counted in weeks, not a daily streak. A streak turns one
// missed day into a loss ("you lost your 40-day streak"), and fear of that
// loss pushes people to cram or to quit after the first break. Spaced
// practice needs regular returns, not every day, so the Today page counts
// the weeks with any practice in them: "You practised in 4 of the last 5
// weeks." A missed day costs nothing, and a missed week is one out of five.
//
// A "week" is seven days ending today, then the seven before those, and so
// on, in the learner's own calendar days (each event's recorded local_day,
// days.ts). Rolling weeks, not Monday-to-Sunday ones, so the current week
// is always a whole seven days and nothing resets on a Monday morning.

/** How many weeks the count looks back over. */
export const WEEKS_COUNTED = 5

export type WeeksPractised = {
  /** How many of the weeks had practice in them. */
  practised: number
  /**
   * How many weeks were counted: WEEKS_COUNTED, or fewer for a learner who
   * started more recently, so a new learner isn't shown "1 of 5".
   */
  weeks: number
  /** Whether each week had practice, the current week first. */
  byWeek: boolean[]
}

/** Whole calendar days from `from` to `to` (both "YYYY-MM-DD"). */
function daysFrom(from: Day, to: Day): number {
  const utc = (day: Day) => {
    const [year = 0, month = 1, date = 1] = day.split('-').map(Number)
    return Date.UTC(year, month - 1, date)
  }
  return Math.round((utc(to) - utc(from)) / 86_400_000)
}

/**
 * The weeks with practice in them, up to `today`. Practice is any graded
 * attempt (an answer, a Check, an explanation, a review), except answers in
 * the placement test, which finds a starting point rather than practising.
 * Null when there is no practice at all.
 */
export function weeksPractised(
  attempts: Attempt[],
  today: Day,
  count = WEEKS_COUNTED,
): WeeksPractised | null {
  const byWeek = Array.from({ length: count }, () => false)
  let oldest = -1
  for (const attempt of attempts) {
    if (attempt.context === 'placement') continue
    const ago = daysFrom(dayOf(attempt), today)
    // An event dated after today (another device's clock running fast)
    // counts as today.
    const week = Math.floor(Math.max(0, ago) / 7)
    oldest = Math.max(oldest, week)
    if (week < count) byWeek[week] = true
  }
  if (oldest < 0) return null
  const weeks = Math.min(count, oldest + 1)
  const counted = byWeek.slice(0, weeks)
  return {
    practised: counted.filter(Boolean).length,
    weeks,
    byWeek: counted,
  }
}

/** The sentence for the Today page. Never a warning: only what was done. */
export function describeWeeks({ practised, weeks, byWeek }: WeeksPractised): {
  summary: string
  note: string | null
} {
  const summary =
    weeks === 1
      ? "You've practised this week."
      : practised === weeks
        ? `You practised in each of the last ${weeks} weeks.`
        : `You practised in ${practised} of the last ${weeks} weeks.`
  // Gain-framed, and only when this week has nothing in it yet.
  const note = byWeek[0] ? null : 'A session today counts for this week.'
  return { summary, note }
}
