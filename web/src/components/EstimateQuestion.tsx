import { type FormEvent, useId, useState } from 'react'
import {
  acceptedRange,
  formatNear,
  formatNumber,
  matchingMistake,
  readNumber,
  relativeError,
  withinTolerance,
  withUnit,
} from '../content/estimates.ts'
import type { EstimateItem } from '../content/types.ts'
import { Markdown } from './Markdown.tsx'
import { Recorded } from './Recorded.tsx'
import { BUTTON, CODE_BOX, SECONDARY_BUTTON } from './styles.ts'

/** What the learner answered, for the answer event. */
export type EstimateAnswer = {
  /** What they typed, as they typed it. */
  typed: string
  /** The number it was read as. */
  number: number
  /** How far off, as a share of the answer: 0.22 for 22% high. */
  relativeError: number | null
  /** The known mistake a wrong answer matched, by id. */
  mistake: string | null
}

type Props = {
  item: EstimateItem
  /**
   * Called once, when the learner checks a number the box could read;
   * `answer` is null for "I don't know this" (placement only).
   */
  onAnswer?: (correct: boolean, answer: EstimateAnswer | null) => void
  /**
   * True in the placement test (ADR-0021): no word on whether it was right,
   * and an "I don't know this" button beside Check.
   */
  quiet?: boolean
}

const NOTE = 'text-sm text-slate-600 dark:text-slate-300'
const NUMBER_BOX =
  'w-40 rounded-md border border-slate-300 bg-white px-3 py-2 font-mono text-sm text-slate-900 aria-invalid:border-red-600 dark:border-slate-700'

/** The day prices were read, as a person says it: November 10, 2026. */
function dayOf(isoDate: string): string {
  return new Date(`${isoDate}T12:00:00Z`).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  })
}

/** Prices go out of date, so a question with prices says when they were read. */
function PricesNote({ asOf, source }: { asOf: string; source: string }) {
  return (
    <p className={NOTE}>
      These prices were read on {dayOf(asOf)}. Today's are on{' '}
      <a href={source} target="_blank" rel="noreferrer" className="underline">
        the provider's price page
      </a>
      ; expect them to differ.
    </p>
  )
}

/** A share as a whole percentage: 0.174 is "17%", 0.002 "less than 1%". */
function asPercent(share: number): string {
  const percent = Math.round(Math.abs(share) * 100)
  return percent === 0 ? 'less than 1%' : `${percent}%`
}

/**
 * How the learner's number compares with the answer, in the terms the
 * tolerance uses: a share for a percentage ("17% low"), the units for an
 * absolute one ("6 low").
 */
function howFar(number: number, item: EstimateItem, correct: boolean): string {
  const gap = number - item.answer
  if (gap === 0) return ''
  const share = relativeError(number, item.answer)
  const off =
    'percent' in item.tolerance && share !== null
      ? asPercent(share)
      : formatNear(Math.abs(gap), item.answer)
  const yours = `Yours, ${formatNumber(number)}, is ${off} ${gap > 0 ? 'high' : 'low'}`
  if (correct) return `${yours}: close enough.`
  if ('absolute' in item.tolerance && item.tolerance.absolute === 0) {
    return `${yours}, and this one must be exact.`
  }
  const [low, high] = acceptedRange(item)
  return `${yours}; anything from ${formatNear(low, item.answer)} to ${formatNear(high, item.answer)} counts.`
}

/** The working, then the given numbers it uses. */
function Working({ item }: { item: EstimateItem }) {
  const given = Object.entries(item.given)
    .map(([name, value]) => `${name} = ${value}`)
    .join(', ')
  return (
    <div className="space-y-1">
      <p className="text-sm font-medium">How it's worked out</p>
      <pre className={CODE_BOX}>{item.working}</pre>
      <p className={NOTE}>with {given}</p>
    </div>
  )
}

/**
 * A question whose answer is a number the learner works out and types
 * (ADR-0024). Producing the number is better practice than picking it from
 * a list, and a list would give away its size. A number within the item's
 * tolerance is right; a wrong one that matches a known mistake is told what
 * went wrong. Anything that can't be read as a number gets a note on how to
 * type it, and isn't counted.
 */
export function EstimateQuestion({ item, onAnswer, quiet = false }: Props) {
  const fieldId = useId()
  const unitId = useId()
  const problemId = useId()
  const [typed, setTyped] = useState('')
  const [problem, setProblem] = useState<string | null>(null)
  const [checked, setChecked] = useState<EstimateAnswer | null>(null)
  const [dontKnow, setDontKnow] = useState(false)

  function handleCheck(event: FormEvent) {
    event.preventDefault()
    const reading = readNumber(typed, item.unit)
    if (!reading.ok) {
      setProblem(reading.message)
      return
    }
    const { number } = reading
    const correct = withinTolerance(number, item)
    const answer: EstimateAnswer = {
      typed,
      number,
      relativeError: relativeError(number, item.answer),
      mistake: correct
        ? null
        : (matchingMistake(number, item.mistakes)?.id ?? null),
    }
    setProblem(null)
    setChecked(answer)
    onAnswer?.(correct, answer)
  }

  /** The placement test's way out of guessing: recorded as a wrong answer. */
  function handleDontKnow() {
    setProblem(null)
    setDontKnow(true)
    onAnswer?.(false, null)
  }

  const done = checked !== null || dontKnow
  return (
    <div className="space-y-3">
      <Markdown>{item.prompt}</Markdown>
      {item.prices_as_of && item.prices_source && (
        <PricesNote asOf={item.prices_as_of} source={item.prices_source} />
      )}
      <form onSubmit={handleCheck} className="space-y-2">
        <label htmlFor={fieldId} className="block text-sm font-medium">
          Your answer
        </label>
        <div className="flex flex-wrap items-center gap-2">
          <input
            id={fieldId}
            type="text"
            inputMode="decimal"
            autoComplete="off"
            spellCheck={false}
            value={typed}
            onChange={(event) => {
              setTyped(event.target.value)
              setProblem(null)
            }}
            disabled={done}
            aria-invalid={problem !== null}
            aria-describedby={problem ? `${unitId} ${problemId}` : unitId}
            className={NUMBER_BOX}
          />
          <span id={unitId}>{item.unit}</span>
        </div>
        {problem && (
          <output id={problemId} className={`block ${NOTE}`}>
            {problem}
          </output>
        )}
        {!done && (
          <div className="flex flex-wrap gap-2">
            <button
              type="submit"
              disabled={typed.trim() === ''}
              className={BUTTON}
            >
              Check
            </button>
            {quiet && (
              <button
                type="button"
                onClick={handleDontKnow}
                className={SECONDARY_BUTTON}
              >
                I don't know this
              </button>
            )}
          </div>
        )}
      </form>
      {done && quiet && <Recorded />}
      {checked && !quiet && <Feedback item={item} answer={checked} />}
    </div>
  )
}

/** Right or not, how far off, the slip if it was a known one, then why. */
function Feedback({
  item,
  answer,
}: {
  item: EstimateItem
  answer: EstimateAnswer
}) {
  const correct = withinTolerance(answer.number, item)
  const mistake = item.mistakes.find(({ id }) => id === answer.mistake)
  const far = howFar(answer.number, item, correct)
  return (
    <output className="block space-y-2 rounded-md bg-slate-100 p-3 dark:bg-slate-800">
      <p className="font-medium">
        {correct ? (
          <>
            <span aria-hidden="true">✓ </span>Correct!
          </>
        ) : (
          <>
            <span aria-hidden="true">✗ </span>Not quite.
          </>
        )}{' '}
        The answer is {withUnit(formatNumber(item.answer), item.unit)}.
      </p>
      {far && <p>{far}</p>}
      {mistake && (
        <div className="rounded-md border-l-4 border-amber-500 bg-white px-3 py-2 dark:bg-slate-900">
          <p className="text-sm font-medium">A common slip</p>
          <Markdown>{mistake.why}</Markdown>
        </div>
      )}
      <Working item={item} />
      <Markdown>{item.explanation}</Markdown>
    </output>
  )
}
