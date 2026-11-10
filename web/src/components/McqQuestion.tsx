import { useId, useMemo, useState } from 'react'
import type { McqItem } from '../content/types.ts'
import { Markdown } from './Markdown.tsx'
import { Recorded } from './Recorded.tsx'
import { choiceOrder } from './scramble.ts'
import { BUTTON, INLINE_CODE } from './styles.ts'

type Props = {
  item: McqItem
  /**
   * Called once, when the learner checks their answer. `choice` is the
   * author's index, or null for "I don't know this" (placement only).
   */
  onAnswer?: (correct: boolean, choice: number | null) => void
  /**
   * True in the placement test (ADR-0021): the answer is taken without
   * saying whether it was right, so the test measures instead of teaching,
   * and "I don't know this" is offered so that nobody has to guess.
   */
  quiet?: boolean
}

/** What the learner picked: a choice's index, or the way out of guessing. */
type Picked = number | 'unknown'

/**
 * A multiple-choice question. The learner commits to an answer before seeing
 * whether it's right and why (retrieval practice). The choices are shown in a
 * repeatable shuffled order so their position gives nothing away; `choice` is
 * always the author's index, which is what gets recorded.
 */
export function McqQuestion({ item, onAnswer, quiet = false }: Props) {
  const promptId = useId()
  const order = useMemo(() => choiceOrder(item), [item])
  const [choice, setChoice] = useState<Picked | null>(null)
  const [checked, setChecked] = useState(false)

  function handleCheck() {
    if (choice === null) return
    setChecked(true)
    onAnswer?.(choice === item.answer, choice === 'unknown' ? null : choice)
  }

  const correct = choice === item.answer
  return (
    <div className="space-y-3">
      <div id={promptId}>
        <Markdown>{item.prompt}</Markdown>
      </div>
      <div role="radiogroup" aria-labelledby={promptId} className="space-y-2">
        {order.map((index) => (
          <label
            key={index}
            className="flex cursor-pointer items-center gap-2 rounded-md border border-slate-200 px-3 py-2 dark:border-slate-700"
          >
            <input
              type="radio"
              name={promptId}
              checked={choice === index}
              disabled={checked}
              onChange={() => setChoice(index)}
            />
            {/* Choices may use Markdown, e.g. `print("Hi")` for code. */}
            <span className={INLINE_CODE}>
              <Markdown inline>{item.choices[index] ?? ''}</Markdown>
            </span>
          </label>
        ))}
        {quiet && (
          // The honest answer when none of the above is known (ADR-0021,
          // amended 2026-11-10): it counts as wrong, so a guess can't place
          // the learner past what they know.
          <label className="flex cursor-pointer items-center gap-2 rounded-md border border-dashed border-slate-300 px-3 py-2 text-slate-600 dark:border-slate-600 dark:text-slate-400">
            <input
              type="radio"
              name={promptId}
              checked={choice === 'unknown'}
              disabled={checked}
              onChange={() => setChoice('unknown')}
            />
            I don't know this
          </label>
        )}
      </div>
      {checked && quiet ? (
        <Recorded />
      ) : checked ? (
        <output className="block space-y-2 rounded-md bg-slate-100 p-3 dark:bg-slate-800">
          <p className="font-medium">
            {correct ? (
              <>
                <span aria-hidden="true">✓ </span>Correct!
              </>
            ) : (
              <>
                <span aria-hidden="true">✗ </span>Not quite. The answer is:{' '}
                <span className={INLINE_CODE}>
                  <Markdown inline>{item.choices[item.answer] ?? ''}</Markdown>
                </span>
              </>
            )}
          </p>
          <Markdown>{item.explanation}</Markdown>
        </output>
      ) : (
        <button
          type="button"
          onClick={handleCheck}
          disabled={choice === null}
          className={BUTTON}
        >
          Check
        </button>
      )}
    </div>
  )
}
