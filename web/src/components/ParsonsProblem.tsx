import { useId, useState } from 'react'
import type { ParsonsItem } from '../content/types.ts'
import { Markdown } from './Markdown.tsx'
import { Recorded } from './Recorded.tsx'
import { scramble, swap } from './scramble.ts'
import { BUTTON, CODE_BOX } from './styles.ts'

type Props = {
  item: ParsonsItem
  /** Called once, when the learner checks, with the program as they left it. */
  onAnswer?: (correct: boolean, program: string[]) => void
  /** True in the placement test (ADR-0021): no word on whether it was right. */
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

  function handleCheck() {
    setChecked(true)
    onAnswer?.(correct, program)
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
          <Markdown>{item.explanation}</Markdown>
        </output>
      ) : (
        <button
          type="button"
          onClick={handleCheck}
          disabled={program.length === 0}
          className={BUTTON}
        >
          Check
        </button>
      )}
    </div>
  )
}
