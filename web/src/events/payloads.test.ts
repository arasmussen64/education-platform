import { describe, expect, it } from 'vitest'
import { oneFailed, printed, report } from '../test/fakePython.ts'
import {
  checkEventData,
  clip,
  MAX_CODE_CHARS,
  runEventData,
} from './payloads.ts'

describe('clip', () => {
  it('leaves short text alone and marks where long text was cut', () => {
    expect(clip('short', 10)).toBe('short')
    expect(clip('abcdefghij', 10)).toBe('abcdefghij')
    expect(clip('abcdefghij-more', 10)).toBe('abcd…(cut)')
  })

  it('never returns more than the limit, the marker included', () => {
    for (const max of [0, 3, 6, 7, 10, 100]) {
      expect(clip('x'.repeat(500), max).length).toBeLessThanOrEqual(max)
    }
  })

  it('never cuts an emoji in half, which the database would refuse', () => {
    // An emoji is two UTF-16 halves; a lone half isn't valid text in Postgres.
    const clipped = clip(`abc😀${'x'.repeat(20)}`, 10)
    expect(clipped).toBe('abc…(cut)')
  })
})

describe('runEventData', () => {
  it('saves the code and what it printed', () => {
    expect(runEventData('print(1)', printed('1\n'))).toEqual({
      code: 'print(1)',
      outcome: 'done',
      output: '1\n',
      error: null,
      waiting_for_input: false,
    })
  })

  it('saves a timeout without any output', () => {
    expect(runEventData('while True: pass', { kind: 'timeout' })).toEqual({
      code: 'while True: pass',
      outcome: 'timeout',
    })
  })

  it('cuts very long code to the limit, marker included', () => {
    const data = runEventData('x'.repeat(30_000), { kind: 'timeout' })
    expect(String(data.code)).toHaveLength(MAX_CODE_CHARS)
    expect(String(data.code)).toMatch(/…\(cut\)$/)
  })
})

describe('checkEventData', () => {
  it('saves how many tests passed and which ones failed', () => {
    expect(checkEventData('code', oneFailed('Says hi'))).toEqual({
      code: 'code',
      outcome: 'done',
      status: 'ok',
      passed: 0,
      total: 1,
      failing: ['test_0'],
    })
  })

  it("saves the harness's message when the tests couldn't run", () => {
    const outcome = report({ status: 'error', message: 'SyntaxError' })
    expect(checkEventData('code', outcome)).toMatchObject({
      status: 'error',
      message: 'SyntaxError',
    })
  })
})
