// A personal forgetting curve (ADR-0009, amended 2026-11-16). FSRS's
// default parameters describe an average learner. Once this learner has
// enough reviews, one number is fitted to them: how many times longer (or
// shorter) their memory lasts than the average curve says. Intervals are
// then that many times as long.
//
// Modest on purpose: one number, not FSRS's seventeen (fitting those is the
// ML capstone's job), clamped to a safe range, and nothing until there are
// enough reviews to say something. Like everything else, it's worked out
// from the event log on every visit; nothing is stored.
import type { TopicProgress } from '../progress/progress.ts'
import { addDays, intervalDays, retrievability } from './fsrs.ts'
import { type ReviewPoint, replayWithCredits } from './implicit.ts'

/** Nothing is fitted before this many review outcomes. */
export const MIN_REVIEWS = 100
/** The multiplier never goes outside this range. */
export const LOWEST = 0.5
export const HIGHEST = 2
/** It's rounded to this, so one more review doesn't nudge every date. */
export const ROUNDING = 0.05

/** The learner's fitted curve: the multiplier, and how many reviews it rests on. */
export type PersonalCurve = {
  /** 1 until there are MIN_REVIEWS outcomes. */
  multiplier: number
  reviews: number
}

/**
 * How well a multiplier explains the reviews: the log-likelihood of what
 * happened (remembered or not) under the recall each review was predicted
 * to have with stability × multiplier. Higher is better.
 */
export function logLikelihood(
  points: ReviewPoint[],
  multiplier: number,
): number {
  let total = 0
  for (const { stability, elapsedDays, recalled } of points) {
    const p = retrievability(elapsedDays, stability * multiplier)
    // Never exactly 0 or 1, so one surprise can't make it minus infinity.
    const clamped = Math.min(1 - 1e-6, Math.max(1e-6, p))
    total += Math.log(recalled ? clamped : 1 - clamped)
  }
  return total
}

/**
 * The multiplier that best explains the reviews (maximum likelihood),
 * searched over LOWEST to HIGHEST in small even steps on a log scale, then
 * rounded to ROUNDING. A search over one number needs nothing cleverer, and
 * it can't fail to converge.
 */
export function fitMultiplier(points: ReviewPoint[]): number {
  const steps = 400
  let best = 1
  let bestScore = -Infinity
  for (let step = 0; step <= steps; step++) {
    const multiplier = LOWEST * (HIGHEST / LOWEST) ** (step / steps)
    const score = logLikelihood(points, multiplier)
    if (score > bestScore) {
      bestScore = score
      best = multiplier
    }
  }
  const rounded = Math.round(best / ROUNDING) * ROUNDING
  return Math.min(HIGHEST, Math.max(LOWEST, Number(rounded.toFixed(2))))
}

/** Every real review's prediction, across the learner's Learned topics. */
export function reviewPointsOf(
  progress: Map<string, TopicProgress>,
): ReviewPoint[] {
  const points: ReviewPoint[] = []
  for (const entry of progress.values()) {
    if (!entry.card || !entry.learnedAt) continue
    points.push(
      ...replayWithCredits(entry.learnedAt, entry.reviews, entry.credits)
        .points,
    )
  }
  return points
}

/** The learner's curve, from every topic's reviews. */
export function personalCurve(
  progress: Map<string, TopicProgress>,
): PersonalCurve {
  const points = reviewPointsOf(progress)
  return {
    multiplier: points.length < MIN_REVIEWS ? 1 : fitMultiplier(points),
    reviews: points.length,
  }
}

/**
 * The progress with every card scheduled by the multiplier: due after
 * stability × multiplier days, and its recall worked out the same way.
 * A multiplier of 1 changes nothing.
 */
export function withPersonalCurve(
  progress: Map<string, TopicProgress>,
  multiplier: number,
): Map<string, TopicProgress> {
  if (multiplier === 1) return progress
  return new Map(
    [...progress].map(([topicId, entry]) => {
      const { card } = entry
      if (!card) return [topicId, entry]
      return [
        topicId,
        {
          ...entry,
          card: {
            ...card,
            due: addDays(
              card.lastReview,
              intervalDays(card.stability * multiplier),
            ),
            personal: multiplier,
          },
        },
      ]
    }),
  )
}

/** The curve in plain words, for the Account page. */
export function describeCurve({ multiplier, reviews }: PersonalCurve): string {
  if (reviews < MIN_REVIEWS) {
    const left = MIN_REVIEWS - reviews
    return `Your reviews are timed by the average forgetting curve for now. After ${MIN_REVIEWS} reviews the app fits the curve to you; ${left === 1 ? 'one more to go' : `${left} more to go`}.`
  }
  const percent = Math.round(Math.abs(1 - multiplier) * 100)
  const basis = `Worked out from your ${reviews} reviews, and again after each new one.`
  if (percent === 0) {
    return `You forget at about the average rate, so reviews come when the average curve says. ${basis}`
  }
  const degree = percent <= 25 ? 'a little ' : ''
  if (multiplier < 1) {
    return `You forget ${degree}faster than average: reviews come about ${percent}% sooner. ${basis}`
  }
  return `You remember ${degree}longer than average: reviews come about ${percent}% later. ${basis}`
}
