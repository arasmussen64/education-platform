import { describe, expect, it } from 'vitest'
import { ESTIMATE } from '../test/fakeContent.tsx'
import {
  acceptedRange,
  formatNear,
  formatNumber,
  isPercentUnit,
  matchingMistake,
  NOT_A_NUMBER,
  readNumber,
  relativeError,
  withinTolerance,
  withUnit,
} from './estimates.ts'
import type { EstimateItem } from './types.ts'

const read = (typed: string, unit = 'core licences') => readNumber(typed, unit)

describe('readNumber', () => {
  it.each([
    ['1168', 1168],
    ['  27.5 ', 27.5],
    ['1,168', 1168],
    ['1,168,000.25', 1168000.25],
    ['.5', 0.5],
    ['$1,168', 1168],
    ['€ 12', 12],
    ['-3', -3],
    ['−3', -3],
    ['-$5', -5],
    ['+5', 5],
  ])('reads %j as %d', (typed, number) => {
    expect(read(typed)).toEqual({ ok: true, number })
  })

  it.each([
    'about 1200',
    '1.2k',
    '1e3',
    '1 168',
    // In much of Europe these mean 11.68 and 1168.5: too risky to guess.
    '11,68',
    '1.168,50',
    '27,5',
    '$-5',
    '28 licences',
    '1'.padEnd(400, '0'),
  ])('refuses %j, saying how to type a number', (typed) => {
    expect(read(typed)).toEqual({ ok: false, message: NOT_A_NUMBER })
  })

  it('asks for a number when the box is empty', () => {
    expect(read('   ')).toEqual({ ok: false, message: 'Type a number first.' })
  })

  it('takes a % after a percentage, and nowhere else', () => {
    expect(read('15%', '%')).toEqual({ ok: true, number: 15 })
    expect(read('15 %', 'percent saved')).toEqual({ ok: true, number: 15 })
    expect(read('15%', 'dollars a month')).toEqual({
      ok: false,
      message: 'Leave out the %: the answer is in dollars a month.',
    })
  })
})

describe('isPercentUnit', () => {
  it('knows a percentage from its unit', () => {
    expect(isPercentUnit('%')).toBe(true)
    expect(isPercentUnit('% of the vCPUs')).toBe(true)
    expect(isPercentUnit('Percent')).toBe(true)
    expect(isPercentUnit('percentage points')).toBe(true)
    expect(isPercentUnit('dollars')).toBe(false)
    expect(isPercentUnit('percentile')).toBe(false)
  })
})

const exact: EstimateItem = {
  ...ESTIMATE,
  answer: 28,
  tolerance: { absolute: 0 },
}
const withinATenth: EstimateItem = {
  ...ESTIMATE,
  answer: 27.5,
  tolerance: { absolute: 0.1 },
}

describe('withinTolerance', () => {
  it('takes a percentage of the answer, edges included', () => {
    // 10% of 87.6 is 8.76.
    expect(withinTolerance(78.84, ESTIMATE)).toBe(true)
    expect(withinTolerance(96.36, ESTIMATE)).toBe(true)
    expect(withinTolerance(78.83, ESTIMATE)).toBe(false)
    expect(withinTolerance(73, ESTIMATE)).toBe(false)
  })

  it('takes an absolute amount either side, and 0 means exactly', () => {
    expect(withinTolerance(28, exact)).toBe(true)
    expect(withinTolerance(28.0001, exact)).toBe(false)
    // 27.4 - 27.5 is -0.10000000000000142 in binary, a hair past 0.1.
    expect(withinTolerance(27.4, withinATenth)).toBe(true)
    expect(withinTolerance(27.6, withinATenth)).toBe(true)
    expect(withinTolerance(27.39, withinATenth)).toBe(false)
  })

  it('stays exact for a big exact answer', () => {
    const bytes: EstimateItem = {
      ...exact,
      answer: 17_179_869_184,
      unit: 'bytes',
    }
    expect(withinTolerance(17_179_869_184, bytes)).toBe(true)
    expect(withinTolerance(17_179_869_183, bytes)).toBe(false)
    expect(withinTolerance(17_179_869_170, bytes)).toBe(false)
  })
})

describe('acceptedRange and relativeError', () => {
  it('give the edges, and how far off as a share of the answer', () => {
    const [low, high] = acceptedRange(ESTIMATE)
    expect(low).toBeCloseTo(78.84)
    expect(high).toBeCloseTo(96.36)
    expect(relativeError(73, 87.6)).toBeCloseTo(-0.1667, 4)
    expect(relativeError(-2, -1)).toBe(-1)
    expect(relativeError(5, 0)).toBeNull()
  })
})

describe('matchingMistake', () => {
  it('matches a number within half a percent of a mistake, the nearest first', () => {
    expect(matchingMistake(73, ESTIMATE.mistakes)?.id).toBe('vm-only')
    expect(matchingMistake(73.3, ESTIMATE.mistakes)?.id).toBe('vm-only')
    expect(matchingMistake(74, ESTIMATE.mistakes)).toBeNull()
    expect(matchingMistake(2.88, ESTIMATE.mistakes)?.id).toBe('one-day')
    const close = [
      { id: 'a', value: 100, working: '', why: '' },
      { id: 'b', value: 100.6, working: '', why: '' },
    ]
    expect(matchingMistake(100.4, close)?.id).toBe('b')
  })
})

describe('showing numbers', () => {
  it('writes thousands with commas, and hides binary noise', () => {
    expect(formatNumber(1916)).toBe('1,916')
    expect(formatNumber(0.1 + 0.2)).toBe('0.3')
    expect(formatNear(87.6 * 0.9, 87.6)).toBe('78.84')
    expect(withUnit('28', 'core licences')).toBe('28 core licences')
    expect(withUnit('20', '%')).toBe('20%')
  })
})
