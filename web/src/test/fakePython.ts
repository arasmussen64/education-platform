// Stand-ins for the Python runner, so component tests don't need Pyodide.
import { vi } from 'vitest'
import type { CheckReport, TestResult } from '../python/protocol.ts'
import type { CheckOutcome, RunOptions, RunOutcome } from '../python/runner.ts'

/** A finished run (or one waiting for input) that printed `output`. */
export function printed(output: string, waiting = false): RunOutcome {
  return {
    kind: 'done',
    result: { output, error: null, waiting_for_input: waiting },
  }
}

/** A finished Check, with whatever report fields the test cares about. */
export function report(overrides: Partial<CheckReport>): CheckOutcome {
  return {
    kind: 'done',
    report: {
      status: 'ok',
      message: '',
      passed: 0,
      total: 0,
      results: [],
      ...overrides,
    },
  }
}

/** A Check where every one of `descriptions` passed. */
export function allPassed(...descriptions: string[]): CheckOutcome {
  const results: TestResult[] = descriptions.map((description, index) => ({
    name: `test_${index}`,
    description,
    outcome: 'pass',
    message: '',
  }))
  return report({ passed: results.length, total: results.length, results })
}

/** A Check where the one test, `description`, failed. */
export function oneFailed(description: string, message = ''): CheckOutcome {
  return report({
    passed: 0,
    total: 1,
    results: [{ name: 'test_0', description, outcome: 'fail', message }],
  })
}

/** A fake runner whose Run and Check give the outcomes you choose. */
export function fakeRunner(
  outcomes: { run?: RunOutcome; check?: CheckOutcome } = {},
) {
  return {
    start: vi.fn((): Promise<void> => Promise.resolve()),
    run: vi.fn((_code: string, _options?: RunOptions): Promise<RunOutcome> =>
      Promise.resolve(outcomes.run ?? printed('')),
    ),
    check: vi.fn(
      (
        _code: string,
        _tests: string,
        _options?: { timeLimitMs?: number },
      ): Promise<CheckOutcome> => Promise.resolve(outcomes.check ?? report({})),
    ),
  }
}
