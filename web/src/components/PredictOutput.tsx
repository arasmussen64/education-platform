import { useId, useState } from 'react'
import { normalizeOutput } from '../content/answers.ts'
import type { PredictOutputItem, PredictShellItem } from '../content/types.ts'
import { Markdown } from './Markdown.tsx'
import { Recorded } from './Recorded.tsx'
import { BUTTON, CODE_BOX, TEXT_INPUT } from './styles.ts'

type Props = {
  item: PredictOutputItem | PredictShellItem
  /** Called once, when the learner checks their prediction. */
  onAnswer?: (correct: boolean, prediction: string) => void
  /** True in the placement test (ADR-0021): no word on whether it was right. */
  quiet?: boolean
}

const NOTE = 'text-sm text-slate-600 dark:text-slate-300'

/**
 * The scene of a shell item: the files the command sees, then the command
 * itself at a prompt (ADR-0017). Nothing here runs; the validator proved
 * the output in real bash.
 */
function ShellScene({ item }: { item: PredictShellItem }) {
  const files = Object.entries(item.files)
  return (
    <div className="space-y-2">
      {files.length > 0 && (
        <p className={NOTE}>
          {files.length === 1
            ? 'The folder holds one file:'
            : `The folder holds ${files.length} files:`}
        </p>
      )}
      {files.map(([name, text]) => (
        <figure key={name} className="space-y-1">
          <figcaption className="font-mono text-xs text-slate-600 dark:text-slate-300">
            {name}
          </figcaption>
          <pre className={CODE_BOX}>{text}</pre>
        </figure>
      ))}
      <p className={NOTE}>The command:</p>
      <pre className={CODE_BOX}>
        <span aria-hidden="true">$ </span>
        {item.command}
      </pre>
    </div>
  )
}

/**
 * "What will this print?" Reading and tracing code comes before writing it
 * (docs/learning-science.md), so learners predict first, then compare. The
 * same question works for a Python program and for a shell command.
 */
export function PredictOutput({ item, onAnswer, quiet = false }: Props) {
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
      {item.type === 'predict_shell' ? (
        <ShellScene item={item} />
      ) : (
        <pre className={CODE_BOX}>{item.code}</pre>
      )}
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
                <span aria-hidden="true">✗ </span>Not quite. It prints:
              </>
            )}
          </p>
          {!correct && <pre className={CODE_BOX}>{item.expected_output}</pre>}
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
