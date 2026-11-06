import { type ReactNode, useEffect, useRef, useState } from 'react'
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

/**
 * One press of Run. When the program stops at input(), the learner types a
 * line and the program runs again from the start with every line so far,
 * using the code and random seed it started with, so it behaves the same up
 * to the new input.
 */
type RunSession = {
  code: string
  seed: number
  inputs: string[]
  outcome: RunOutcome
}

type Shown =
  | { kind: 'nothing' }
  | { kind: 'run'; session: RunSession }
  | { kind: 'check'; outcome: CheckOutcome }

function newSeed(): number {
  return Math.floor(Math.random() * 2 ** 31)
}

function toStdin(lines: string[]): string {
  return lines.map((line) => `${line}\n`).join('')
}

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

  async function runSession(session: Omit<RunSession, 'outcome'>) {
    setStatus('running')
    const outcome = await python.run(session.code, {
      stdin: toStdin(session.inputs),
      seed: session.seed,
    })
    setShown({ kind: 'run', session: { ...session, outcome } })
    setStatus('ready')
  }

  function handleRun() {
    return runSession({ code, seed: newSeed(), inputs: [] })
  }

  function handleInput(line: string) {
    if (shown.kind !== 'run') return
    const { session } = shown
    return runSession({ ...session, inputs: [...session.inputs, line] })
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
        {shown.kind === 'run' && (
          <Terminal session={shown.session} busy={busy} onInput={handleInput} />
        )}
        {shown.kind === 'check' && (
          <CheckResult outcome={shown.outcome} hidden={hiddenTests} />
        )}
      </div>
    </div>
  )
}

/** The program's output, shown like a terminal, including typing input. */
function Terminal({
  session,
  busy,
  onInput,
}: {
  session: RunSession
  busy: boolean
  onInput: (line: string) => void
}) {
  const { outcome } = session
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
  const { output, error, waiting_for_input: waiting } = outcome.result
  const printedNothing = !output && !error && !waiting
  return (
    <section aria-label="Output" className="space-y-2">
      {(output || waiting || printedNothing) && (
        <div className="overflow-x-auto rounded-md bg-slate-900 p-3 font-mono text-sm whitespace-pre-wrap text-slate-100">
          {output}
          {waiting && (
            // A new line of input gets a fresh field (key), so it starts
            // empty and takes the focus again.
            <InputLine
              key={session.inputs.length}
              disabled={busy}
              onSubmit={onInput}
            />
          )}
          {printedNothing && (
            <span className="text-slate-400">
              Your program printed nothing.
            </span>
          )}
        </div>
      )}
      {waiting && (
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Your program is waiting for input. Type your answer and press Enter.
        </p>
      )}
      {error && (
        <pre className="overflow-x-auto rounded-md border border-red-300 bg-red-50 p-3 text-sm whitespace-pre-wrap text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100">
          {error}
        </pre>
      )}
    </section>
  )
}

/** A text field right after the program's prompt, like typing in a terminal. */
function InputLine({
  disabled,
  onSubmit,
}: {
  disabled: boolean
  onSubmit: (line: string) => void
}) {
  const lineRef = useRef<HTMLSpanElement>(null)

  // Put the cursor here as soon as the program asks, as a terminal would.
  useEffect(() => {
    lineRef.current?.focus()
  }, [])

  // This is an editable <span>, not an <input>, on purpose. Password managers
  // and autofill extensions only look at real form fields, and a prompt like
  // "What's your name?" makes an <input> look like a contact form to them
  // (NordPass, for one, has no way for a page to opt out). Screen readers
  // still announce it as a text box, through role="textbox".
  return (
    <span
      ref={lineRef}
      // An <input> is exactly what we're avoiding here (see above).
      // oxlint-disable-next-line jsx-a11y/prefer-tag-over-role
      role="textbox"
      aria-label="Program input"
      aria-multiline="false"
      aria-disabled={disabled || undefined}
      contentEditable={!disabled}
      tabIndex={disabled ? -1 : 0}
      spellCheck={false}
      autoCapitalize="off"
      autoCorrect="off"
      enterKeyHint="enter"
      onKeyDown={(event) => {
        // Ignore the Enter that finishes an input-method composition (e.g.
        // typing Japanese); only a plain Enter sends the line.
        if (event.key === 'Enter' && !event.nativeEvent.isComposing) {
          event.preventDefault()
          onSubmit(event.currentTarget.textContent ?? '')
        }
      }}
      onPaste={(event) => {
        // Paste as plain text on one line, never formatting or images.
        event.preventDefault()
        const text = event.clipboardData
          .getData('text/plain')
          .replace(/\r?\n/g, ' ')
        document.execCommand('insertText', false, text)
      }}
      className="inline-block min-w-48 rounded border border-slate-500 bg-slate-800 px-1 text-slate-100 outline-none focus:border-lime-400"
    />
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
