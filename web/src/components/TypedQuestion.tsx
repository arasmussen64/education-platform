import { type FormEvent, type ReactNode, useId, useRef, useState } from 'react'
import type { Confidence } from '../confidence/confidence.ts'
import { gradeTyped, type TypedGrade } from '../content/typed.ts'
import type { TypedItem } from '../content/types.ts'
import { ConfidenceButtons, ConfidenceNote } from './Confidence.tsx'
import { Markdown } from './Markdown.tsx'
import { Recorded } from './Recorded.tsx'
import { BUTTON, SECONDARY_BUTTON } from './styles.ts'

/** What the learner answered, for the answer event. */
export type TypedAnswer = {
  /** What they typed, as they typed it. */
  typed: string
  /** The known mistake it matched, by id, or null. */
  mistake: string | null
  /** True when it was right but for one slip among its letters. */
  slip: boolean
}

type Props = {
  item: TypedItem
  /**
   * Called once, when the learner checks what they typed; `answer` is null
   * for "I don't know this" (placement only). `confidence` is how sure the
   * learner said they were (ADR-0028), or null in the placement test,
   * which doesn't ask.
   */
  onAnswer?: (
    correct: boolean,
    answer: TypedAnswer | null,
    confidence: Confidence | null,
  ) => void
  /**
   * True in the placement test (ADR-0021): no word on whether it was right,
   * and an "I don't know this" button beside Check.
   */
  quiet?: boolean
}

const BOX =
  'w-full min-w-0 rounded-md border border-line-strong bg-card px-3 py-2 text-sm text-ink'

/** An answer as the page shows it: as code for a command, as text otherwise. */
function Shown({ item, text }: { item: TypedItem; text: string }): ReactNode {
  // Shown inside a sunken box, which in dark mode is the same colour as the
  // usual shade behind code (line); the card colour shows there instead.
  return item.kind === 'command' ? (
    <code className="rounded bg-line px-1 font-mono text-[0.9em] wrap-anywhere dark:bg-card">
      {text}
    </code>
  ) : (
    <strong className="wrap-anywhere">{text}</strong>
  )
}

/**
 * A question whose answer the learner types from memory: a command, a
 * term, a value or a short phrase (ADR-0027). Recalling the answer builds
 * memory better than picking it from a list (Kang, McDermott and Roediger,
 * 2007).
 * What's typed is read forgivingly, the item's way: spaces, quotes, a
 * copied "$ " prompt and, for text, case and one slip of the fingers don't
 * count against it.
 */
export function TypedQuestion({ item, onAnswer, quiet = false }: Props) {
  const fieldId = useId()
  const [typed, setTyped] = useState('')
  const [checked, setChecked] = useState<TypedGrade | null>(null)
  const [dontKnow, setDontKnow] = useState(false)
  const [confidence, setConfidence] = useState<Confidence | null>(null)
  const firstChoice = useRef<HTMLButtonElement>(null)
  const isCommand = item.kind === 'command'

  /**
   * Enter in the box. In the placement test it's Check. Elsewhere it would
   * have to pick how sure the learner is for them, so it moves on to the
   * three buttons instead (ADR-0028).
   */
  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (typed.trim() === '') return
    if (quiet) check(null)
    else firstChoice.current?.focus()
  }

  function check(sure: Confidence | null) {
    if (typed.trim() === '' || checked) return
    const grade = gradeTyped(item, typed)
    setChecked(grade)
    setConfidence(sure)
    onAnswer?.(
      grade.correct,
      { typed, mistake: grade.mistake, slip: grade.slip },
      sure,
    )
  }

  /** The placement test's way out of guessing: recorded as a wrong answer. */
  function handleDontKnow() {
    setDontKnow(true)
    onAnswer?.(false, null, null)
  }

  const done = checked !== null || dontKnow
  return (
    <div className="space-y-3">
      <Markdown>{item.prompt}</Markdown>
      <form onSubmit={handleSubmit} className="space-y-2">
        <label htmlFor={fieldId} className="block text-sm font-medium">
          {isCommand ? 'Your command' : 'Your answer'}
        </label>
        <div className="flex items-center gap-2">
          {isCommand && (
            <span aria-hidden="true" className="font-mono text-sm">
              $
            </span>
          )}
          <input
            id={fieldId}
            type="text"
            // What's recalled is the learner's own: no phone keyboard
            // capitalising a command or "correcting" a term.
            autoComplete="off"
            autoCapitalize="none"
            autoCorrect="off"
            spellCheck={false}
            value={typed}
            onChange={(event) => setTyped(event.target.value)}
            disabled={done}
            className={`${BOX} ${isCommand ? 'font-mono' : ''}`}
          />
        </div>
        {!done && quiet && (
          <div className="flex flex-wrap gap-2">
            <button
              type="submit"
              disabled={typed.trim() === ''}
              className={BUTTON}
            >
              Check
            </button>
            <button
              type="button"
              onClick={handleDontKnow}
              className={SECONDARY_BUTTON}
            >
              I don't know this
            </button>
          </div>
        )}
        {!done && !quiet && (
          <ConfidenceButtons
            onPick={check}
            disabled={typed.trim() === ''}
            firstRef={firstChoice}
          />
        )}
      </form>
      {done && quiet && <Recorded />}
      {checked && !quiet && (
        <Feedback item={item} grade={checked} confidence={confidence} />
      )}
    </div>
  )
}

/** Right or not, the answer, the slip if it was a known one, then why. */
function Feedback({
  item,
  grade,
  confidence,
}: {
  item: TypedItem
  grade: TypedGrade
  confidence: Confidence | null
}) {
  const [first = ''] = item.answers
  const mistake = item.mistakes.find(({ id }) => id === grade.mistake)
  const others = item.answers.filter((answer) => answer !== grade.matched)
  const alsoAccepted = grade.correct ? others : item.answers.slice(1)
  return (
    <output className="block space-y-2 rounded-md bg-sunken p-3">
      <p className="font-medium">
        {grade.correct ? (
          <>
            <span aria-hidden="true">✓ </span>Correct!
          </>
        ) : (
          <>
            <span aria-hidden="true">✗ </span>Not quite. The answer is{' '}
            <Shown item={item} text={first} />.
          </>
        )}
      </p>
      {grade.slip && grade.matched !== null && (
        <p>
          Watch the spelling: it's <Shown item={item} text={grade.matched} />.
        </p>
      )}
      <ConfidenceNote confidence={confidence} correct={grade.correct} />
      {mistake && (
        <div className="rounded-md border-l-4 border-amber-500 bg-card px-3 py-2">
          <p className="text-sm font-medium">A common slip</p>
          <Markdown>{mistake.why}</Markdown>
        </div>
      )}
      {alsoAccepted.length > 0 && (
        <p className="text-sm text-muted">
          {grade.correct ? 'Also right: ' : 'Also accepted: '}
          {alsoAccepted.map((answer, index) => (
            <span key={answer}>
              {index > 0 && ', '}
              <Shown item={item} text={answer} />
            </span>
          ))}
        </p>
      )}
      <Markdown>{item.explanation}</Markdown>
    </output>
  )
}
