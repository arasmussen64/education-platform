import { useId, useState } from 'react'
import type { Confidence } from '../confidence/confidence.ts'
import type { ParsonsItem } from '../content/types.ts'
import { ConfidenceButtons, ConfidenceNote } from './Confidence.tsx'
import { Markdown } from './Markdown.tsx'
import { Recorded } from './Recorded.tsx'
import { scramble, swap } from './scramble.ts'
import { BUTTON, CODE_BOX, SECONDARY_BUTTON } from './styles.ts'

type Props = {
  item: ParsonsItem
  /**
   * Called once, when the learner checks, with the program as they left it,
   * or null for "I don't know this" (placement only). `confidence` is how
   * sure the learner said they were (ADR-0028), or null in the placement
   * test, which doesn't ask.
   */
  onAnswer?: (
    correct: boolean,
    program: string[] | null,
    confidence: Confidence | null,
  ) => void
  /**
   * True in the placement test (ADR-0021): no word on whether it was right,
   * and an "I don't know this" button beside Check.
   */
  quiet?: boolean
}

const SMALL_BUTTON =
  'rounded border border-slate-300 px-2 py-0.5 text-xs hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700 dark:hover:bg-slate-800'

/**
 * A Parsons problem (ADR-0016): the lines of a short program, scrambled,
 * sometimes with a decoy. The learner builds the program with Add, Up,
 * Down and Remove, which work with a keyboard and on a phone, then checks.
 */
export function ParsonsProblem({ item, onAnswer, quiet = false }: Props) {
  const id = useId()
  const [tray, setTray] = useState(() => scramble(item))
  const [program, setProgram] = useState<string[]>([])
  const [checked, setChecked] = useState(false)
  const [confidence, setConfidence] = useState<Confidence | null>(null)
  const correct =
    program.length === item.lines.length &&
    program.every((line, index) => line === item.lines[index])

  function add(line: string) {
    setTray(tray.filter((each) => each !== line))
    setProgram([...program, line])
  }

  function remove(index: number) {
    const line = program[index]
    if (line === undefined) return
    setProgram(program.filter((_, each) => each !== index))
    setTray([...tray, line])
  }

  function move(index: number, by: -1 | 1) {
    const target = index + by
    if (target < 0 || target >= program.length) return
    const next = [...program]
    swap(next, index, target)
    setProgram(next)
  }

  function handleCheck(sure: Confidence | null) {
    setChecked(true)
    setConfidence(sure)
    onAnswer?.(correct, program, sure)
  }

  /** The placement test's way out of guessing: recorded as a wrong answer. */
  function dontKnow() {
    setChecked(true)
    onAnswer?.(false, null, null)
  }

  const decoys = item.distractors.length
  return (
    <div className="space-y-3">
      <Markdown>{item.prompt}</Markdown>
      <div className="grid gap-4 md:grid-cols-2">
        <section aria-labelledby={`${id}-program`} className="space-y-2">
          <h4 id={`${id}-program`} className="text-sm font-medium">
            Your program
          </h4>
          {program.length === 0 ? (
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Add lines from the list, top to bottom. Each line already has its
              indentation.
            </p>
          ) : (
            <ol className="space-y-1 font-mono text-sm">
              {program.map((line, index) => (
                <li
                  key={line}
                  className="flex items-center gap-2 rounded-md bg-slate-100 px-2 py-1 dark:bg-slate-800"
                >
                  <code className="flex-1 whitespace-pre">{line}</code>
                  <button
                    type="button"
                    aria-label={`Move up: ${line.trim()}`}
                    disabled={checked || index === 0}
                    onClick={() => move(index, -1)}
                    className={SMALL_BUTTON}
                  >
                    Up
                  </button>
                  <button
                    type="button"
                    aria-label={`Move down: ${line.trim()}`}
                    disabled={checked || index === program.length - 1}
                    onClick={() => move(index, 1)}
                    className={SMALL_BUTTON}
                  >
                    Down
                  </button>
                  <button
                    type="button"
                    aria-label={`Remove: ${line.trim()}`}
                    disabled={checked}
                    onClick={() => remove(index)}
                    className={SMALL_BUTTON}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ol>
          )}
        </section>
        <section aria-labelledby={`${id}-tray`} className="space-y-2">
          <h4 id={`${id}-tray`} className="text-sm font-medium">
            Lines to use
          </h4>
          {tray.length === 0 ? (
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Every line is in your program.
            </p>
          ) : (
            <ul className="space-y-1 font-mono text-sm">
              {tray.map((line) => (
                <li
                  key={line}
                  className="flex items-center gap-2 rounded-md border border-slate-200 px-2 py-1 dark:border-slate-700"
                >
                  <code className="flex-1 whitespace-pre">{line}</code>
                  <button
                    type="button"
                    aria-label={`Add: ${line.trim()}`}
                    disabled={checked}
                    onClick={() => add(line)}
                    className={SMALL_BUTTON}
                  >
                    Add
                  </button>
                </li>
              ))}
            </ul>
          )}
          {decoys > 0 && (
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {decoys === 1
                ? "One line is a decoy that doesn't belong."
                : `${decoys} lines are decoys that don't belong.`}
            </p>
          )}
        </section>
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
                <span aria-hidden="true">✗ </span>Not quite. The program is:
              </>
            )}
          </p>
          {!correct && <pre className={CODE_BOX}>{item.lines.join('\n')}</pre>}
          <ConfidenceNote confidence={confidence} correct={correct} />
          <Markdown>{item.explanation}</Markdown>
        </output>
      ) : quiet ? (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => handleCheck(null)}
            disabled={program.length === 0}
            className={BUTTON}
          >
            Check
          </button>
          <button type="button" onClick={dontKnow} className={SECONDARY_BUTTON}>
            I don't know this
          </button>
        </div>
      ) : (
        <ConfidenceButtons
          onPick={handleCheck}
          disabled={program.length === 0}
        />
      )}
    </div>
  )
}
