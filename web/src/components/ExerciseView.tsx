import { useState } from 'react'
import { STAGES } from '../content/stages.ts'
import type { Exercise, Step } from '../content/types.ts'
import {
  allChecksPassed,
  type CheckOutcome,
  type RunOutcome,
} from '../python/runner.ts'
import { CodeRunner } from './CodeRunner.tsx'
import { Markdown } from './Markdown.tsx'
import { SECONDARY_BUTTON } from './styles.ts'

/** Something the learner did in an exercise, reported so it can be saved. */
export type ExerciseActivity =
  | { kind: 'run'; code: string; outcome: RunOutcome }
  | { kind: 'check'; code: string; outcome: CheckOutcome; hintsUsed: number }
  | { kind: 'hint'; hintsUsed: number }

type ActivityHandler = (activity: ExerciseActivity) => void

type Props = {
  exercise: Exercise
  onActivity?: ActivityHandler
}

/** One exercise: its instructions, the code runner, hints and, once passed, the answer. */
export function ExerciseView({ exercise, onActivity }: Props) {
  if (exercise.stage === 'worked_example') {
    return <WorkedExample exercise={exercise} onActivity={onActivity} />
  }
  return <CodingExercise exercise={exercise} onActivity={onActivity} />
}

/** A full solution to study and run, explained step by step. */
function WorkedExample({
  exercise,
  onActivity,
}: {
  exercise: Exercise
  onActivity?: ActivityHandler
}) {
  return (
    <div className="space-y-3">
      <Markdown>{exercise.prompt}</Markdown>
      <CodeRunner
        initialCode={exercise.solution}
        timeLimitMs={exercise.time_limit_ms}
        onRun={(outcome, code) => onActivity?.({ kind: 'run', code, outcome })}
      />
      <h4 className="font-semibold">How it works</h4>
      <ol className="space-y-3">
        {exercise.steps.map((step) => (
          <li key={`${step.lines} ${step.label}`} className="space-y-1">
            <p>
              <span className="font-medium">{step.label}</span>{' '}
              <span className="text-sm text-slate-500 dark:text-slate-400">
                ({linesLabel(step)})
              </span>
            </p>
            <Markdown>{step.note}</Markdown>
          </li>
        ))}
      </ol>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        Run it, then try changing something and predict what will happen before
        you run it again.
      </p>
    </div>
  )
}

/** "1" -> "line 1", "2-4" -> "lines 2–4". */
function linesLabel(step: Step): string {
  const [first, last] = step.lines.split('-')
  return last ? `lines ${first}–${last}` : `line ${first}`
}

/** Every other stage: write or fix code until the checks pass. */
function CodingExercise({
  exercise,
  onActivity,
}: {
  exercise: Exercise
  onActivity?: ActivityHandler
}) {
  const stage = STAGES[exercise.stage]
  const [passed, setPassed] = useState(false)
  // Kept here, not in <Hints>, because checks report how many were used.
  const [hintsShown, setHintsShown] = useState(0)

  function handleCheck(outcome: CheckOutcome, code: string) {
    if (allChecksPassed(outcome)) setPassed(true)
    onActivity?.({ kind: 'check', code, outcome, hintsUsed: hintsShown })
  }

  function showHint() {
    setHintsShown(hintsShown + 1)
    onActivity?.({ kind: 'hint', hintsUsed: hintsShown + 1 })
  }

  return (
    <div className="space-y-3">
      <Markdown>{exercise.prompt}</Markdown>
      <CodeRunner
        initialCode={exercise.starter}
        tests={exercise.tests}
        hiddenTests={stage.hiddenTests}
        timeLimitMs={exercise.time_limit_ms}
        onRun={(outcome, code) => onActivity?.({ kind: 'run', code, outcome })}
        onCheck={handleCheck}
      />
      {stage.hints && exercise.hints.length > 0 && !passed && (
        <Hints
          hints={exercise.hints}
          shown={hintsShown}
          onShowMore={showHint}
        />
      )}
      {passed && <ReferenceSolution code={exercise.solution} />}
    </div>
  )
}

/** Hints, one at a time, so the learner takes only as much help as they need. */
function Hints({
  hints,
  shown,
  onShowMore,
}: {
  hints: string[]
  shown: number
  onShowMore: () => void
}) {
  return (
    <div className="space-y-2">
      {hints.slice(0, shown).map((hint, index) => (
        <div
          // Hints never change order, so their position is a stable key.
          // oxlint-disable-next-line react/no-array-index-key
          key={index}
          className="rounded-md border-l-4 border-amber-400 bg-amber-50 p-3 dark:bg-amber-950/40"
        >
          <p className="text-sm font-semibold">Hint {index + 1}</p>
          <Markdown>{hint}</Markdown>
        </div>
      ))}
      {shown < hints.length && (
        <button type="button" onClick={onShowMore} className={SECONDARY_BUTTON}>
          {shown === 0 ? 'Show a hint' : 'Show another hint'}
        </button>
      )}
    </div>
  )
}

/** Shown only after a pass (v1 spec, F5), so it can't replace the effort. */
function ReferenceSolution({ code }: { code: string }) {
  return (
    <details className="rounded-md border border-slate-200 dark:border-slate-700">
      <summary className="cursor-pointer px-3 py-2 text-sm font-medium">
        Compare with a reference solution
      </summary>
      <pre className="overflow-x-auto border-t border-slate-200 p-3 font-mono text-sm dark:border-slate-700">
        {code}
      </pre>
    </details>
  )
}
