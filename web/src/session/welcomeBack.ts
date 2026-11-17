// A calm plan for coming back. After a break, or whenever more reviews are
// due than the daily limit can clear, a long list of overdue topics is the
// moment people give up: it reads as a debt. So the Today page shows the
// same reviews as a plan instead: the most faded first, spread over the
// next few days within the daily limit, with about how long each day takes.
//
// It changes the message and nothing else. The topics, their order (most
// faded first) and the limit of 20 a day (ADR-0009) are the reviews
// engine's own; this only reads them and sets them out by day.
import type { Topic } from '../content/types.ts'
import { addDays, type Day, dayOf } from '../days.ts'
import type { Attempt } from '../followups/followUps.ts'
import { reviewItemMinutes } from '../progress/pace.ts'
import type { TopicProgress } from '../progress/progress.ts'
import {
  DAILY_REVIEW_LIMIT,
  type DueReview,
  dueReviews,
  ITEMS_PER_REVIEW,
  reviewsLeftToday,
} from '../reviews/reviews.ts'

/** A gap of this many days or more since the last practice is a break. */
export const BREAK_DAYS = 7

/** One day of the plan. */
export type PlanDay = {
  day: Day
  /** That day's reviews, most faded first. */
  reviews: DueReview[]
  /** About how long they take, in whole minutes. */
  minutes: number
}

export type WelcomeBack = {
  /** Days since the last practice before today, when that was a break. */
  breakDays: number | null
  /** Every topic due now. */
  due: number
  /** The reviews set out by day, from today. Empty when none are due. */
  days: PlanDay[]
}

/** Whole calendar days from `from` to `to`. */
function daysFrom(from: Day, to: Day): number {
  const utc = (day: Day) => {
    const [year = 0, month = 1, date = 1] = day.split('-').map(Number)
    return Date.UTC(year, month - 1, date)
  }
  return Math.round((utc(to) - utc(from)) / 86_400_000)
}

/**
 * How many days the learner has been away: from their last day of practice
 * to `today`. Null if they have practised today already (they are back), or
 * never have. The placement test isn't practice.
 */
function daysAway(attempts: Attempt[], today: Day): number | null {
  let last: Day | null = null
  for (const attempt of attempts) {
    if (attempt.context === 'placement') continue
    const day = dayOf(attempt)
    if (day >= today) return null
    if (last === null || day > last) last = day
  }
  return last === null ? null : daysFrom(last, today)
}

/**
 * The welcome-back plan as of `now`, or null when there's no need for one:
 * the learner hasn't been away BREAK_DAYS or more, and no more reviews are
 * due than a day's limit can clear. `topics` are the ones that can be
 * opened.
 */
export function welcomeBack({
  topics,
  progress,
  attempts,
  now,
  limit = DAILY_REVIEW_LIMIT,
}: {
  topics: Topic[]
  progress: Map<string, TopicProgress>
  attempts: Attempt[]
  now: string
  limit?: number
}): WelcomeBack | null {
  const today = dayOf(now)
  const all = dueReviews(topics, progress, now, Number.POSITIVE_INFINITY)
  const left = reviewsLeftToday(attempts, now, limit)
  const away = daysAway(attempts, today)
  const breakDays = away !== null && away >= BREAK_DAYS ? away : null
  if (breakDays === null && all.length <= limit) return null

  const perReview = ITEMS_PER_REVIEW * reviewItemMinutes(attempts)
  const days: PlanDay[] = []
  let rest = all
  // A limit of 0 would never place anything: stop rather than loop.
  for (let offset = 0; rest.length > 0 && limit > 0; offset += 1) {
    const room = offset === 0 ? left : limit
    if (room === 0) continue
    const reviews = rest.slice(0, room)
    rest = rest.slice(room)
    days.push({
      day: addDays(today, offset),
      reviews,
      minutes: Math.ceil(reviews.length * perReview),
    })
  }
  return { breakDays, due: all.length, days }
}

/** "Today", "Tomorrow", or "Thursday, Nov 19". */
export function dayLabel(day: Day, today: Day): string {
  if (day === today) return 'Today'
  if (day === addDays(today, 1)) return 'Tomorrow'
  const [year = 0, month = 1, date = 1] = day.split('-').map(Number)
  return new Date(year, month - 1, date, 12).toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  })
}
