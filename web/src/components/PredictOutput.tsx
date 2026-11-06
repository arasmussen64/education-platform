import { useId, useState } from 'react'
import { normalizeOutput } from '../content/answers.ts'
import type { PredictOutputItem } from '../content/types.ts'
import { Markdown } from './Markdown.tsx'
import { BUTTON, TEXT_INPUT } from './styles.ts'

type Props = {
  item: PredictOutputItem
  /** Called once, when the learner checks their prediction. */
  onAnswer?: (correct: boolean, prediction: string) => void
}

/**
 * "What will this print?" Reading and tracing code comes before writing it
 * (docs/learning-science.md), so learners predict first, then compare.
 */
export function PredictOutput({ item, onAnswer }: Props) {
  const fieldId = useId()
  const [prediction, setPrediction] = useState('')
  const [checked, setChecked] = useState(false)
  const correct =
    normalizeOutput(prediction) === normalizeOutput(item.expected_output)
  const lines = item.expected_output.split('\n').length

  function handleCheck() {
    setChecked(true)
    onAnswer?.(correct, prediction)
  }

  return (
    <div className="space-y-3">
      <Markdown>{item.prompt}</Markdown>
      <pre className="overflow-x-auto rounded-md bg-slate-900 p-3 font-mono text-sm text-slate-100">
        {item.code}
      </pre>
      <label htmlFor={fieldId} className="block text-sm font-medium">
        What will it print?
      </label>
      <textarea
        id={fieldId}
        value={prediction}
        onChange={(event) => setPrediction(event.target.value)}
        disabled={checked}
        rows={Math.max(2, lines)}
        spellCheck={false}
        autoComplete="off"
        className={`${TEXT_INPUT} font-mono`}
      />
      {checked ? (
        <output className="block space-y-2 rounded-md bg-slate-100 p-3 dark:bg-slate-800">
          <p className="font-medium">
            {correct ? (
              <>
                <span aria-hidden="true">✓ </span>Correct!
              </>
            ) : (
              <>
                <span aria-hidden="true">✗ </span>Not quite. It prints:
              </>
            )}
          </p>
          {!correct && (
            <pre className="overflow-x-auto rounded-md bg-slate-900 p-3 font-mono text-sm text-slate-100">
              {item.expected_output}
            </pre>
          )}
          <Markdown>{item.explanation}</Markdown>
        </output>
      ) : (
        <button type="button" onClick={handleCheck} className={BUTTON}>
          Check
        </button>
      )}
    </div>
  )
}
