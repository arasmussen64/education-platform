// Stand-ins for the Python runner, so component tests don't need Pyodide.
import { vi } from 'vitest'
import type {
  CheckReport,
  TestResult,
  TraceResult,
  TraceStep,
} from '../python/protocol.ts'
import type {
  CheckOutcome,
  RunOptions,
  RunOutcome,
  TraceOutcome,
} from '../python/runner.ts'

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

/** The program `x = 1`, `y = x + 1`, `print(x, y)`, stepped through. */
export const SIMPLE_CODE = 'x = 1\ny = x + 1\nprint(x, y)\n'
export const SIMPLE_STEPS: TraceStep[] = [
  { line: 1, event: 'line', frames: [program(1, [])], out_len: 0 },
  { line: 2, event: 'line', frames: [program(2, [['x', '1']])], out_len: 0 },
  {
    line: 3,
    event: 'line',
    frames: [
      program(3, [
        ['x', '1'],
        ['y', '2'],
      ]),
    ],
    out_len: 0,
  },
  {
    line: 3,
    event: 'return',
    frames: [
      program(3, [
        ['x', '1'],
        ['y', '2'],
      ]),
    ],
    out_len: 4,
  },
]

function program(line: number, vars: [string, string][]) {
  return { name: 'program', line, vars, returns: null }
}

/** A finished Step through, with whatever the test cares about changed. */
export function traced(overrides: Partial<TraceResult> = {}): TraceOutcome {
  return {
    kind: 'done',
    trace: {
      steps: SIMPLE_STEPS,
      output: '1 2\n',
      error: null,
      waiting_for_input: false,
      truncated: false,
      ...overrides,
    },
  }
}

/** A fake runner whose Run, Check and Step through give the outcomes you choose. */
export function fakeRunner(
  outcomes: {
    run?: RunOutcome
    check?: CheckOutcome
    trace?: TraceOutcome
  } = {},
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
    trace: vi.fn(
      (_code: string, _options?: RunOptions): Promise<TraceOutcome> =>
        Promise.resolve(outcomes.trace ?? traced()),
    ),
  }
}
