import { useId, useState } from 'react'
import type { TraceFrame, TraceResult } from '../python/protocol.ts'
import { describeStep } from './stepText.ts'
import { CODE_BOX, SECONDARY_BUTTON } from './styles.ts'

type Props = {
  /** The program that was traced, as it was run. */
  code: string
  trace: TraceResult
}

/**
 * A program played back one step at a time (ADR-0022): the line about to
 * run, every running call's variables at that moment, and the output so
 * far. Reading and tracing code is a skill of its own, and seeing the
 * machine's view of each line is how the "notional machine" gets built
 * (docs/learning-science.md).
 */
export function StepThrough({ code, trace }: Props) {
  const headingId = useId()
  const [at, setAt] = useState(0)
  const { steps } = trace
  const step = steps[at]
  const last = steps.length - 1
  const lines = code.replace(/\n$/, '').split('\n')

  if (!step) {
    return (
      <section aria-labelledby={headingId} className="space-y-2">
        <h4 id={headingId} className="font-semibold">
          Step through
        </h4>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Nothing to step through: the program didn't get to its first line.
        </p>
        {trace.error && <ErrorBox text={trace.error} />}
      </section>
    )
  }

  return (
    <section aria-labelledby={headingId} className="space-y-3">
      <h4 id={headingId} className="font-semibold">
        Step through
      </h4>
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={() => setAt(0)}
          disabled={at === 0}
          className={SECONDARY_BUTTON}
        >
          First
        </button>
        <button
          type="button"
          onClick={() => setAt(at - 1)}
          disabled={at === 0}
          className={SECONDARY_BUTTON}
        >
          Back
        </button>
        <button
          type="button"
          onClick={() => setAt(at + 1)}
          disabled={at >= last}
          className={SECONDARY_BUTTON}
        >
          Next
        </button>
        <button
          type="button"
          onClick={() => setAt(last)}
          disabled={at >= last}
          className={SECONDARY_BUTTON}
        >
          Last
        </button>
        <label className="flex items-center gap-2 text-sm">
          <span>
            Step {at + 1} of {steps.length}
          </span>
          <input
            type="range"
            min={0}
            max={last}
            value={at}
            onChange={(event) => setAt(Number(event.target.value))}
            aria-label="Step"
          />
        </label>
      </div>
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block font-medium">{describeStep(step, trace)}</output>
      <div className="grid gap-3 md:grid-cols-2">
        <pre className={`${CODE_BOX} overflow-x-auto`} aria-label="Code">
          {lines.map((text, index) => {
            const number = index + 1
            const current = number === step.line
            return (
              <div
                key={number}
                aria-current={current ? 'step' : undefined}
                className={
                  current
                    ? 'rounded bg-amber-200/60 font-semibold dark:bg-amber-900/60'
                    : ''
                }
              >
                <span aria-hidden="true" className="inline-block w-4">
                  {current ? '→' : ''}
                </span>
                <span className="inline-block w-8 text-right text-slate-400 select-none">
                  {number}
                </span>{' '}
                {text}
              </div>
            )
          })}
        </pre>
        <div className="space-y-3">
          {[...step.frames].reverse().map((frame, index) => (
            <FrameTable key={`${index}-${frame.name}`} frame={frame} />
          ))}
          <div className="space-y-1">
            <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400">
              Output so far
            </p>
            <pre className={`${CODE_BOX} whitespace-pre-wrap`}>
              {trace.output.slice(0, step.out_len) || (
                <span className="text-slate-400">Nothing printed yet</span>
              )}
            </pre>
          </div>
        </div>
      </div>
      {at === last && trace.error && <ErrorBox text={trace.error} />}
      {at === last && trace.truncated && (
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Recording stopped after {steps.length} steps. The program went on
          without being recorded; Run shows everything it prints.
        </p>
      )}
      {at === last && trace.waiting_for_input && (
        <p className="text-sm text-slate-600 dark:text-slate-400">
          The program asked for more input than it was given. Press Run, answer
          its questions, then step through again: it uses what you typed.
        </p>
      )}
    </section>
  )
}

/** One running call's variables. */
function FrameTable({ frame }: { frame: TraceFrame }) {
  const title = frame.name === 'program' ? 'The program' : `${frame.name}()`
  return (
    <table className="w-full text-sm" aria-label={`Variables: ${title}`}>
      <caption className="text-left text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400">
        {title}
        {frame.returns !== null && (
          <span className="normal-case">
            {' '}
            returns <code>{frame.returns}</code>
          </span>
        )}
      </caption>
      <tbody>
        {frame.vars.length === 0 ? (
          <tr>
            <td className="py-0.5 text-slate-500 dark:text-slate-400">
              No variables yet
            </td>
          </tr>
        ) : (
          frame.vars.map(([name, value]) => (
            <tr
              key={name}
              className="border-t border-slate-200 dark:border-slate-700"
            >
              <th
                scope="row"
                className="py-0.5 pr-3 text-left font-mono font-medium"
              >
                {name}
              </th>
              <td className="py-0.5 font-mono break-all">{value}</td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  )
}

function ErrorBox({ text }: { text: string }) {
  return (
    <pre className="overflow-x-auto rounded-md border border-red-300 bg-red-50 p-3 text-sm whitespace-pre-wrap text-red-900 dark:border-red-800 dark:bg-red-950 dark:text-red-100">
      {text}
    </pre>
  )
}
