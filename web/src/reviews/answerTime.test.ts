import { describe, expect, it } from 'vitest'
import type { Attempt, ItemsOf } from '../followups/followUps.ts'
import {
  kindOf,
  LONGEST_COUNTED_MS,
  MIN_TIMED_ANSWERS,
  RECENT_ANSWERS,
  rateSession,
  type SessionAnswer,
  slowAfter,
  SLOW_FLOOR_MS,
  usualTimes,
} from './answerTime.ts'

const SECOND = 1000
const MINUTE = 60 * SECOND

// One topic with a question of each kind the tests need.
const itemsOf: ItemsOf = (topicId) =>
  topicId === 'csa.a'
    ? {
        'mcq-1': { skills: ['s'], type: 'mcq' },
        'parsons-1': { skills: ['s'], type: 'parsons' },
        'write-1': { skills: ['s'], stage: 'write' },
        'example-1': { skills: ['s'], stage: 'worked_example' },
        'lab-1': { skills: ['s'], stage: 'write', runtime: 'lab' },
      }
    : undefined

let counter = 0
/** A right answer to `item`, `ms` long, on minute `n` of 2026-11-01. */
function answer(
  item: string,
  ms: number | null,
  overrides: Partial<Attempt> = {},
): Attempt {
  counter += 1
  return {
    id: `a${counter}`,
    type:
      item.startsWith('write') || item.startsWith('lab')
        ? 'code_check'
        : 'answer',
    topic_id: 'csa.a',
    item_id: item,
    correct: true,
    occurred_at: new Date(
      Date.UTC(2026, 10, 1) + counter * MINUTE,
    ).toISOString(),
    duration_ms: ms,
    context: 'practice',
    ...overrides,
  }
}

/** `count` right answers to `item`, each `ms` long. */
const many = (item: string, ms: number, count = MIN_TIMED_ANSWERS) =>
  Array.from({ length: count }, () => answer(item, ms))

describe('kindOf', () => {
  it("is a question's type, or a Python exercise's stage", () => {
    expect(kindOf({ skills: [], type: 'predict_shell' })).toBe('predict_shell')
    expect(kindOf({ skills: [], stage: 'fill_in' })).toBe('code:fill_in')
  })

  it('leaves labs, worked examples and unknown items untimed', () => {
    expect(
      kindOf({ skills: [], stage: 'debug', runtime: 'lab' }),
    ).toBeUndefined()
    expect(kindOf({ skills: [], stage: 'worked_example' })).toBeUndefined()
    expect(kindOf(undefined)).toBeUndefined()
  })
})

describe('usualTimes', () => {
  it('is the median of right answers, by kind', () => {
    const usual = usualTimes(
      [
        ...many('mcq-1', 10 * SECOND, 5),
        ...many('mcq-1', 20 * SECOND, 6),
        ...many('parsons-1', 50 * SECOND),
      ],
      itemsOf,
    )
    expect(usual.get('mcq')).toBe(20 * SECOND)
    expect(usual.get('parsons')).toBe(50 * SECOND)
  })

  it('needs enough timed right answers before it judges a kind', () => {
    const usual = usualTimes(
      [
        ...many('mcq-1', 10 * SECOND, MIN_TIMED_ANSWERS - 1),
        answer('mcq-1', null),
        answer('mcq-1', 10 * SECOND, { correct: false }),
        answer('mcq-1', 10 * SECOND, { context: 'placement' }),
      ],
      itemsOf,
    )
    expect(usual.has('mcq')).toBe(false)
  })

  it('looks at the most recent answers, so it follows a learner who speeds up', () => {
    const usual = usualTimes(
      [
        ...many('mcq-1', 60 * SECOND, 30),
        ...many('mcq-1', 15 * SECOND, RECENT_ANSWERS),
      ],
      itemsOf,
    )
    expect(usual.get('mcq')).toBe(15 * SECOND)
  })

  it('counts a very long time as thirty minutes', () => {
    const usual = usualTimes(many('write-1', 5 * 60 * MINUTE), itemsOf)
    expect(usual.get('code:write')).toBe(LONGEST_COUNTED_MS)
  })

  it("doesn't time labs, worked examples, or items it can't find", () => {
    const usual = usualTimes(
      [
        ...many('lab-1', 10 * MINUTE),
        ...many('example-1', MINUTE),
        ...many('constructor', MINUTE),
        ...many('mcq-1', MINUTE).map((each) => ({
          ...each,
          topic_id: 'csa.b',
        })),
      ],
      itemsOf,
    )
    expect(usual.size).toBe(0)
  })
})

describe('slowAfter', () => {
  it('is three times the usual time, and never under a minute', () => {
    const usual = new Map([
      ['mcq', 15 * SECOND],
      ['code:write', 4 * MINUTE],
    ])
    expect(slowAfter('mcq', usual)).toBe(SLOW_FLOOR_MS)
    expect(slowAfter('code:write', usual)).toBe(12 * MINUTE)
    expect(slowAfter('parsons', usual)).toBeUndefined()
    expect(slowAfter(undefined, usual)).toBeUndefined()
  })
})

describe('rateSession', () => {
  const usual = new Map([
    ['mcq', 15 * SECOND],
    ['predict_output', 40 * SECOND],
  ])
  const item = (
    itemId: string,
    correct: boolean,
    durationMs: number | null,
    kind?: string,
  ): SessionAnswer => ({ itemId, correct, durationMs, kind })

  it('is Good when every answer is right in a usual time', () => {
    expect(
      rateSession(
        [
          item('a', true, 30 * SECOND, 'mcq'),
          item('b', true, MINUTE, 'predict_output'),
        ],
        usual,
      ),
    ).toEqual({ rating: 'good', slow: [], slowed: false })
  })

  it('is Hard when every answer is right but one took far longer than usual', () => {
    expect(
      rateSession(
        [
          item('a', true, 30 * SECOND, 'mcq'),
          item('b', true, 2.5 * MINUTE, 'predict_output'),
        ],
        usual,
      ),
    ).toEqual({ rating: 'hard', slow: ['b'], slowed: true })
  })

  it('needs both: three times the usual and over a minute', () => {
    // 50 s is more than three times 15 s, but under the minute.
    expect(
      rateSession([item('a', true, 50 * SECOND, 'mcq')], usual).rating,
    ).toBe('good')
    // 61 s is over both.
    expect(
      rateSession([item('a', true, 61 * SECOND, 'mcq')], usual).rating,
    ).toBe('hard')
  })

  it('stays Good when the time is missing, or the kind has too little history', () => {
    expect(
      rateSession(
        [item('a', true, null, 'mcq'), item('b', true, 9 * MINUTE, 'parsons')],
        usual,
      ),
    ).toEqual({ rating: 'good', slow: [], slowed: false })
    expect(rateSession([item('a', true, 9 * MINUTE)], usual).rating).toBe(
      'good',
    )
  })

  it('leaves Hard and Again as they were: time only ever turns Good into Hard', () => {
    expect(
      rateSession(
        [
          item('a', false, 5 * SECOND, 'mcq'),
          item('b', true, 9 * MINUTE, 'mcq'),
        ],
        usual,
      ),
    ).toEqual({ rating: 'hard', slow: ['b'], slowed: false })
    expect(rateSession([item('a', false, 9 * MINUTE, 'mcq')], usual)).toEqual({
      rating: 'again',
      slow: [],
      slowed: false,
    })
  })
})
