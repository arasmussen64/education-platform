import { type ReactNode, useId, useRef, useState } from 'react'
import { Markdown } from './Markdown.tsx'
import { SECONDARY_BUTTON, TEXT_INPUT } from './styles.ts'

type Props = {
  /** The puzzling question, one or two sentences of Markdown. */
  question: string
  /** The answer, shown once the learner has typed a guess. */
  children?: ReactNode
  /** A place on the page the outline can point at (LessonView sets it). */
  id?: string
  'data-place'?: string
}

/**
 * An opening puzzle (ADR-0026): a question the lesson is about to answer,
 * first in the intro. The learner types a guess before the answer shows,
 * because wanting to know makes the answer stick (Gruber, Gelman & Ranganath
 * 2014), and a guess made first helps even when it's wrong (Richland,
 * Kornell & Kao 2009). The guess isn't graded and isn't saved anywhere: it
 * lives only while the page is open.
 */
export function Puzzle({ question, children, id, ...rest }: Props) {
  const [guess, setGuess] = useState('')
  const [revealed, setRevealed] = useState(false)
  // True after "Show the answer" with nothing typed, until a guess is.
  const [needGuess, setNeedGuess] = useState(false)
  const answer = useRef<HTMLParagraphElement>(null)
  const guessBox = useRef<HTMLTextAreaElement>(null)
  const ids = useId()
  const headingId = `${ids}-heading`
  const guessId = `${ids}-guess`
  const hintId = `${ids}-hint`

  return (
    <section
      id={id}
      data-place={rest['data-place']}
      aria-labelledby={headingId}
      className="space-y-3 rounded-lg border border-line-strong bg-card p-4"
    >
      <p
        id={headingId}
        className="text-sm font-semibold tracking-wide text-muted uppercase"
      >
        A puzzle to start
      </p>
      <div className="font-medium">
        <Markdown>{question}</Markdown>
      </div>
      {revealed ? (
        <div className="space-y-2">
          <p className="text-sm text-muted">
            <span className="font-semibold">Your guess:</span> {guess.trim()}
          </p>
          <div className="space-y-2 border-l-4 border-muted pl-3">
            <p
              ref={answer}
              tabIndex={-1}
              className="font-semibold outline-none"
            >
              The answer
            </p>
            {children}
          </div>
        </div>
      ) : (
        <form
          className="space-y-2"
          onSubmit={(event) => {
            event.preventDefault()
            if (!guess.trim()) {
              setNeedGuess(true)
              guessBox.current?.focus()
              return
            }
            setRevealed(true)
            // Once the answer is on the page, take the learner (and a screen
            // reader) to it.
            requestAnimationFrame(() => answer.current?.focus())
          }}
        >
          <label htmlFor={guessId} className="block text-sm font-medium">
            Your guess
          </label>
          <textarea
            ref={guessBox}
            id={guessId}
            rows={2}
            value={guess}
            aria-describedby={hintId}
            onChange={(event) => {
              setGuess(event.target.value)
              if (event.target.value.trim()) setNeedGuess(false)
            }}
            className={TEXT_INPUT}
          />
          <p
            id={hintId}
            className={`text-sm ${needGuess ? 'font-medium text-ink' : 'text-muted'}`}
          >
            {needGuess
              ? 'Type a guess first: any guess, even "no idea, maybe…". Guessing before you read helps you remember the answer, even when the guess is wrong.'
              : "It isn't marked and isn't saved. A wrong guess helps as much as a right one."}
          </p>
          <button type="submit" className={SECONDARY_BUTTON}>
            Show the answer
          </button>
        </form>
      )}
    </section>
  )
}
