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
  memoryPercent,
  ratingOf,
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
