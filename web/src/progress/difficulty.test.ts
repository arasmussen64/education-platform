import { describe, expect, it } from 'vitest'
import type { Attempt } from '../followups/followUps.ts'
import {
  bandOf,
  describeRate,
  firstTries,
  recentDifficulty,
  topicDifficulty,
  topicsOffTarget,
} from './difficulty.ts'

let clock = 0
/** An answer a minute after the one before it. */
function answer(
  item: string,
  correct: boolean,
  over: Partial<Attempt> = {},
): Attempt {
  clock += 1
  return {
    id: `a-${clock}`,
    type: 'answer',
    topic_id: 'py.print',
    item_id: item,
    correct,
    occurred_at: new Date(Date.UTC(2026, 10, 1, 12, clock)).toISOString(),
    context: 'practice',
    ...over,
  }
}

/** First tries at `count` different questions, `right` of them right. */
function tries(count: number, right: number, topicId = 'py.print'): Attempt[] {
  return Array.from({ length: count }, (_, index) =>
    answer(`${topicId}-q${index}`, index < right, { topic_id: topicId }),
  )
}

describe('first tries', () => {
  it('counts only the first answer to each question', () => {
    const attempts = [
      answer('q1', false),
      answer('q1', true),
      answer('q2', true),
    ]
    expect(firstTries(attempts).map((each) => each.correct)).toEqual([
      false,
      true,
    ])
  })

  it('finds the first by time, whatever order the history is in', () => {
    const wrong = answer('q1', false)
    const right = answer('q1', true)
    expect(firstTries([right, wrong])[0].correct).toBe(false)
  })

  it('leaves out Checks, reviews, proofs, placement and the quick check', () => {
    const attempts = [
      answer('q1', true, { type: 'code_check' }),
      answer('q2', true, { context: 'review' }),
      answer('q3', true, { context: 'prove' }),
      answer('q4', true, { context: 'placement' }),
      answer('q5', true, { quick_check: true }),
      answer('q6', true, { context: 'learn' }),
      // Saved before answers carried a context: it was practice.
      answer('q7', false, { context: undefined }),
    ]
    expect(firstTries(attempts).map((each) => each.itemId)).toEqual([
      'q6',
      'q7',
    ])
  })
})

describe('how hard practice has been', () => {
  it('puts a share of right answers in a band around 85%', () => {
    expect(bandOf(0.85)).toBe('about-right')
    expect(bandOf(0.7)).toBe('about-right')
    expect(bandOf(0.69)).toBe('hard')
    expect(bandOf(0.94)).toBe('about-right')
    expect(bandOf(0.95)).toBe('easy')
  })

  it('says nothing until there are 20 first tries', () => {
    expect(recentDifficulty(tries(19, 19))).toBeNull()
    expect(recentDifficulty(tries(20, 17))).toMatchObject({
      tries: 20,
      right: 17,
      band: 'about-right',
    })
  })

  it('looks at the most recent 40 only', () => {
    // 30 old misses, then 40 right answers: lately, it has been easy.
    const attempts = [...tries(30, 0, 'old.topic'), ...tries(40, 40)]
    expect(recentDifficulty(attempts)).toMatchObject({
      tries: 40,
      right: 40,
      band: 'easy',
    })
  })

  it("gives one topic's figure once it has 8 first tries", () => {
    expect(topicDifficulty(tries(7, 0), 'py.print')).toBeNull()
    expect(topicDifficulty(tries(8, 5), 'py.print')).toMatchObject({
      right: 5,
      band: 'hard',
    })
    expect(topicDifficulty(tries(8, 8), 'py.other')).toBeNull()
  })

  it('lists the topics off the target, the furthest first', () => {
    const attempts = [
      ...tries(10, 10, 'easy.topic'),
      ...tries(10, 3, 'hard.topic'),
      ...tries(10, 8, 'fine.topic'),
      ...tries(4, 0, 'few.topic'),
    ]
    expect(topicsOffTarget(attempts).map((each) => each.topicId)).toEqual([
      'hard.topic',
      'easy.topic',
    ])
  })

  it('writes a figure out', () => {
    const difficulty = recentDifficulty(tries(40, 36))
    expect(difficulty && describeRate(difficulty)).toBe(
      '36 of 40 right first time (90%)',
    )
  })
})
