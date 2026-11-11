import { describe, expect, it } from 'vitest'
import { labEventData, parseLabResult } from './result.ts'

const LAB = 'csa.linux.shell/build-log-report'
/** The lab's own checks, as the page has them from checks.yaml. */
const IDS = ['report-folder', 'failed-count']

function printedWith(checks: { id: string; passed: boolean }[], rev = 1) {
  return JSON.stringify({
    lab: LAB,
    rev,
    checker: '1',
    checked_at: '2026-11-09T18:00:00+00:00',
    passed: checks.filter((check) => check.passed).length,
    total: checks.length,
    checks,
  })
}

const printed = printedWith([
  { id: 'report-folder', passed: true },
  { id: 'failed-count', passed: false },
])

describe('parseLabResult', () => {
  it('reads what the checker printed, counting the checks itself', () => {
    const tampered = printed.replace(
      '"passed":1,"total":2',
      '"passed":2,"total":2',
    )
    const parsed = parseLabResult(`  ${tampered}\n`, LAB, 1, IDS)
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
      const parsed = parseLabResult(text, LAB, 1, IDS)
      expect('error' in parsed && parsed.error).toMatch(
        /isn't the checker's result/,
      )
    }
    const empty = printed.replace(/"checks":\[.*\]/, '"checks":[]')
    expect(parseLabResult(empty, LAB, 1, IDS)).toMatchObject({
      error: expect.stringMatching(/isn't the checker's result/),
    })
  })

  it('refuses a result for another lab', () => {
    expect(parseLabResult(printed, 'csa.linux.shell/other', 1, IDS)).toEqual({
      error: `That result is for another lab (${LAB}).`,
    })
  })

  it('says what to do about a result for an older revision', () => {
    const parsed = parseLabResult(printed, LAB, 2, IDS)
    if (!('error' in parsed)) throw new Error('an old result was accepted')
    expect(parsed.error).toMatch(/revision 1 of this lab.*revision 2/)
    // Running start again keeps the old container, so --fresh is the advice.
    expect(parsed.error).toMatch(/start command with --fresh added/)
    expect(parsed.error).toMatch(/run the checks again/)
  })

  it('says the page is behind when the result is for a newer revision', () => {
    const newer = printedWith(
      IDS.map((id) => ({ id, passed: true })),
      3,
    )
    const parsed = parseLabResult(newer, LAB, 2, IDS)
    if (!('error' in parsed)) throw new Error('a newer result was accepted')
    expect(parsed.error).toMatch(/revision 3 of this lab.*revision 2/)
    expect(parsed.error).toMatch(/Reload the page/)
    expect(parsed.error).not.toMatch(/--fresh/)
  })

  it("accepts the lab's own checks in any order", () => {
    const reversed = printedWith([
      { id: 'failed-count', passed: true },
      { id: 'report-folder', passed: true },
    ])
    const parsed = parseLabResult(reversed, LAB, 1, IDS)
    if (!('result' in parsed)) throw new Error(parsed.error)
    expect(parsed.result.passed).toBe(2)
    expect(parsed.result.total).toBe(2)
  })

  it("refuses a result whose checks are not exactly this lab's checks", () => {
    const others = {
      // The audit's forged line: one made-up check that passed.
      'a made-up check': [{ id: 'a', passed: true }],
      'one of the two missing': [{ id: 'report-folder', passed: true }],
      'one extra': [
        { id: 'report-folder', passed: true },
        { id: 'failed-count', passed: true },
        { id: 'extra', passed: true },
      ],
      'one renamed since': [
        { id: 'report-folder', passed: true },
        { id: 'count-of-failures', passed: true },
      ],
      'one twice': [
        { id: 'report-folder', passed: true },
        { id: 'report-folder', passed: true },
      ],
    }
    for (const [why, checks] of Object.entries(others)) {
      const parsed = parseLabResult(printedWith(checks), LAB, 1, IDS)
      if (!('error' in parsed)) throw new Error(`accepted: ${why}`)
      // A stale result is the likely cause, so that is what it says to fix.
      expect(parsed.error).toMatch(/doesn't list the same checks/)
      expect(parsed.error).toMatch(/run the check command again/)
    }
  })
})

describe('labEventData', () => {
  it('saves the counts and the failing ids, marked as a lab', () => {
    const parsed = parseLabResult(printed, LAB, 1, IDS)
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
