import { useId, useState } from 'react'
import { STAGES } from '../content/stages.ts'
import type { Exercise, Step } from '../content/types.ts'
import { type LabResult, parseLabResult } from '../labs/result.ts'
import type { ExerciseActivity } from './ExerciseView.tsx'
import { Hints, ReferenceSolution } from './exerciseParts.tsx'
import { Markdown } from './Markdown.tsx'
import { BUTTON, CODE_BOX, TEXT_INPUT } from './styles.ts'

type Props = {
  exercise: Exercise
  /** Names the lab for the checker: labs are "topic/exercise". */
  topicId: string
  onActivity?: (activity: ExerciseActivity) => void
  allowHints: boolean
}

const NOTE = 'text-sm text-slate-600 dark:text-slate-300'

/**
 * A lab (ADR-0018): an exercise that runs in a container on the learner's
 * machine. The page can't run it, so it says how to, lists what the checker
 * looks for, and takes the checker's result to record it.
 */
export function LabExercise({
  exercise,
  topicId,
  onActivity,
  allowHints,
}: Props) {
  const stage = STAGES[exercise.stage]
  const isExample = exercise.stage === 'worked_example'
  const [hintsShown, setHintsShown] = useState(0)
  const [result, setResult] = useState<LabResult | null>(null)
  const passed = result !== null && result.passed === result.total

  function showHint() {
    setHintsShown(hintsShown + 1)
    onActivity?.({ kind: 'hint', hintsUsed: hintsShown + 1 })
  }

  function handleResult(recorded: LabResult) {
    setResult(recorded)
    onActivity?.({ kind: 'lab', result: recorded, hintsUsed: hintsShown })
  }

  return (
    <div className="space-y-3">
      <Markdown>{exercise.prompt}</Markdown>
      <LabCommands topicId={topicId} exerciseId={exercise.id} />
      {isExample && <Walkthrough exercise={exercise} />}
      <Checks exercise={exercise} result={result} />
      <ResultBox
        lab={`${topicId}/${exercise.id}`}
        rev={exercise.rev}
        onResult={handleResult}
      />
      {stage.hints && allowHints && !passed && exercise.hints.length > 0 && (
        <Hints
          hints={exercise.hints}
          shown={hintsShown}
          onShowMore={showHint}
        />
      )}
      {passed && !isExample && <ReferenceSolution code={exercise.solution} />}
    </div>
  )
}

/** The three commands, with this lab's name filled in. */
function LabCommands({
  topicId,
  exerciseId,
}: {
  topicId: string
  exerciseId: string
}) {
  const run = `python -m uv run python tools/labcheck.py`
  return (
    <div className="space-y-2">
      <p className={NOTE}>
        This lab runs in a container on your own computer. In a terminal, in the
        repository folder, with Docker Desktop running:
      </p>
      <pre className={CODE_BOX}>
        {`${run} start ${topicId} ${exerciseId}\n`}
        {`# It prints the command that opens a shell inside the lab. Do the work there, then:\n`}
        {`${run} check ${topicId} ${exerciseId}\n`}
        {`# Copy the result line it prints into the box below. When you're done:\n`}
        {`${run} stop ${topicId} ${exerciseId}`}
      </pre>
    </div>
  )
}

/** A worked-example lab: the walkthrough to follow, explained step by step. */
function Walkthrough({ exercise }: { exercise: Exercise }) {
  return (
    <div className="space-y-3">
      <h4 className="font-semibold">The walkthrough</h4>
      <pre className={CODE_BOX}>{exercise.solution}</pre>
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
      <p className={NOTE}>
        Type each command yourself in the lab's shell and watch what it does,
        then run the checks.
      </p>
    </div>
  )
}

/** "1" -> "line 1", "2-4" -> "lines 2–4". */
function linesLabel(step: Step): string {
  const [first, last] = step.lines.split('-')
  return last ? `lines ${first}–${last}` : `line ${first}`
}

/** What the checker looks for, with ticks once a result is in. */
function Checks({
  exercise,
  result,
}: {
  exercise: Exercise
  result: LabResult | null
}) {
  const headingId = useId()
  const outcomes = new Map(result?.checks.map((c) => [c.id, c.passed]) ?? [])
  return (
    <section aria-labelledby={headingId} className="space-y-1">
      <h4 id={headingId} className="font-semibold">
        What the checker looks for
      </h4>
      <ul className="space-y-1">
        {exercise.checks.map((check) => {
          const outcome = outcomes.get(check.id)
          return (
            <li key={check.id} className="flex gap-2">
              <span aria-hidden="true" className="w-4 shrink-0">
                {outcome === undefined ? '○' : outcome ? '✓' : '✗'}
              </span>
              <span>
                {check.description}
                {outcome !== undefined && (
                  <span className="sr-only">
                    {outcome ? ' (passed)' : ' (failed)'}
                  </span>
                )}
              </span>
            </li>
          )
        })}
      </ul>
      {result && (
        <p className="font-medium">
          {result.passed === result.total
            ? 'All checks passed.'
            : `${result.passed} of ${result.total} checks passed.`}
        </p>
      )}
    </section>
  )
}

/** Where the checker's printed result goes. */
function ResultBox({
  lab,
  rev,
  onResult,
}: {
  lab: string
  rev: number
  onResult: (result: LabResult) => void
}) {
  const fieldId = useId()
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)

  function record() {
    const parsed = parseLabResult(text, lab, rev)
    if ('error' in parsed) {
      setError(parsed.error)
      return
    }
    setError(null)
    setText('')
    onResult(parsed.result)
  }

  return (
    <div className="space-y-2">
      <label htmlFor={fieldId} className="block text-sm font-medium">
        The checker's result
      </label>
      <textarea
        id={fieldId}
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={2}
        spellCheck={false}
        autoComplete="off"
        placeholder='{"lab":"…","rev":1,…}'
        className={`${TEXT_INPUT} font-mono`}
      />
      <button
        type="button"
        onClick={record}
        disabled={text.trim() === ''}
        className={BUTTON}
      >
        Record result
      </button>
      {error && (
        <p role="alert" className="text-sm text-red-700 dark:text-red-300">
          {error}
        </p>
      )}
    </div>
  )
}
