// The shapes of data passed between the app and the Python worker.
// The Python side of these lives in harness/program.py and harness/testrunner.py.

/** What the Run button gets back (harness/program.py). */
export type ProgramResult = {
  output: string
  /** A traceback trimmed to the learner's file, or null if nothing crashed. */
  error: string | null
  /**
   * True when the program stopped at input() because it needs another line.
   * The app asks the learner, then runs the program again from the start
   * with every line typed so far (and the same random seed).
   */
  waiting_for_input: boolean
}

/** One function call that's running, in a step (harness/tracer.py). */
export type TraceFrame = {
  /** "program" for the program itself, else the function's name. */
  name: string
  line: number
  /** Name and value (as text), in the order the names were made. */
  vars: [string, string][]
  /** The value being returned, on a return step. */
  returns: string | null
}

/** One moment of a program, for the Step through button (ADR-0022). */
export type TraceStep = {
  line: number
  /**
   * "line": about to run the line. "call": a function was just called.
   * "return": it's returning. "exception": an error was raised here.
   */
  event: 'line' | 'call' | 'return' | 'exception'
  /** The calls that are running: the program first, the innermost last. */
  frames: TraceFrame[]
  /** How much of `output` had been printed by then. */
  out_len: number
}

/** What the Step through button gets back (harness/tracer.py). */
export type TraceResult = {
  steps: TraceStep[]
  output: string
  error: string | null
  waiting_for_input: boolean
  /** True when the recording stopped at the step limit. */
  truncated: boolean
}

export type TestOutcome = 'pass' | 'fail' | 'error'

export type TestResult = {
  name: string
  /** The first line of the test's docstring. */
  description: string
  outcome: TestOutcome
  message: string
}

/** What the Check button gets back (harness/testrunner.py). */
export type CheckReport = {
  /** "error" means the tests couldn't run at all; see `message`. */
  status: 'ok' | 'error'
  message: string
  passed: number
  total: number
  results: TestResult[]
}

export type WorkerRequest =
  | {
      id: number
      type: 'run'
      code: string
      stdin: string
      /** Seeds Python's random module, so re-runs make the same choices. */
      seed: number | null
    }
  | { id: number; type: 'check'; code: string; tests: string }
  | {
      id: number
      type: 'trace'
      code: string
      stdin: string
      seed: number | null
    }

export type WorkerResponse =
  | { type: 'ready' }
  | { type: 'load-error'; message: string }
  | { id: number; type: 'run-result'; result: ProgramResult }
  | { id: number; type: 'check-result'; report: CheckReport }
  | { id: number; type: 'trace-result'; trace: TraceResult }
  | { id: number; type: 'internal-error'; message: string }
