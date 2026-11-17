import { describe, expect, it } from 'vitest'
import type { TopicContent } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import { fakeContent, fakeLab, fakeTopic } from '../test/fakeContent.tsx'
import { replayCard } from './fsrs.ts'
import {
  earlierAnswers,
  labForReview,
  planReview,
  REVIEW_LAB_MIN_DAYS,
  reviewLabsOf,
} from './reviews.ts'

const day = (n: number) => new Date(Date.UTC(2026, 10, 1 + n, 12)).toISOString()

/** A topic whose review pool is a quick check and a prediction, with two review labs. */
function withLabs(
  reviewLabs: string[] = ['debug-lab', 'write-lab'],
): TopicContent {
  const base = fakeContent(
    fakeTopic({
      prerequisites: [],
      review_pool: ['mcq-print', 'predict-print'],
      review_labs: reviewLabs,
    }),
  )
  return {
    ...base,
    exercises: {
      ...base.exercises,
      'debug-lab': fakeLab({ id: 'debug-lab', stage: 'debug' }),
      'write-lab': fakeLab({ id: 'write-lab', stage: 'write' }),
      'example-lab': fakeLab({ id: 'example-lab', stage: 'worked_example' }),
    },
  }
}

const content = withLabs()
const topicId = content.topic.id

/** Learned on day 0, its first review Good on day 4: the next is due 15 days on. */
const longGap = replayCard(day(0), [{ at: day(4), rating: 'good' }])
/** Learned on day 0, no review yet: the first is due 4 days on. */
const shortGap = replayCard(day(0), [])

let counter = 0
function attempt(overrides: Partial<Attempt>): Attempt {
  counter += 1
  return {
    id: `a${counter}`,
    type: 'answer',
    topic_id: topicId,
    item_id: 'mcq-print',
    correct: true,
    occurred_at: day(1),
    ...overrides,
  }
}
const labCheck = (
  item: string,
  at: string,
  context: Attempt['context'] = 'review',
) => attempt({ type: 'code_check', item_id: item, occurred_at: at, context })
const review = (at: string) =>
  attempt({
    type: 'review',
    item_id: 'review',
    occurred_at: at,
    rating: 'good',
  })

describe('reviewLabsOf', () => {
  it('keeps the labs that exist and are not worked examples', () => {
    expect(
      reviewLabsOf(
        withLabs(['debug-lab', 'example-lab', 'gone', 'write-hello']),
      ),
    ).toEqual(['debug-lab'])
  })
})

describe('labForReview', () => {
  it(`asks a lab once the gap is at least ${REVIEW_LAB_MIN_DAYS} days`, () => {
    expect(labForReview(content, longGap, [])).toBe('debug-lab')
    expect(labForReview(content, shortGap, [])).toBeNull()
  })

  it('asks none for a topic without review labs, or without a card', () => {
    expect(labForReview(withLabs([]), longGap, [])).toBeNull()
    expect(labForReview(content, null, [])).toBeNull()
  })

  it('asks the lab done longest ago', () => {
    const history = [labCheck('debug-lab', day(2), 'practice')]
    expect(labForReview(content, longGap, history)).toBe('write-lab')
  })

  it('asks at most one lab in three reviews', () => {
    // A lab in the review on day 4, saved just before that review.
    const history = [
      labCheck('debug-lab', '2026-11-05T11:00:00.000Z'),
      review(day(4)),
    ]
    expect(labForReview(content, longGap, history)).toBeNull()
    expect(
      labForReview(content, longGap, [...history, review(day(20))]),
    ).toBeNull()
    expect(
      labForReview(content, longGap, [
        ...history,
        review(day(20)),
        review(day(60)),
      ]),
    ).toBe('write-lab')
  })

  it('comes back at the next review when it was put off, since a put-off lab leaves no result', () => {
    const history = [review(day(4)), review(day(20)), review(day(60))]
    expect(labForReview(content, longGap, history)).toBe('debug-lab')
  })
})

describe('planReview with a lab', () => {
  it('asks the lab in place of a quick question, and knows what replaces it', () => {
    const plan = planReview(content, longGap, [])
    expect(plan.lab).toBe('debug-lab')
    expect(plan.items).toHaveLength(2)
    expect(plan.items).toContain('debug-lab')
    // Put off, the lab's place goes to a question from the pool, and the
    // other item stays.
    const other = plan.items.find((id) => id !== 'debug-lab')
    expect(plan.withoutLab).toHaveLength(2)
    expect(plan.withoutLab).toContain(other)
    expect(plan.withoutLab).not.toContain('debug-lab')
    expect(
      plan.withoutLab.every((id) => content.topic.review_pool.includes(id)),
    ).toBe(true)
  })

  it('asks no lab on a short gap', () => {
    const plan = planReview(content, shortGap, [])
    expect(plan.lab).toBeNull()
    expect(plan.items).toEqual(plan.withoutLab)
    expect(plan.items).not.toContain('debug-lab')
  })

  it('keeps a lab answered on an earlier visit, which can no longer be put off', () => {
    const history = [labCheck('debug-lab', longGap.due)]
    expect(earlierAnswers(content, longGap, history)).toEqual(
      new Map([['debug-lab', true]]),
    )
    const plan = planReview(content, longGap, history)
    expect(plan.answered.get('debug-lab')).toBe(true)
    expect(plan.items).toContain('debug-lab')
    expect(plan.lab).toBeNull()
  })
})
