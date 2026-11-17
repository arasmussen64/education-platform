import { describe, expect, it } from 'vitest'
import { progressOf } from '../progress/progress.ts'
import { fakeTopic } from '../test/fakeContent.tsx'
import { replayCard, retrievability, retrievabilityAt } from './fsrs.ts'
import type { ReviewPoint } from './implicit.ts'
import {
  describeCurve,
  fitMultiplier,
  HIGHEST,
  logLikelihood,
  LOWEST,
  MIN_REVIEWS,
  personalCurve,
  withPersonalCurve,
} from './personal.ts'

/** A small seeded random number generator, so the tests are repeatable. */
function generator(seed: number) {
  let state = seed
  return () => {
    state = (state * 1_103_515_245 + 12_345) % 2_147_483_648
    return state / 2_147_483_648
  }
}

/**
 * `count` reviews by a learner whose memory lasts `truth` times what the
 * average curve says: each remembered with the chance that learner has.
 */
function reviewsBy(truth: number, count: number, seed = 1): ReviewPoint[] {
  const random = generator(seed)
  return Array.from({ length: count }, () => {
    const stability = 1 + random() * 60
    // Reviewed around when it falls due, give or take.
    const elapsedDays = stability * (0.5 + random())
    const chance = retrievability(elapsedDays, stability * truth)
    return { stability, elapsedDays, recalled: random() < chance }
  })
}

describe('fitMultiplier', () => {
  it('finds a learner who forgets faster, or slower, than average', () => {
    // Within 0.15 of the truth from 3,000 reviews: forgetting is rare, so
    // each review says only a little.
    for (const truth of [0.7, 1, 1.5]) {
      const fitted = fitMultiplier(reviewsBy(truth, 3000))
      expect(Math.abs(fitted - truth)).toBeLessThanOrEqual(0.15)
    }
  })

  it('is the multiplier the reviews are most likely under', () => {
    const points = reviewsBy(0.8, 500)
    const best = fitMultiplier(points)
    const score = logLikelihood(points, best)
    expect(score).toBeGreaterThan(logLikelihood(points, best + 0.2))
    expect(score).toBeGreaterThan(logLikelihood(points, best - 0.2))
  })

  it('stays inside its safe range, rounded to a twentieth', () => {
    const all = reviewsBy(1, 200).map((point) => ({
      ...point,
      recalled: true,
    }))
    const none = all.map((point) => ({ ...point, recalled: false }))
    expect(fitMultiplier(all)).toBe(HIGHEST)
    expect(fitMultiplier(none)).toBe(LOWEST)
    const fitted = fitMultiplier(reviewsBy(0.83, 400))
    expect(Math.round(fitted * 20)).toBeCloseTo(fitted * 20, 6)
  })
})

describe('personalCurve', () => {
  const day = (n: number) =>
    new Date(Date.UTC(2026, 0, 1, 12) + n * 86_400_000).toISOString()

  /** `count` topics, each Learned on day 0 and reviewed on day 10 with this rating. */
  function history(count: number, rating: 'good' | 'again') {
    const topics = Array.from({ length: count }, (_, index) =>
      fakeTopic({ id: `csa.t${index}`, prerequisites: [] }),
    )
    const events = topics.flatMap((topic) => [
      ...[
        ['code_check', 'build-hello'],
        ['code_check', 'debug-hello'],
        ['explain_submit', null],
      ].map(([type, item_id]) => ({
        type: type as 'code_check' | 'explain_submit',
        topic_id: topic.id,
        item_id,
        correct: true,
        occurred_at: day(0),
      })),
      {
        type: 'review' as const,
        topic_id: topic.id,
        item_id: 'review',
        correct: rating === 'good',
        rating,
        occurred_at: day(10),
      },
    ])
    return progressOf(topics, events)
  }

  it(`changes nothing below ${MIN_REVIEWS} reviews`, () => {
    const curve = personalCurve(history(MIN_REVIEWS - 1, 'again'))
    expect(curve).toEqual({ multiplier: 1, reviews: MIN_REVIEWS - 1 })
  })

  it(`fits from ${MIN_REVIEWS} reviews: every one failed means faster forgetting`, () => {
    const curve = personalCurve(history(MIN_REVIEWS, 'again'))
    expect(curve.reviews).toBe(MIN_REVIEWS)
    expect(curve.multiplier).toBe(LOWEST)
  })
})

describe('withPersonalCurve', () => {
  const topic = fakeTopic({ prerequisites: [] })
  const learned = progressOf(
    [topic],
    [
      ['code_check', 'build-hello'],
      ['code_check', 'debug-hello'],
      ['explain_submit', null],
    ].map(([type, item_id]) => ({
      type: type as 'code_check' | 'explain_submit',
      topic_id: topic.id,
      item_id,
      correct: true,
      occurred_at: '2026-01-01T12:00:00.000Z',
    })),
  )

  it('changes nothing at 1', () => {
    expect(withPersonalCurve(learned, 1)).toBe(learned)
  })

  it('schedules by stability × multiplier, and works recall out the same way', () => {
    // The first card: stability 3.71 days, due after 4.
    const card = learned.get(topic.id)?.card
    expect(card).toEqual(replayCard('2026-01-01T12:00:00.000Z', []))
    const slower = withPersonalCurve(learned, 2).get(topic.id)?.card
    const faster = withPersonalCurve(learned, 0.5).get(topic.id)?.card
    // 3.71 × 2 = 7.43, so 7 days; 3.71 × 0.5 = 1.86, so 2.
    expect(slower?.due).toBe('2026-01-08T12:00:00.000Z')
    expect(faster?.due).toBe('2026-01-03T12:00:00.000Z')
    // Recall still reaches 90% when the stretched interval is up.
    expect(retrievabilityAt(slower!, '2026-01-08T12:00:00.000Z')).toBeCloseTo(
      retrievability(7, 3.7145 * 2),
      6,
    )
  })
})

describe('describeCurve', () => {
  it('says how many reviews are left before it fits', () => {
    expect(describeCurve({ multiplier: 1, reviews: 40 })).toBe(
      'Your reviews are timed by the average forgetting curve for now. After 100 reviews the app fits the curve to you; 60 more to go.',
    )
  })

  it('says it in plain words, with how much sooner or later', () => {
    expect(describeCurve({ multiplier: 0.8, reviews: 140 })).toBe(
      'You forget a little faster than average: reviews come about 20% sooner. Worked out from your 140 reviews, and again after each new one.',
    )
    expect(describeCurve({ multiplier: 1.5, reviews: 300 })).toMatch(
      /^You remember longer than average: reviews come about 50% later\./,
    )
    expect(describeCurve({ multiplier: 1, reviews: 300 })).toMatch(
      /^You forget at about the average rate/,
    )
  })
})
