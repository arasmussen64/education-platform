import { type ReactNode, useEffect, useState } from 'react'
import { DEFAULT_TIME_LIMIT_MS } from '../python/constants.ts'
import type {
  CheckReport,
  TestOutcome,
  TestResult,
} from '../python/protocol.ts'
import {
  type CheckOutcome,
  getPythonRunner,
  type PythonRunner,
  type RunOutcome,
} from '../python/runner.ts'
import { CodeEditor } from './CodeEditor.tsx'

type Runner = Pick<PythonRunner, 'start' | 'run' | 'check'>

type Props = {
  initialCode: string
  /** The exercise's tests (test_exercise.py). Without tests there's no Check button. */
  tests?: string
  /** Hidden tests show what they check, but not why they failed (v1 spec, F4). */
  hiddenTests?: boolean
  /** Tests pass a fake here; the app uses the shared runner. */
  runner?: Runner
}

type Status = 'starting' | 'ready' | 'running' | 'unavailable'

type Shown =
  | { kind: 'nothing' }
  | { kind: 'run'; outcome: RunOutcome }
  | { kind: 'check'; outcome: CheckOutcome }

const STATUS_TEXT: Record<Status, string> = {
  starting: 'Starting Python…',
  ready: '',
  running: 'Running…',
  unavailable: "Python couldn't start. Check your connection, then try again.",
}

const TIMEOUT_MESSAGE = `Your code ran for more than ${DEFAULT_TIME_LIMIT_MS / 1000} seconds, so it was stopped. Is there a loop that never ends?`

const BUTTON =
  'rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200'

/** A code editor with Run (and, for exercises, Check) buttons and results. */
export function CodeRunner({
  initialCode,
  tests,
  hiddenTests = false,
  runner,
}: Props) {
  const python = runner ?? getPythonRunner()
  const [code, setCode] = useState(initialCode)
  const [stdin, setStdin] = useState('')
  const [status, setStatus] = useState<Status>('starting')
  const [shown, setShown] = useState<Shown>({ kind: 'nothing' })

  useEffect(() => {
    let active = true
    python.start().then(
      () => {
        if (active) setStatus('ready')
      },
      () => {
        if (active) setStatus('unavailable')
      },
    )
    return () => {
      active = false
    }
  }, [python])

  async function handleRun() {
    setStatus('running')
    const outcome = await python.run(code, stdin)
    setShown({ kind: 'run', outcome })
    setStatus('ready')
  }

  async function handleCheck(exerciseTests: string) {
    setStatus('running')
    const outcome = await python.check(code, exerciseTests)
    setShown({ kind: 'check', outcome })
    setStatus('ready')
  }

  const busy = status === 'running'

  return (
    <div className="space-y-3">
      <CodeEditor
        initialCode={initialCode}
        onChange={setCode}
        label="Python code"
      />
      <p className="text-xs text-slate-500 dark:text-slate-400">
        Tip: press Esc, then Tab, to move out of the editor.
      </p>
      <label className="block text-sm">
        <span className="font-medium">Input for Run</span>{' '}
        <span className="text-slate-500 dark:text-slate-400">
          (one line for each input() call)
        </span>
        <textarea
          value={stdin}
          onChange={(event) => setStdin(event.target.value)}
          rows={2}
          className="mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 font-mono text-sm text-slate-900 dark:border-slate-700"
        />
      </label>
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={handleRun}
          disabled={busy}
          className={BUTTON}
        >
          Run
        </button>
        {tests !== undefined && (
          <button
            type="button"
            onClick={() => handleCheck(tests)}
            disabled={busy}
            className={BUTTON}
          >
            Check
          </button>
        )}
        {/* <output> is announced by screen readers when its text changes. */}
        <output className="text-sm text-slate-500 dark:text-slate-400">
          {STATUS_TEXT[status]}
        </output>
      </div>
      <div aria-live="polite">
        {shown.kind === 'run' && <RunResult outcome={shown.outcome} />}
        {shown.kind === 'check' && (
          <CheckResult outcome={shown.outcome} hidden={hiddenTests} />
        )}
      </div>
    </div>
  )
}

function RunResult({ outcome }: { outcome: RunOutcome }) {
  if (outcome.kind === 'timeout') {
    return <Notice tone="warning">{TIMEOUT_MESSAGE}</Notice>
  }
  if (outcome.kind === 'failed') {
    return (
      <Notice tone="error">
        Something went wrong running Python: {outcome.message}
      </Notice>
    )
  }
  const { output, error } = outcome.result
  return (
    <section aria-label="Output" className="space-y-2">
      {(output || !error) && (
        <pre className="overflow-x-auto rounded-md bg-slate-900 p-3 text-sm whitespace-pre-wrap text-slate-100">
          {output || 'Your program printed nothing.'}
        </pre>
      )}
      {error && (
        <pre className="overflow-x-auto rounded-md border border-red-300 bg-red-50 p-3 text-sm whitespace-pre-wrap text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100">
          {error}
        </pre>
      )}
    </section>
  )
}

function CheckResult({
  outcome,
  hidden,
}: {
  outcome: CheckOutcome
  hidden: boolean
}) {
  if (outcome.kind === 'timeout') {
    return <Notice tone="warning">{TIMEOUT_MESSAGE}</Notice>
  }
  if (outcome.kind === 'failed') {
    return (
      <Notice tone="error">
        Something went wrong running the checks: {outcome.message}
      </Notice>
    )
  }
  const report = outcome.report
  if (report.status === 'error') {
    return <Notice tone="error">{report.message}</Notice>
  }
  return (
    <section aria-label="Check results" className="space-y-2">
      <p className="font-medium">{checkSummary(report)}</p>
      <ul className="space-y-2">
        {report.results.map((result) => (
          <TestRow key={result.name} result={result} hidden={hidden} />
        ))}
      </ul>
    </section>
  )
}

/** A one-line summary that reads naturally for one check or many. */
function checkSummary(report: CheckReport): string {
  const { passed, total } = report
  if (total === 0) return 'This exercise has no checks yet.'
  if (total === 1) {
    return passed === 1 ? 'The check passed!' : "The check didn't pass yet."
  }
  return passed === total
    ? `All ${total} checks passed!`
    : `${passed} of ${total} checks passed`
}

const OUTCOME_LABEL: Record<TestOutcome, string> = {
  pass: 'Passed',
  fail: 'Failed',
  error: 'Error',
}

const OUTCOME_ICON: Record<TestOutcome, string> = {
  pass: '✓',
  fail: '✗',
  error: '!',
}

const OUTCOME_COLOR: Record<TestOutcome, string> = {
  pass: 'text-emerald-600 dark:text-emerald-400',
  fail: 'text-red-600 dark:text-red-400',
  error: 'text-amber-600 dark:text-amber-400',
}

function TestRow({ result, hidden }: { result: TestResult; hidden: boolean }) {
  // A hidden test's failure details could give the answer away, so only
  // errors in the learner's own code are shown for hidden tests.
  const showMessage =
    result.message !== '' && (!hidden || result.outcome === 'error')
  return (
    <li className="flex gap-2 text-sm">
      <span
        aria-hidden="true"
        className={`w-4 font-bold ${OUTCOME_COLOR[result.outcome]}`}
      >
        {OUTCOME_ICON[result.outcome]}
      </span>
      <div className="min-w-0">
        <p>
          <span className="sr-only">{OUTCOME_LABEL[result.outcome]}: </span>
          {result.description}
        </p>
        {showMessage && (
          <pre className="mt-1 overflow-x-auto text-xs whitespace-pre-wrap text-slate-600 dark:text-slate-400">
            {result.message}
          </pre>
        )}
      </div>
    </li>
  )
}

function Notice({
  tone,
  children,
}: {
  tone: 'warning' | 'error'
  children: ReactNode
}) {
  const colors =
    tone === 'error'
      ? 'border-red-300 bg-red-50 text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100'
      : 'border-amber-300 bg-amber-50 text-amber-900 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-100'
  return (
    <p className={`rounded-md border px-3 py-2 text-sm ${colors}`}>
      {children}
    </p>
  )
}
