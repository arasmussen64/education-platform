import { describe, expect, it } from 'vitest'
import testrunner from '../../../harness/testrunner.py?raw'
import type { CheckOutcome } from '../python/runner.ts'
import { allPassed, oneFailed, report } from '../test/fakePython.ts'
import { checkCorrect, TESTS_NOT_LOADED } from './checkGrade.ts'

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
