import { describe, expect, it } from 'vitest'
import type { Topic } from '../content/types.ts'
import { type GradedEvent, progressOf, stateOf } from '../progress/progress.ts'
import { fakeCheckpointContent, fakeTopic } from '../test/fakeContent.tsx'
import { initialState, type Rating, replayCard, type Review } from './fsrs.ts'
import {
  type Credit,
  creditsFrom,
  creditWeights,
  implicitState,
  replayWithCredits,
} from './implicit.ts'

const day = (n: number) => new Date(Date.UTC(2026, 10, 1 + n, 12)).toISOString()
/** Whole days from day 0 to an ISO time. */
const dayNumber = (iso: string) =>
  (Date.parse(iso) - Date.parse(day(0))) / 86_400_000

const credit = (n: number, share = 0.5, from = 'csa.next'): Credit => ({
  at: day(n),
  share,
  from,
})
const review = (at: number | string, rating: Rating = 'good'): Review => ({
  at: typeof at === 'number' ? day(at) : at,
  rating,
})

// A chain, as in a track: A ← B ← C ← D ← E, and F built on B and on D.
// A checkpoint after A, and a topic after the checkpoint.
const topic = (id: string, prerequisites: string[]) =>
  fakeTopic({ id, prerequisites })
const A = topic('csa.a', [])
const B = topic('csa.b', ['csa.a'])
const C = topic('csa.c', ['csa.b'])
const D = topic('csa.d', ['csa.c'])
const E = topic('csa.e', ['csa.d'])
const F = topic('csa.f', ['csa.b', 'csa.d'])
const CHECKPOINT: Topic = {
  ...fakeCheckpointContent().topic,
  id: 'csa.m1.checkpoint',
  prerequisites: ['csa.a', 'csa.b'],
}
const AFTER = topic('csa.after', ['csa.m1.checkpoint'])
const ALL = [A, B, C, D, E, F, CHECKPOINT, AFTER]
const byId = new Map(ALL.map((each) => [each.id, each]))
const topicOf = (id: string) => byId.get(id)

describe('creditWeights', () => {
  it('gives a direct prerequisite 1, and halves at each step down, for three steps', () => {
    expect(creditWeights(E, topicOf)).toEqual(
      new Map([
        ['csa.d', 1],
        ['csa.c', 0.5],
        ['csa.b', 0.25],
      ]),
    )
  })

  it('takes the shortest path when two reach the same topic, never adding them up', () => {
    // F builds on B directly and through D and C.
    const weights = creditWeights(F, topicOf)
    expect(weights.get('csa.b')).toBe(1)
    expect(weights.get('csa.d')).toBe(1)
    expect(weights.get('csa.c')).toBe(0.5)
    expect(weights.get('csa.a')).toBe(0.5)
  })

  it("doesn't go through a checkpoint, which is a gate, not a use", () => {
    expect(creditWeights(AFTER, topicOf)).toEqual(new Map())
  })

  it("credits a checkpoint's direct prerequisites, whose skills its tests use", () => {
    expect(creditWeights(CHECKPOINT, topicOf)).toEqual(
      new Map([
        ['csa.a', 1],
        ['csa.b', 1],
      ]),
    )
  })

  it('skips topics it can’t find', () => {
    const lost = topic('csa.lost', ['csa.nowhere', 'csa.a'])
    expect(creditWeights(lost, topicOf)).toEqual(new Map([['csa.a', 1]]))
  })
})

function event(
  topicId: string,
  overrides: Partial<GradedEvent> = {},
): GradedEvent {
  return {
    type: 'review',
    topic_id: topicId,
    item_id: 'review',
    correct: true,
    rating: 'good',
    occurred_at: day(10),
    ...overrides,
  }
}

describe('creditsFrom', () => {
  it('passes half a Good review to a direct prerequisite, a quarter two steps down, an eighth three', () => {
    const credits = creditsFrom([event('csa.e')], topicOf)
    expect(credits.get('csa.d')).toEqual([credit(10, 0.5, 'csa.e')])
    expect(credits.get('csa.c')).toEqual([credit(10, 0.25, 'csa.e')])
    expect(credits.get('csa.b')).toEqual([credit(10, 0.125, 'csa.e')])
    expect(credits.has('csa.a')).toBe(false)
  })

  it('passes half as much for a Hard review, and stops sooner', () => {
    const credits = creditsFrom(
      [event('csa.e', { rating: 'hard', correct: false })],
      topicOf,
    )
    expect(credits.get('csa.d')).toEqual([credit(10, 0.25, 'csa.e')])
    expect(credits.get('csa.c')).toEqual([credit(10, 0.125, 'csa.e')])
    expect(credits.has('csa.b')).toBe(false)
  })

  it('passes nothing for a review rated Again: it neither helps nor hurts', () => {
    const credits = creditsFrom(
      [event('csa.e', { rating: 'again', correct: false })],
      topicOf,
    )
    expect(credits.size).toBe(0)
  })

  it('passes half a Good review for a passed build or debug, and nothing for a failed one', () => {
    const credits = creditsFrom(
      [
        event('csa.b', { type: 'code_check', item_id: 'build-hello' }),
        event('csa.b', {
          type: 'code_check',
          item_id: 'debug-hello',
          occurred_at: day(11),
        }),
        event('csa.b', {
          type: 'code_check',
          item_id: 'build-hello',
          correct: false,
          occurred_at: day(12),
        }),
      ],
      topicOf,
    )
    expect(credits.get('csa.a')).toEqual([
      credit(10, 0.5, 'csa.b'),
      credit(11, 0.5, 'csa.b'),
    ])
  })

  it('counts a fresh version of a checkpoint build, crediting the topics it builds on', () => {
    const credits = creditsFrom(
      [event(CHECKPOINT.id, { type: 'code_check', item_id: 'build-split' })],
      topicOf,
    )
    expect(credits.get('csa.a')).toEqual([credit(10, 0.5, CHECKPOINT.id)])
    expect(credits.get('csa.b')).toEqual([credit(10, 0.5, CHECKPOINT.id)])
  })

  it('ignores practice, explanations, the placement test and unknown topics', () => {
    const credits = creditsFrom(
      [
        event('csa.b', { type: 'answer', item_id: 'mcq-print' }),
        event('csa.b', { type: 'code_check', item_id: 'write-hello' }),
        event('csa.b', { type: 'explain_submit', item_id: null }),
        event('csa.b', {
          type: 'code_check',
          item_id: 'build-hello',
          context: 'placement',
        }),
        event('csa.unknown'),
      ],
      topicOf,
    )
    expect(credits.size).toBe(0)
  })
})

describe('implicitState', () => {
  it('moves stability part of the way toward what a Good review would give, and leaves difficulty alone', () => {
    const start = initialState('good')
    const half = implicitState(start, 3, 0.5)
    const quarter = implicitState(start, 3, 0.25)
    expect(half.difficulty).toBe(start.difficulty)
    expect(quarter.stability).toBeGreaterThan(start.stability)
    expect(half.stability).toBeGreaterThan(quarter.stability)
    expect(implicitState(start, 3, 0).stability).toBe(start.stability)
  })
})

describe('replayWithCredits', () => {
  it('is replayCard exactly when there are no credits', () => {
    const histories: Review[][] = [
      [],
      [review(4), review(19), review(68)],
      [review(4, 'again'), review(5), review(9, 'hard')],
      [review(3, 'hard'), review(40, 'again'), review(41), review(60)],
    ]
    for (const reviews of histories) {
      expect(replayWithCredits(day(0), reviews).card).toEqual(
        replayCard(day(0), reviews),
      )
    }
  })

  // Worked examples. Learned on day 0, a topic's first review is due on
  // day 4 (FSRS-4.5's first Good: stability 3.71 days).
  it('pushes the first review from day 4 to day 8 for half a review on day 2', () => {
    const { card, counted } = replayWithCredits(day(0), [], [credit(2)])
    // A real Good on day 2 would have put it on day 12: half way is day 8.
    expect(card.stability).toBeCloseTo(7.645, 3)
    expect(dayNumber(card.due)).toBe(8)
    expect(counted).toHaveLength(1)
    // It isn't a review: the card still has none.
    expect(card.reviews).toBe(0)
    expect(card.lastReview).toBe(day(0))
  })

  it('gives less for a smaller share: day 9, 7 and 5 for a half, a quarter and an eighth on day 3', () => {
    const due = (share: number) =>
      dayNumber(replayWithCredits(day(0), [], [credit(3, share)]).card.due)
    expect(due(0.5)).toBe(9)
    expect(due(0.25)).toBe(7)
    expect(due(0.125)).toBe(5)
  })

  it('takes no credit before the card is half way to due', () => {
    // Day 1 is less than half of 3.71 days.
    const { card, counted } = replayWithCredits(day(0), [], [credit(1)])
    expect(dayNumber(card.due)).toBe(4)
    expect(counted).toEqual([])
    // After a Good on day 4 the next is due on day 19; day 10 is short of half.
    expect(
      replayWithCredits(day(0), [review(4)], [credit(10)]).counted,
    ).toEqual([])
    expect(
      replayWithCredits(day(0), [review(4)], [credit(13)]).counted,
    ).toHaveLength(1)
  })

  it('takes at most one credit a day, the biggest, whatever order they come in', () => {
    const same = [credit(3, 0.25, 'csa.x'), credit(3, 0.5, 'csa.y')]
    const one = replayWithCredits(day(0), [], same)
    const other = replayWithCredits(day(0), [], same.toReversed())
    expect(one).toEqual(other)
    expect(one.counted).toEqual([credit(3, 0.5, 'csa.y')])
  })

  it('takes at most two credits between real reviews, so a real one always comes', () => {
    const credits = [credit(2), credit(6), credit(12)]
    const { card, counted } = replayWithCredits(day(0), [], credits)
    // Two credits: day 4 → day 8 → day 18. The third waits for a review.
    expect(counted).toEqual([credit(2), credit(6)])
    expect(dayNumber(card.due)).toBe(18)
    // After a real review, credits count again.
    const after = replayWithCredits(
      day(0),
      [review(18)],
      [...credits, credit(50)],
    )
    expect(after.counted).toEqual([credit(2), credit(6), credit(50)])
  })

  it('gives nothing to a topic that is relearning, until a real review passes', () => {
    const lapsed = replayWithCredits(day(0), [review(4, 'again')], [credit(6)])
    expect(lapsed.counted).toEqual([])
    expect(lapsed.card).toEqual(replayCard(day(0), [review(4, 'again')]))
    const passed = replayWithCredits(
      day(0),
      [review(4, 'again'), review(5)],
      [credit(8)],
    )
    expect(passed.counted).toEqual([credit(8)])
  })

  it('helps an overdue topic: due on day 4, used on day 30, next due on day 44', () => {
    const { card } = replayWithCredits(day(0), [], [credit(30)])
    expect(dayNumber(card.due)).toBe(44)
  })

  it('ignores credits from before the topic was Learned', () => {
    const { card, counted } = replayWithCredits(day(5), [], [credit(2)])
    expect(counted).toEqual([])
    expect(card).toEqual(replayCard(day(5), []))
  })

  it('never makes a review come sooner, in 2,000 random histories', () => {
    let seed = 7
    const random = () => {
      seed = (seed * 1_103_515_245 + 12_345) % 2_147_483_648
      return seed / 2_147_483_648
    }
    const ratings: Rating[] = ['again', 'hard', 'good', 'good']
    for (let run = 0; run < 2000; run++) {
      const reviews: Review[] = []
      let at = 0
      for (let count = 1 + Math.floor(random() * 6); count > 0; count--) {
        at += 1 + Math.floor(random() * 40)
        reviews.push(review(at, ratings[Math.floor(random() * 4)]))
      }
      const credits = Array.from({ length: Math.floor(random() * 6) }, () =>
        credit(
          Math.floor(random() * (at + 30)),
          [0.5, 0.25, 0.125][Math.floor(random() * 3)],
        ),
      )
      const without = replayCard(day(0), reviews)
      const { card } = replayWithCredits(day(0), reviews, credits)
      expect(card.due >= without.due).toBe(true)
      expect(card.reviews).toBe(without.reviews)
      expect(card.lapses).toBe(without.lapses)
    }
  })
})

/** The three proof checks of a topic, passed on `n`. */
function learnedOn(each: Topic, n: number): GradedEvent[] {
  return [
    event(each.id, { type: 'code_check', item_id: 'build-hello' }),
    event(each.id, { type: 'code_check', item_id: 'debug-hello' }),
    event(each.id, { type: 'explain_submit', item_id: null }),
  ].map((one) => ({ ...one, occurred_at: day(n), rating: undefined }))
}

describe('implicit credit in progressOf', () => {
  it('pushes a prerequisite’s review when the topic built on it is proved', () => {
    // A learned on day 0; B's build and debug pass on day 3.
    const events = [...learnedOn(A, 0), ...learnedOn(B, 3)]
    const progress = progressOf(ALL, events)
    const a = progress.get('csa.a')
    // The build pass on day 3 counts; the debug the same day doesn't add.
    expect(a?.credits).toEqual([credit(3, 0.5, 'csa.b')])
    expect(dayNumber(a?.card?.due ?? '')).toBe(9)
    expect(a?.reviews).toEqual([])
    // On day 5 A would have been fading; now it isn't.
    expect(stateOf(A, progress, day(5))).toBe('learned')
    expect(stateOf(A, progressOf(ALL, learnedOn(A, 0)), day(5))).toBe('fading')
  })

  it('finds what a topic builds on through topicOf, for topics it was not asked about', () => {
    const events = [...learnedOn(A, 0), ...learnedOn(B, 3)]
    const onlyA = progressOf([A], events, [], topicOf).get('csa.a')
    expect(onlyA?.credits).toHaveLength(1)
    // Without topicOf, B isn't known, so its proofs give nothing.
    expect(progressOf([A], events).get('csa.a')?.credits).toEqual([])
  })

  it('never makes a topic Mastered: only a real review rated Good a week on does', () => {
    const events = [
      ...learnedOn(A, 0),
      ...learnedOn(B, 3),
      event('csa.b', { occurred_at: day(10) }),
      event('csa.b', { occurred_at: day(20) }),
    ]
    const progress = progressOf(ALL, events)
    expect(progress.get('csa.a')?.credits).toHaveLength(2)
    // Credit postpones A's review, but no credit is a review.
    expect(stateOf(A, progress, day(25))).not.toBe('mastered')
    // A real Good review of A on day 30 makes it Mastered.
    const reviewed = progressOf(ALL, [
      ...events,
      event('csa.a', { occurred_at: day(30) }),
    ])
    expect(stateOf(A, reviewed, day(31))).toBe('mastered')
  })

  it("doesn't depend on the order of the events", () => {
    const events = [
      ...learnedOn(A, 0),
      ...learnedOn(B, 3),
      ...learnedOn(C, 5),
      event('csa.c', { occurred_at: day(9), rating: 'hard' }),
      event('csa.b', { occurred_at: day(12) }),
      event('csa.a', { occurred_at: day(20) }),
    ]
    const forwards = progressOf(ALL, events)
    const backwards = progressOf(ALL, events.toReversed())
    for (const id of ['csa.a', 'csa.b', 'csa.c']) {
      expect(backwards.get(id)).toEqual(forwards.get(id))
    }
  })
})
