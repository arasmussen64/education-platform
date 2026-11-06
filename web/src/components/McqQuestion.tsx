import { useId, useState } from 'react'
import type { McqItem } from '../content/types.ts'
import { Markdown } from './Markdown.tsx'
import { BUTTON, INLINE_CODE } from './styles.ts'

type Props = {
  item: McqItem
  /** Called once, when the learner checks their answer. */
  onAnswer?: (correct: boolean, choice: number) => void
}

/**
 * A multiple-choice question. The learner commits to an answer before seeing
 * whether it's right and why (retrieval practice).
 */
export function McqQuestion({ item, onAnswer }: Props) {
  const promptId = useId()
  const [choice, setChoice] = useState<number | null>(null)
  const [checked, setChecked] = useState(false)

  function handleCheck() {
    if (choice === null) return
    setChecked(true)
    onAnswer?.(choice === item.answer, choice)
  }

  const correct = choice === item.answer
  return (
    <div className="space-y-3">
      <div id={promptId}>
        <Markdown>{item.prompt}</Markdown>
      </div>
      <div role="radiogroup" aria-labelledby={promptId} className="space-y-2">
        {item.choices.map((text, index) => (
          <label
            key={text}
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
              <Markdown inline>{text}</Markdown>
            </span>
          </label>
        ))}
      </div>
      {checked ? (
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
