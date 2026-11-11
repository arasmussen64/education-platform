import { describe, expect, it } from 'vitest'
import testrunner from '../../../harness/testrunner.py?raw'
import type { CheckOutcome } from '../python/runner.ts'
import { allPassed, oneFailed, report } from '../test/fakePython.ts'
import {
  checkCorrect,
  checkCouldNotRun,
  savedCheckCouldNotRun,
  TESTS_NOT_LOADED,
} from './checkGrade.ts'
import { checkEventData } from './payloads.ts'

describe('how a Check is graded', () => {
  it('is right when every test ran and passed', () => {
    expect(checkCorrect(allPassed('Greets', 'Says goodbye'))).toBe(true)
  })

  it('is wrong when a test ran and failed', () => {
    expect(checkCorrect(oneFailed('Greets'))).toBe(false)
  })

  it("is wrong when the learner's code ran past the time limit", () => {
    // A loop that never ends is the learner's own result. The runner turns a
    // slow package download into a failure, below, never into this.
    expect(checkCorrect({ kind: 'timeout' })).toBe(false)
  })

  it("is wrong when the learner's own code couldn't be loaded", () => {
    const outcome = report({
      status: 'error',
      message:
        "Your code couldn't be loaded. SyntaxError: invalid syntax (solution.py, line 2)",
    })
    expect(checkCorrect(outcome)).toBe(false)
  })

  it.each<[string, CheckOutcome]>([
    [
      "Python didn't start",
      {
        kind: 'failed',
        message: 'Failed to fetch dynamically imported module',
      },
    ],
    [
      'the packages took too long to load',
      {
        kind: 'failed',
        message:
          'Loading numpy took too long. Check your connection and try again.',
      },
    ],
    [
      'the worker crashed partway through',
      { kind: 'failed', message: 'Python stopped unexpectedly.' },
    ],
    [
      "the exercise's own tests couldn't be loaded",
      report({
        status: 'error',
        message: `${TESTS_NOT_LOADED} This is a problem with the exercise. ModuleNotFoundError: No module named 'numpy'`,
      }),
    ],
    ['the exercise has no tests', report({ status: 'ok', total: 0 })],
  ])('is neither when it could not run: %s', (_why, outcome) => {
    expect(checkCorrect(outcome)).toBeUndefined()
  })

  it("matches the harness's own words for tests that couldn't be loaded", () => {
    // The harness and the app are two programs: if its message changes, this
    // test says so before a broken exercise counts against a learner.
    expect(testrunner).toContain(`"${TESTS_NOT_LOADED} This is a problem`)
  })
})

describe('a Check that is already saved', () => {
  /** One of each kind of outcome, run or not. */
  const outcomes: [string, CheckOutcome][] = [
    ['every test passed', allPassed('Greets')],
    ['a test failed', oneFailed('Greets')],
    ['the time limit', { kind: 'timeout' }],
    [
      "the learner's code couldn't be loaded",
      report({ status: 'error', message: "Your code couldn't be loaded. x" }),
    ],
    ["Python didn't start", { kind: 'failed', message: 'No network' }],
    [
      "the tests couldn't be loaded",
      report({ status: 'error', message: `${TESTS_NOT_LOADED} x` }),
    ],
    ['no tests', report({ status: 'ok', total: 0 })],
  ]

  it.each(outcomes)(
    'is judged as it was when it happened: %s',
    (_what, outcome) => {
      // The data exactly as the page saves it.
      const saved = checkEventData('print("hi")', outcome)
      expect(savedCheckCouldNotRun(saved)).toBe(checkCouldNotRun(outcome))
    },
  )

  it.each<[string, Record<string, unknown>]>([
    ['a lab, which has no outcome', { runtime: 'lab', passed: 0, total: 2 }],
    ['nothing at all', {}],
    ['a total saved as text', { outcome: 'done', status: 'ok', total: '0' }],
    ['a message that is not text', { outcome: 'done', status: 'error' }],
  ])('counts as one that ran when its data says otherwise: %s', (_, data) => {
    expect(savedCheckCouldNotRun(data)).toBe(false)
  })
})
