import { describe, expect, it } from 'vitest'
import type { Attempt } from '../followups/followUps.ts'
import { progressOf } from '../progress/progress.ts'
import { fakeContent, fakeTopic } from '../test/fakeContent.tsx'
import { replayCard } from './fsrs.ts'
import {
  chooseReviewItems,
  DAILY_REVIEW_LIMIT,
  describeGap,
  dueReviews,
  earlierAnswers,
  memoryPercent,
  planReview,
  ratingOf,
  reviewsLeftToday,
} from './reviews.ts'

const day = (n: number) => new Date(Date.UTC(2026, 10, 1 + n, 12)).toISOString()

/** A topic Learned on `learnedDay`, with no prerequisites. */
function learned(id: string, learnedDay: number) {
  const topic = fakeTopic({ id, prerequisites: [] })
  const events = [
    { type: 'code_check' as const, item_id: 'build-hello', correct: true },
    { type: 'code_check' as const, item_id: 'debug-hello', correct: true },
    { type: 'explain_submit' as const, item_id: 'explain', correct: true },
  ].map((event) => ({ ...event, topic_id: id, occurred_at: day(learnedDay) }))
  return { topic, events }
}

describe('memoryPercent', () => {
  it('is 100 right after a review, near the 90% target when due, and drifts down', () => {
    const card = replayCard(day(0), [])
    expect(memoryPercent(card, day(0))).toBe(100)
    const atDue = memoryPercent(card, card.due)
    expect(atDue).toBeGreaterThan(80)
    expect(atDue).toBeLessThan(100)
    expect(memoryPercent(card, day(365))).toBeLessThan(atDue)
    expect(memoryPercent(card, day(365))).toBeGreaterThanOrEqual(0)
  })
})

describe('dueReviews', () => {
  const a = learned('py.a', 0)
  const b = learned('py.b', 0)
  const fresh = learned('py.fresh', 29)
  const checkpoint = fakeTopic({
    id: 'py.m9.checkpoint',
    kind: 'checkpoint',
    prerequisites: [],
  })
  const topics = [a.topic, b.topic, fresh.topic, checkpoint]
  const checkpointEvents = a.events.map((event) => ({
    ...event,
    topic_id: checkpoint.id,
  }))

  it('lists Learned topics whose review is due, most forgotten first', () => {
    const progress = progressOf(topics, [
      ...a.events,
      ...b.events,
      ...fresh.events,
      ...checkpointEvents,
      // b was reviewed recently, so it's remembered better than a.
      {
        type: 'review',
        topic_id: 'py.b',
        item_id: 'review',
        correct: true,
        occurred_at: day(4),
        rating: 'good',
      },
    ])
    const due = dueReviews(topics, progress, day(30))
    expect(due.map((review) => review.topic.id)).toEqual(['py.a', 'py.b'])
    expect(due[0]!.retrievability).toBeLessThan(due[1]!.retrievability)
  })

  it('leaves out topics not yet due, not yet Learned, and checkpoints', () => {
    const progress = progressOf(topics, [...a.events, ...checkpointEvents])
    const card = progress.get('py.a')!.card!
    const justBefore = new Date(Date.parse(card.due) - 1000).toISOString()
    expect(dueReviews(topics, progress, justBefore)).toEqual([])
    expect(
      dueReviews(topics, progress, card.due).map((r) => r.topic.id),
    ).toEqual(['py.a'])
  })

  it('stops at the daily limit', () => {
    const many = Array.from({ length: DAILY_REVIEW_LIMIT + 5 }, (_, i) =>
      learned(`py.t${i}`, 0),
    )
    const progress = progressOf(
      many.map((each) => each.topic),
      many.flatMap((each) => each.events),
    )
    expect(
      dueReviews(
        many.map((each) => each.topic),
        progress,
        day(30),
      ),
    ).toHaveLength(DAILY_REVIEW_LIMIT)
  })
})

describe('reviewsLeftToday', () => {
  /** A finished review session at a local time on 11 November 2026. */
  const reviewAt = (hour: number, minute = 0, date = 11): Attempt => ({
    id: `review-${date}-${hour}-${minute}`,
    type: 'review',
    topic_id: 'py.a',
    item_id: 'review',
    correct: true,
    occurred_at: new Date(2026, 10, date, hour, minute).toISOString(),
    rating: 'good',
    context: 'review',
  })
  const now = new Date(2026, 10, 11, 18, 0).toISOString()

  it('is the whole limit on a day with no reviews yet', () => {
    expect(reviewsLeftToday([], now)).toBe(DAILY_REVIEW_LIMIT)
  })

  it("counts the day's finished reviews, from midnight, local time", () => {
    const history = [
      reviewAt(23, 30, 10), // yesterday evening: doesn't count
      reviewAt(0, 10),
      reviewAt(9),
      reviewAt(17, 59),
    ]
    expect(reviewsLeftToday(history, now)).toBe(DAILY_REVIEW_LIMIT - 3)
  })

  it("leaves out answers, Checks and explanations: they aren't review sessions", () => {
    const at = reviewAt(9).occurred_at
    const others: Attempt[] = [
      ['answer', 'mcq-print'] as const,
      ['code_check', 'write-hello'] as const,
      ['explain_submit', 'explain'] as const,
    ].map(([type, item]) => ({
      id: `${type}-1`,
      type,
      topic_id: 'py.a',
      item_id: item,
      correct: true,
      occurred_at: at,
      context: 'review',
    }))
    expect(reviewsLeftToday(others, now)).toBe(DAILY_REVIEW_LIMIT)
  })

  it('never goes below none', () => {
    const many = Array.from({ length: DAILY_REVIEW_LIMIT + 3 }, (_, i) =>
      reviewAt(8, i),
    )
    expect(reviewsLeftToday(many, now)).toBe(0)
  })

  it('makes dueReviews offer only what is left of the day', () => {
    const many = Array.from({ length: DAILY_REVIEW_LIMIT + 5 }, (_, i) =>
      learned(`py.t${i}`, 0),
    )
    const topics = many.map((each) => each.topic)
    const progress = progressOf(
      topics,
      many.flatMap((each) => each.events),
    )
    // Learned on 1 November, so all of them are due by the 11th.
    const doneToday = Array.from({ length: 5 }, (_, i) => reviewAt(8, i))
    expect(dueReviews(topics, progress, now)).toHaveLength(DAILY_REVIEW_LIMIT)
    expect(
      dueReviews(topics, progress, now, reviewsLeftToday(doneToday, now)),
    ).toHaveLength(DAILY_REVIEW_LIMIT - 5)
  })
})

describe('chooseReviewItems', () => {
  const content = fakeContent(
    fakeTopic({
      review_pool: ['mcq-print', 'predict-print', 'write-hello', 'fill-hello'],
    }),
  )
  const attempt = (item: string, when: string): Attempt => ({
    id: `${item}-${when}`,
    type: 'answer',
    topic_id: content.topic.id,
    item_id: item,
    correct: true,
    occurred_at: when,
  })

  it('asks two items, at least one of them code or predict-the-output', () => {
    const items = chooseReviewItems(content, [])
    expect(items).toHaveLength(2)
    expect(
      items.some((id) => id === 'predict-print' || content.exercises[id]),
    ).toBe(true)
  })

  it('prefers items answered longest ago, so sessions rotate', () => {
    const first = chooseReviewItems(content, [])
    const afterFirst = first.map((id) => attempt(id, day(1)))
    const second = chooseReviewItems(content, afterFirst)
    expect(second.some((id) => first.includes(id))).toBe(false)
    const afterSecond = [
      ...afterFirst,
      ...second.map((id) => attempt(id, day(5))),
    ]
    const third = chooseReviewItems(content, afterSecond)
    expect(third.sort()).toEqual([...first].sort())
  })

  it('leaves out items that no longer exist, and worked examples', () => {
    const odd = fakeContent(
      fakeTopic({ review_pool: ['gone', 'example-hello', 'mcq-print'] }),
    )
    expect(chooseReviewItems(odd, [])).toEqual(['mcq-print'])
  })
})

describe('picking up a review left half-way', () => {
  // A pool of one quick check and one prediction; the prediction is the
  // code-or-predict item every session must have.
  const content = fakeContent(
    fakeTopic({
      prerequisites: [],
      review_pool: ['mcq-print', 'predict-print'],
    }),
  )
  const card = replayCard(day(0), [])
  const due = card.due
  const later = (minutes: number) =>
    new Date(Date.parse(due) + minutes * 60_000).toISOString()
  let lastId = 0
  const answer = (
    item: string,
    correct: boolean,
    when: string,
    extra: Partial<Attempt> = {},
  ): Attempt => ({
    id: `attempt-${++lastId}`,
    type: 'answer',
    topic_id: content.topic.id,
    item_id: item,
    correct,
    occurred_at: when,
    context: 'review',
    ...extra,
  })

  it('finds the first review answer to each item since the topic fell due', () => {
    const answers = earlierAnswers(content, card, [
      // Out of order on purpose: the earliest answer to an item counts.
      answer('mcq-print', true, later(30)),
      answer('mcq-print', false, later(10)),
      answer('predict-print', true, later(20)),
    ])
    expect([...answers]).toEqual([
      ['mcq-print', false],
      ['predict-print', true],
    ])
  })

  it('leaves out answers from before it was due, from practice, from other topics, and old ones with no context', () => {
    const noContext = answer('mcq-print', false, later(5))
    delete noContext.context
    const answers = earlierAnswers(content, card, [
      answer('mcq-print', false, new Date(Date.parse(due) - 1).toISOString()),
      answer('mcq-print', false, later(1), { context: 'practice' }),
      answer('mcq-print', false, later(2), { topic_id: 'py.other' }),
      answer('gone', false, later(3)),
      answer('review', true, later(4), { type: 'review', rating: 'good' }),
      noContext,
    ])
    expect(answers.size).toBe(0)
  })

  it('keeps an answered item in the next session, with its answer, and asks the other', () => {
    const history = [answer('predict-print', false, later(10))]
    const plan = planReview(content, card, history)
    expect(plan.items).toEqual(['predict-print', 'mcq-print'])
    expect([...plan.answered]).toEqual([['predict-print', false]])
  })

  it('still asks a code or predict item when the earlier answer was the quick check', () => {
    const plan = planReview(content, card, [
      answer('mcq-print', false, later(10)),
    ])
    expect(plan.items).toEqual(['mcq-print', 'predict-print'])
    expect([...plan.answered]).toEqual([['mcq-print', false]])
  })

  it('is complete as it starts when earlier visits answered both, using the first two answers', () => {
    const three = fakeContent(
      fakeTopic({
        prerequisites: [],
        review_pool: ['mcq-print', 'predict-print', 'write-hello'],
      }),
    )
    const plan = planReview(three, card, [
      answer('mcq-print', false, later(10)),
      answer('write-hello', true, later(20), { type: 'code_check' }),
      answer('predict-print', true, later(30)),
    ])
    expect(plan.items).toEqual(['mcq-print', 'write-hello'])
    expect([...plan.answered]).toEqual([
      ['mcq-print', false],
      ['write-hello', true],
    ])
  })

  it('starts fresh when nothing was answered since it fell due, or there is no card', () => {
    const history = [answer('mcq-print', false, later(10))]
    expect(planReview(content, card, []).answered.size).toBe(0)
    expect(planReview(content, null, history)).toEqual({
      items: chooseReviewItems(content, history),
      answered: new Map(),
    })
  })
})

describe('ratingOf', () => {
  it('is Good when everything was right, Hard when some was, Again when nothing was', () => {
    expect(ratingOf([true, true])).toBe('good')
    expect(ratingOf([true, false])).toBe('hard')
    expect(ratingOf([false, false])).toBe('again')
    expect(ratingOf([true])).toBe('good')
    expect(ratingOf([])).toBe('again')
  })
})

describe('describeGap', () => {
  it('says when the next review is, in plain words', () => {
    expect(describeGap(day(0), day(1))).toBe('tomorrow')
    expect(describeGap(day(0), day(4))).toBe('in 4 days')
    expect(describeGap(day(0), day(70))).toBe('in about 2 months')
    const card = replayCard(day(0), [])
    expect(describeGap(day(0), card.due)).toMatch(/^in \d+ days$|^tomorrow$/)
  })
})
