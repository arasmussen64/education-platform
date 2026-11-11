import { type ReactNode, useId, useState } from 'react'
import { STAGES } from '../content/stages.ts'
import type { Exercise, Step } from '../content/types.ts'
import { runsPrivileged } from '../labs/options.ts'
import { type LabResult, parseLabResult } from '../labs/result.ts'
import type { ExerciseActivity } from './ExerciseView.tsx'
import { Hints, ReferenceSolution } from './exerciseParts.tsx'
import { Markdown } from './Markdown.tsx'
import { BUTTON, CODE_BOX, INLINE_CODE, TEXT_INPUT } from './styles.ts'

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
      <LabCommands topicId={topicId} exercise={exercise} />
      {isExample && <Walkthrough exercise={exercise} />}
      <Checks exercise={exercise} result={result} />
      <ResultBox
        lab={`${topicId}/${exercise.id}`}
        rev={exercise.rev}
        checkIds={exercise.checks.map((check) => check.id)}
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

/** How every command of the lab checker is run (tools/labcheck.py). */
const RUN = 'python -m uv run python tools/labcheck.py'

/**
 * A box for a command to copy. The commands are long, so a line wraps
 * rather than scrolling out of sight; copying it still gives one line.
 */
const COMMAND = `${CODE_BOX} break-words whitespace-pre-wrap`

/**
 * How to run the lab: the checker's commands in the order they're needed,
 * with this lab's name filled in, and what the lab's container may touch.
 */
function LabCommands({
  topicId,
  exercise,
}: {
  topicId: string
  exercise: Exercise
}) {
  const lab = `${topicId} ${exercise.id}`
  return (
    <div className={`space-y-3 ${INLINE_CODE}`}>
      <p className={NOTE}>
        This lab runs in a container: a small Linux system of its own that
        Docker runs on your computer. Type these commands in a terminal (on
        Windows, PowerShell or Windows Terminal), in the repository folder, with
        Docker Desktop running.
      </p>
      <ol className="list-decimal space-y-3 pl-6">
        <CommandStep label="Start the lab." command={`${RUN} start ${lab}`}>
          Running this again keeps your work: a lab that is running is left as
          it is, and a lab that stopped when Docker or your computer restarted
          is started again with everything in it.
        </CommandStep>
        <CommandStep
          label="Open a shell inside the lab, and do the work there."
          command={`${RUN} shell ${lab}`}
        >
          Type <code>exit</code> to come back to your own terminal. The lab
          keeps running.
        </CommandStep>
        <CommandStep
          label="Run the checks, as often as you like."
          command={`${RUN} check ${lab}`}
        >
          Copy the result line it prints, the one that starts with{' '}
          <code>{'{"lab"'}</code>, into the box below.
        </CommandStep>
        <CommandStep
          label="Stop the lab when you have finished with it."
          command={`${RUN} stop ${lab}`}
        >
          This removes the container and the work in it, so record your result
          first.
        </CommandStep>
      </ol>
      <p className={NOTE}>
        To throw your work away and begin the lab again, add{' '}
        <code>--fresh</code> to the start command:
      </p>
      <pre className={COMMAND}>{`${RUN} start --fresh ${lab}`}</pre>
      <p className={NOTE}>
        Not sure what is still running? The first of these lists the labs on
        your computer, and the second stops them all:
      </p>
      <pre className={COMMAND}>
        {`${RUN} status\n`}
        {`${RUN} stop --all`}
      </pre>
      <p className={NOTE}>
        {runsPrivileged(exercise) ? (
          <>
            This lab&apos;s container is privileged: so that it can boot like a
            real server, Docker lets it reach the disks and settings of the
            machine Docker runs on, not only its own files. (With Docker
            Desktop, that machine is a small Linux system that Docker Desktop
            keeps running inside your computer.) Inside it, change only what the
            lab asks for. Stop it with the stop command, not from the Docker
            Desktop window: the stop command also cleans up what the lab set up
            on that machine.
          </>
        ) : (
          <>
            This lab&apos;s container is an ordinary one: nothing you do inside
            it can change files on the rest of your computer.
          </>
        )}
      </p>
    </div>
  )
}

/** One step: what it's for, the command to type, and a note about it. */
function CommandStep({
  label,
  command,
  children,
}: {
  label: string
  command: string
  children: ReactNode
}) {
  return (
    <li className="space-y-1">
      <p className="font-medium">{label}</p>
      <pre className={COMMAND}>{command}</pre>
      <p className={NOTE}>{children}</p>
    </li>
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
  checkIds,
  onResult,
}: {
  lab: string
  rev: number
  /** The lab's own checks: a result must name exactly these to count. */
  checkIds: string[]
  onResult: (result: LabResult) => void
}) {
  const fieldId = useId()
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)

  function record() {
    const parsed = parseLabResult(text, lab, rev, checkIds)
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
