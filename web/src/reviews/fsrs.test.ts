import { describe, expect, it } from 'vitest'
import {
  daysBetween,
  type Grade,
  initialState,
  intervalDays,
  MAX_INTERVAL_DAYS,
  nextState,
  type Rating,
  replayCard,
  retrievability,
  retrievabilityAt,
  type Review,
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

  it('finds a topic harder after Again or Hard, and Good leaves a fresh one as it was', () => {
    const start = initialState('good')
    expect(nextState(start, 'again', 3).difficulty).toBeGreaterThan(
      start.difficulty,
    )
    expect(nextState(start, 'hard', 3).difficulty).toBeGreaterThan(
      start.difficulty,
    )
    // Good moves nothing, and the pull back is toward where a first Good
    // starts (FSRS-4.5's D0(3)), so a fresh topic's difficulty stays put.
    expect(nextState(start, 'good', 3).difficulty).toBe(start.difficulty)
    expect(nextState(start, 'easy', 3).difficulty).toBeLessThan(
      start.difficulty,
    )
    // After a lapse, Goods bring it back down toward the start.
    const lapsed = nextState(start, 'again', 3)
    const recovered = nextState(lapsed, 'good', 1)
    expect(recovered.difficulty).toBeLessThan(lapsed.difficulty)
    expect(recovered.difficulty).toBeGreaterThan(start.difficulty)
    // Never outside 1 to 10, however many lapses.
    let state = start
    for (let i = 0; i < 30; i++) state = nextState(state, 'again', 1)
    expect(state.difficulty).toBeLessThanOrEqual(10)
  })

  it('never makes a memory more stable by forgetting it, even after a long break', () => {
    const start = initialState('good')
    // 200 days after a 4-day stability, recall is about 27%: the lapse
    // formula alone would give 3.85 days, more than the 3.71 before.
    const lapsed = nextState(start, 'again', 200)
    expect(lapsed.stability).toBe(start.stability)
  })

  it('keeps stability at 0.01 days or more, however many lapses', () => {
    // A day apart, lapses level off near 0.14 days on their own.
    let daily = initialState('good')
    for (let i = 0; i < 40; i++) daily = nextState(daily, 'again', 1)
    expect(daily.stability).toBeCloseTo(0.1439, 4)
    // With no time between them (two sessions saved at once, say), each
    // lapse would roughly halve it, toward zero: the floor stops that.
    let atOnce = initialState('good')
    for (let i = 0; i < 40; i++) atOnce = nextState(atOnce, 'again', 0)
    expect(atOnce.stability).toBe(0.01)
  })

  it('rewards a review that was overdue more than an early one', () => {
    const start = initialState('good')
    const early = nextState(start, 'good', 1)
    const late = nextState(start, 'good', 20)
    expect(late.stability).toBeGreaterThan(early.stability)
  })
})

// Each row is [the grade, then stability, difficulty and the next interval
// in days after it]. The first row is becoming Learned, a first Good.
// Computed with py-fsrs 2.5.1, the reference FSRS-4.5 package, from its own
// formulas (init_stability, init_difficulty, next_recall_stability,
// next_forget_stability, next_difficulty, next_interval with a 365-day
// maximum), not from this file. Every review is taken on the day it falls
// due unless the row says otherwise.
type Golden = [Grade | 'learned', number, number, number]

const GOLDEN: Record<string, Golden[]> = {
  'Good, Good, Good': [
    ['learned', 3.7145, 5.1618, 4],
    ['good', 14.80810051, 5.1618, 15],
    ['good', 49.46160495, 5.1618, 49],
    ['good', 145.67063221, 5.1618, 146],
  ],
  'Again, then Good': [
    ['learned', 3.7145, 5.1618, 4],
    ['again', 1.43323449, 6.901155, 1],
    ['good', 3.73766709, 6.84723499, 4],
  ],
  'Hard, Good, Easy': [
    ['learned', 3.7145, 5.1618, 4],
    ['hard', 6.23496604, 6.0314775, 6],
    ['good', 19.57942234, 6.0045175, 20],
    ['easy', 128.91174014, 5.10871576, 129],
  ],
  'a long run with Hards and two lapses in a row': [
    ['learned', 3.7145, 5.1618, 4],
    ['good', 14.80810051, 5.1618, 15],
    ['hard', 22.68137672, 6.0314775, 23],
    ['again', 3.84807063, 7.7438725, 4],
    ['again', 1.41277028, 9.40318325, 1],
    ['good', 2.31135073, 9.27170037, 2],
    ['good', 4.10082328, 9.14429346, 4],
    ['hard', 4.89919655, 9.89051366, 5],
    ['good', 7.45076772, 9.74392354, 7],
    ['good', 11.30069611, 9.60187771, 11],
    ['good', 17.64047186, 9.4642353, 18],
    ['good', 28.3129045, 9.3308598, 28],
  ],
  'nine Goods, reaching the 365-day limit': [
    ['learned', 3.7145, 5.1618, 4],
    ['good', 14.80810051, 5.1618, 15],
    ['good', 49.46160495, 5.1618, 49],
    ['good', 145.67063221, 5.1618, 146],
    ['good', 392.69789847, 5.1618, 365],
    ['good', 935.9103602, 5.1618, 365],
    ['good', 1446.20467285, 5.1618, 365],
    ['good', 1934.30999095, 5.1618, 365],
    ['good', 2406.71548267, 5.1618, 365],
    ['good', 2867.11915592, 5.1618, 365],
  ],
}

/** The same sequence through this file's formulas, on due days. */
function onDueDays(grades: Grade[]): Golden[] {
  let state = initialState('good')
  let interval = intervalDays(state.stability)
  const rows: Golden[] = [
    ['learned', state.stability, state.difficulty, interval],
  ]
  for (const grade of grades) {
    state = nextState(state, grade, interval)
    interval = intervalDays(state.stability)
    rows.push([grade, state.stability, state.difficulty, interval])
  }
  return rows
}

function expectRows(actual: Golden[], expected: Golden[]) {
  expect(actual).toHaveLength(expected.length)
  actual.forEach(([grade, stability, difficulty, interval], index) => {
    const [wantGrade, wantStability, wantDifficulty, wantInterval] =
      expected[index]!
    expect(grade).toBe(wantGrade)
    expect(stability).toBeCloseTo(wantStability, 6)
    expect(difficulty).toBeCloseTo(wantDifficulty, 6)
    expect(interval).toBe(wantInterval)
  })
}

describe('FSRS-4.5, against the reference implementation', () => {
  for (const [name, expected] of Object.entries(GOLDEN)) {
    it(`matches py-fsrs 2.5.1 for ${name}`, () => {
      const grades = expected.slice(1).map(([grade]) => grade as Grade)
      expectRows(onDueDays(grades), expected)
    })
  }

  it('matches it for reviews taken early, late and very late', () => {
    // [grade, days since the last review]
    const steps: [Grade, number][] = [
      ['good', 2],
      ['good', 30],
      ['hard', 5],
      ['again', 90],
      ['good', 1],
    ]
    let state = initialState('good')
    const rows: Golden[] = [['learned', state.stability, state.difficulty, 4]]
    for (const [grade, elapsed] of steps) {
      state = nextState(state, grade, elapsed)
      rows.push([
        grade,
        state.stability,
        state.difficulty,
        intervalDays(state.stability),
      ])
    }
    expectRows(rows, [
      ['learned', 3.7145, 5.1618, 4],
      ['good', 9.57481392, 5.1618, 10],
      ['good', 70.64406134, 5.1618, 71],
      ['hard', 72.98642362, 6.0314775, 73],
      ['again', 6.72000785, 7.7438725, 7],
      ['good', 8.29234722, 7.66382825, 8],
    ])
  })

  it('gives the same card through replayCard as through the formulas', () => {
    const expected = GOLDEN['a long run with Hards and two lapses in a row']!
    const reviews: Review[] = []
    let card = replayCard(day(0), reviews)
    for (const [grade] of expected.slice(1)) {
      reviews.push({ at: card.due, rating: grade as Rating })
      card = replayCard(day(0), reviews)
    }
    const last = expected.at(-1)!
    expect(card.stability).toBeCloseTo(last[1], 6)
    expect(card.difficulty).toBeCloseTo(last[2], 6)
    expect(daysBetween(card.lastReview, card.due)).toBe(last[3])
    expect(card.lapses).toBe(2)
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
