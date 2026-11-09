import { describe, expect, it } from 'vitest'
import { labEventData, parseLabResult } from './result.ts'

const LAB = 'csa.linux.shell/build-log-report'
const printed = JSON.stringify({
  lab: LAB,
  rev: 1,
  checker: '1',
  checked_at: '2026-11-09T18:00:00+00:00',
  passed: 1,
  total: 2,
  checks: [
    { id: 'report-folder', passed: true },
    { id: 'failed-count', passed: false },
  ],
})

describe('parseLabResult', () => {
  it('reads what the checker printed, counting the checks itself', () => {
    const tampered = printed.replace(
      '"passed":1,"total":2',
      '"passed":2,"total":2',
    )
    const parsed = parseLabResult(`  ${tampered}\n`, LAB, 1)
    if (!('result' in parsed)) throw new Error(parsed.error)
    expect(parsed.result.passed).toBe(1)
    expect(parsed.result.total).toBe(2)
    expect(parsed.result.checks).toEqual([
      { id: 'report-folder', passed: true },
      { id: 'failed-count', passed: false },
    ])
    expect(parsed.result.checker).toBe('1')
  })

  it('refuses text that is not a result', () => {
    for (const text of [
      '',
      'hello',
      '{"lab": 1}',
      '{"lab":"x","rev":1}',
      '[]',
    ]) {
      const parsed = parseLabResult(text, LAB, 1)
      expect('error' in parsed && parsed.error).toMatch(
        /isn't the checker's result/,
      )
    }
    const empty = printed.replace(/"checks":\[.*\]/, '"checks":[]')
    expect(parseLabResult(empty, LAB, 1)).toMatchObject({
      error: expect.stringMatching(/isn't the checker's result/),
    })
  })

  it('refuses a result for another lab or another revision', () => {
    expect(parseLabResult(printed, 'csa.linux.shell/other', 1)).toEqual({
      error: `That result is for another lab (${LAB}).`,
    })
    expect(parseLabResult(printed, LAB, 2)).toMatchObject({
      error: expect.stringMatching(/revision 1 of this lab.*revision 2/),
    })
  })
})

describe('labEventData', () => {
  it('saves the counts and the failing ids, marked as a lab', () => {
    const parsed = parseLabResult(printed, LAB, 1)
    if (!('result' in parsed)) throw new Error(parsed.error)
    expect(labEventData(parsed.result)).toEqual({
      runtime: 'lab',
      checker: '1',
      checked_at: '2026-11-09T18:00:00+00:00',
      passed: 1,
      total: 2,
      failing: ['failed-count'],
    })
  })
})
