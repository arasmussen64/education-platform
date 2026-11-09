import { describe, expect, it } from 'vitest'
import {
  initialState,
  intervalDays,
  MAX_INTERVAL_DAYS,
  nextState,
  replayCard,
  retrievability,
  retrievabilityAt,
} from './fsrs.ts'

const day = (n: number) => new Date(Date.UTC(2026, 10, 1 + n, 12)).toISOString()

describe('the forgetting curve', () => {
  it('is 90% when the days elapsed equal the stability', () => {
    expect(retrievability(5, 5)).toBeCloseTo(0.9, 6)
    expect(retrievability(20, 20)).toBeCloseTo(0.9, 6)
  })

  it('starts at 100% and falls as time passes', () => {
    expect(retrievability(0, 5)).toBe(1)
    expect(retrievability(10, 5)).toBeLessThan(retrievability(5, 5))
    expect(retrievability(50, 5)).toBeGreaterThan(0)
  })

  it('schedules the next review for when retention would reach 90%', () => {
    // With 90% requested, the interval is the stability itself, rounded.
    expect(intervalDays(4)).toBe(4)
    expect(intervalDays(12.4)).toBe(12)
    expect(intervalDays(0.3)).toBe(1)
    expect(intervalDays(10_000)).toBe(MAX_INTERVAL_DAYS)
  })
})

describe('memory states', () => {
  it('starts more stable after a better first rating', () => {
    expect(initialState('good').stability).toBeGreaterThan(
      initialState('hard').stability,
    )
    expect(initialState('hard').stability).toBeGreaterThan(
      initialState('again').stability,
    )
    for (const rating of ['again', 'hard', 'good'] as const) {
      const { difficulty } = initialState(rating)
      expect(difficulty).toBeGreaterThanOrEqual(1)
      expect(difficulty).toBeLessThanOrEqual(10)
    }
  })

  it('grows stability on Good, less on Hard, and shrinks it on Again', () => {
    const start = initialState('good')
    const good = nextState(start, 'good', start.stability)
    const hard = nextState(start, 'hard', start.stability)
    const again = nextState(start, 'again', start.stability)
    expect(good.stability).toBeGreaterThan(start.stability)
    expect(hard.stability).toBeGreaterThan(start.stability)
    expect(hard.stability).toBeLessThan(good.stability)
    expect(again.stability).toBeLessThan(start.stability)
  })

  it('finds a topic harder after Again and easier after Good', () => {
    const start = initialState('good')
    expect(nextState(start, 'again', 3).difficulty).toBeGreaterThan(
      start.difficulty,
    )
    expect(nextState(start, 'good', 3).difficulty).toBeLessThan(
      start.difficulty,
    )
    // Never outside 1 to 10, however many lapses.
    let state = start
    for (let i = 0; i < 30; i++) state = nextState(state, 'again', 1)
    expect(state.difficulty).toBeLessThanOrEqual(10)
  })

  it('rewards a review that was overdue more than an early one', () => {
    const start = initialState('good')
    const early = nextState(start, 'good', 1)
    const late = nextState(start, 'good', 20)
    expect(late.stability).toBeGreaterThan(early.stability)
  })
})

describe('replaying a card', () => {
  it('starts when the topic is Learned, with the first review a few days later', () => {
    const card = replayCard(day(0), [])
    expect(card.lastReview).toBe(day(0))
    expect(card.reviews).toBe(0)
    const dueInDays = (Date.parse(card.due) - Date.parse(day(0))) / 86_400_000
    expect(dueInDays).toBeGreaterThanOrEqual(2)
    expect(dueInDays).toBeLessThanOrEqual(7)
  })

  it('pushes the next review further out after each Good', () => {
    const first = replayCard(day(0), [])
    const second = replayCard(day(0), [{ at: first.due, rating: 'good' }])
    const third = replayCard(day(0), [
      { at: first.due, rating: 'good' },
      { at: second.due, rating: 'good' },
    ])
    const gap = (card: { lastReview: string; due: string }) =>
      Date.parse(card.due) - Date.parse(card.lastReview)
    expect(gap(second)).toBeGreaterThan(gap(first))
    expect(gap(third)).toBeGreaterThan(gap(second))
  })

  it('brings the next review closer after Again, and counts the lapse', () => {
    const first = replayCard(day(0), [])
    const lapsed = replayCard(day(0), [{ at: first.due, rating: 'again' }])
    const gapDays = (card: { lastReview: string; due: string }) =>
      (Date.parse(card.due) - Date.parse(card.lastReview)) / 86_400_000
    expect(gapDays(lapsed)).toBeLessThan(gapDays(first))
    expect(lapsed.lapses).toBe(1)
    expect(lapsed.reviews).toBe(1)
  })

  it('applies reviews in time order, and ignores any from before Learned', () => {
    const reviews = [
      { at: day(10), rating: 'good' as const },
      { at: day(4), rating: 'hard' as const },
      { at: day(-3), rating: 'again' as const },
    ]
    const card = replayCard(day(0), reviews)
    expect(card.reviews).toBe(2)
    expect(card.lapses).toBe(0)
    expect(card.lastReview).toBe(day(10))
    expect(card).toEqual(replayCard(day(0), [reviews[1]!, reviews[0]!]))
  })

  it('knows how much is likely remembered now', () => {
    const card = replayCard(day(0), [])
    expect(retrievabilityAt(card, day(0))).toBe(1)
    expect(retrievabilityAt(card, card.due)).toBeCloseTo(0.9, 1)
    expect(retrievabilityAt(card, day(60))).toBeLessThan(0.9)
  })
})
