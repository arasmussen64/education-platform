import { type ReactNode, useEffect, useRef, useState } from 'react'
import type { DraftKey } from '../drafts/drafts.ts'
import { useDraft } from '../drafts/useDraft.ts'
import { DEFAULT_TIME_LIMIT_MS } from '../python/constants.ts'
import type {
  CheckReport,
  TestOutcome,
  TestResult,
} from '../python/protocol.ts'
import {
  allChecksPassed,
  type CheckOutcome,
  getPythonRunner,
  type PythonRunner,
  type RunOutcome,
  type TraceOutcome,
} from '../python/runner.ts'
import { CodeEditor } from './CodeEditor.tsx'
import { StepThrough } from './StepThrough.tsx'
import { BUTTON, CODE_BOX, SECONDARY_BUTTON } from './styles.ts'

type Runner = Pick<PythonRunner, 'start' | 'run' | 'check' | 'trace'>

/** One shared empty list, so a re-render doesn't look like new packages. */
const NO_PACKAGES: string[] = []

type Props = {
  /** The starter: the code the editor shows when there's no draft. */
  initialCode: string
  /**
   * Where to keep the learner's draft on this device, so leaving and coming
   * back doesn't lose what they typed. Without it, nothing is kept.
   */
  draft?: DraftKey
  /** The exercise's tests (test_exercise.py). Without tests there's no Check button. */
  tests?: string
  /** Hidden tests show what they check, but not why they failed (v1 spec, F4). */
  hiddenTests?: boolean
  /** Tests pass a fake here; the app uses the shared runner. */
  runner?: Runner
  /** Called after each press of Run, with the code and its result. */
  onRun?: (outcome: RunOutcome, code: string) => void
  /** Called with every Check result and the code that was checked. */
  onCheck?: (outcome: CheckOutcome, code: string) => void
  /** Called after each press of Step through, with the code and its trace (ADR-0022). */
  onTrace?: (outcome: TraceOutcome, code: string) => void
  /** Called as the learner types, with the code as it is now. */
  onCodeChange?: (code: string) => void
  /** How long the code may run before it's stopped. */
  timeLimitMs?: number
  /** The topic's packages, loaded before the first run (ADR-0023). */
  packages?: string[]
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
  /** A Step through: the code as traced, and the input it was given. */
  | { kind: 'trace'; code: string; inputs: string[]; outcome: TraceOutcome }

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

// Not "the code it started with": after a draft is brought back, the editor
// started this visit with the draft, and Start over goes back further.
const START_OVER_QUESTION =
  'Start over? Your changes will be lost, and the editor will go back to the starting code.'

function timeoutMessage(timeLimitMs: number): string {
  const seconds = timeLimitMs / 1000
  return `Your code ran for more than ${seconds} ${seconds === 1 ? 'second' : 'seconds'}, so it was stopped. Is there a loop that never ends?`
}

/** A code editor with Run (and, for exercises, Check) buttons and results. */
export function CodeRunner({
  initialCode,
  draft: draftKey,
  tests,
  hiddenTests = false,
  runner,
  onRun,
  onCheck,
  onTrace,
  onCodeChange,
  timeLimitMs = DEFAULT_TIME_LIMIT_MS,
  packages = NO_PACKAGES,
}: Props) {
  const python = runner ?? getPythonRunner()
  const draft = useDraft(draftKey, initialCode)
  const [code, setCode] = useState(draft.initial)
  const [status, setStatus] = useState<Status>('starting')
  const [shown, setShown] = useState<Shown>({ kind: 'nothing' })
  // Each Start over builds a fresh editor (a new React key), showing the
  // starter; before the first, the editor shows the draft, if there was one.
  const [startOvers, setStartOvers] = useState(0)
  const editorStart = startOvers === 0 ? draft.initial : initialCode

  // A restored draft is the code now, not the starter the parent passed in,
  // so the parent hears about it (the tutor reads the code), once.
  const onCodeChangeRef = useRef(onCodeChange)
  useEffect(() => {
    if (draft.restored) onCodeChangeRef.current?.(draft.initial)
  }, [draft.restored, draft.initial])

  function handleEdit(next: string) {
    setCode(next)
    draft.save(next)
    onCodeChange?.(next)
  }

  function startOver() {
    if (!window.confirm(START_OVER_QUESTION)) return
    draft.discard()
    setStartOvers(startOvers + 1)
    setCode(initialCode)
    onCodeChange?.(initialCode)
  }

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
      timeLimitMs,
      packages,
    })
    setShown({ kind: 'run', session: { ...session, outcome } })
    setStatus('ready')
    return outcome
  }

  async function handleRun() {
    const outcome = await runSession({ code, seed: newSeed(), inputs: [] })
    // Lines typed into a waiting program re-run it, but only the press of
    // Run itself is reported.
    onRun?.(outcome, code)
  }

  function handleInput(line: string) {
    if (shown.kind !== 'run') return
    const { session } = shown
    return runSession({ ...session, inputs: [...session.inputs, line] })
  }

  /**
   * Step through (ADR-0022): the same run, recorded. It gets the input and
   * random seed of the last Run, if there was one, so it plays back what the
   * learner just saw.
   */
  async function handleStepThrough() {
    const previous =
      shown.kind === 'run'
        ? { inputs: shown.session.inputs, seed: shown.session.seed }
        : shown.kind === 'trace'
          ? { inputs: shown.inputs, seed: newSeed() }
          : { inputs: [], seed: newSeed() }
    setStatus('running')
    const outcome = await python.trace(code, {
      stdin: toStdin(previous.inputs),
      seed: previous.seed,
      timeLimitMs,
      packages,
    })
    setShown({ kind: 'trace', code, inputs: previous.inputs, outcome })
    setStatus('ready')
    onTrace?.(outcome, code)
  }

  async function handleCheck(exerciseTests: string) {
    setStatus('running')
    const outcome = await python.check(code, exerciseTests, {
      timeLimitMs,
      packages,
    })
    setShown({ kind: 'check', outcome })
    setStatus('ready')
    // Passed: the draft has done its job, and the next visit starts fresh.
    if (allChecksPassed(outcome)) draft.finish()
    onCheck?.(outcome, code)
  }

  const busy = status === 'running'

  return (
    <div className="space-y-3">
      <CodeEditor
        key={startOvers}
        initialCode={editorStart}
        onChange={handleEdit}
        label="Python code"
        // Start over removes its own button, so the cursor goes to the
        // fresh editor instead of being lost.
        focusOnStart={startOvers > 0}
      />
      <p className="text-xs text-slate-500 dark:text-slate-400">
        {draft.restored &&
          startOvers === 0 &&
          'This is your code from last time, kept on this device. '}
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
        <button
          type="button"
          onClick={handleStepThrough}
          disabled={busy}
          className={SECONDARY_BUTTON}
          title="Run the program one line at a time, watching the variables"
        >
          Step through
        </button>
        {code !== initialCode && (
          <button
            type="button"
            onClick={startOver}
            disabled={busy}
            className={SECONDARY_BUTTON}
          >
            Start over
          </button>
        )}
        {/* <output> is announced by screen readers when its text changes. */}
        <output className="text-sm text-slate-500 dark:text-slate-400">
          {STATUS_TEXT[status]}
        </output>
      </div>
      <div aria-live="polite">
        {shown.kind === 'run' && (
          <Terminal
            session={shown.session}
            busy={busy}
            onInput={handleInput}
            timeLimitMs={timeLimitMs}
          />
        )}
        {shown.kind === 'check' && (
          <CheckResult
            outcome={shown.outcome}
            hidden={hiddenTests}
            timeLimitMs={timeLimitMs}
          />
        )}
        {shown.kind === 'trace' && (
          <TraceView
            code={shown.code}
            outcome={shown.outcome}
            timeLimitMs={timeLimitMs}
          />
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
  timeLimitMs,
}: {
  session: RunSession
  busy: boolean
  onInput: (line: string) => void
  timeLimitMs: number
}) {
  const { outcome } = session
  if (outcome.kind === 'timeout') {
    return <Notice tone="warning">{timeoutMessage(timeLimitMs)}</Notice>
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
        <div className={`${CODE_BOX} whitespace-pre-wrap`}>
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

/** The Step through button's result: the player, or what went wrong. */
export function TraceView({
  code,
  outcome,
  timeLimitMs,
}: {
  code: string
  outcome: TraceOutcome
  timeLimitMs: number
}) {
  if (outcome.kind === 'timeout') {
    return <Notice tone="warning">{timeoutMessage(timeLimitMs)}</Notice>
  }
  if (outcome.kind === 'failed') {
    return (
      <Notice tone="error">
        Something went wrong stepping through: {outcome.message}
      </Notice>
    )
  }
  return <StepThrough code={code} trace={outcome.trace} />
}

function CheckResult({
  outcome,
  hidden,
  timeLimitMs,
}: {
  outcome: CheckOutcome
  hidden: boolean
  timeLimitMs: number
}) {
  if (outcome.kind === 'timeout') {
    return <Notice tone="warning">{timeoutMessage(timeLimitMs)}</Notice>
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
