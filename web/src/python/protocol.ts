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

export type WorkerResponse =
  | { type: 'ready' }
  | { type: 'load-error'; message: string }
  | { id: number; type: 'run-result'; result: ProgramResult }
  | { id: number; type: 'check-result'; report: CheckReport }
  | { id: number; type: 'internal-error'; message: string }
