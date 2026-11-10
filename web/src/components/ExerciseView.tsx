import { useState } from 'react'
import { getTopic } from '../content/content.ts'
import { STAGES } from '../content/stages.ts'
import type { Exercise, Step } from '../content/types.ts'
import type { LabResult } from '../labs/result.ts'
import {
  allChecksPassed,
  type CheckOutcome,
  type RunOutcome,
  type TraceOutcome,
} from '../python/runner.ts'
import { TutorBox, type TutorHintGiven } from '../tutor/TutorBox.tsx'
import { CodeRunner } from './CodeRunner.tsx'
import { Hints, ReferenceSolution } from './exerciseParts.tsx'
import { LabExercise } from './LabExercise.tsx'
import { Markdown } from './Markdown.tsx'

/** Something the learner did in an exercise, reported so it can be saved. */
export type ExerciseActivity =
  | { kind: 'run'; code: string; outcome: RunOutcome }
  /** The learner stepped through the code (ADR-0022). */
  | { kind: 'trace'; code: string; outcome: TraceOutcome }
  | { kind: 'check'; code: string; outcome: CheckOutcome; hintsUsed: number }
  /** A written hint was opened. `hintsUsed` counts written and tutor hints. */
  | { kind: 'hint'; hintsUsed: number }
  /** The tutor gave a hint (ADR-0015). */
  | { kind: 'tutor'; hintsUsed: number; given: TutorHintGiven }
  /** The learner recorded a lab's result from the checker (ADR-0018). */
  | { kind: 'lab'; result: LabResult; hintsUsed: number }

type ActivityHandler = (activity: ExerciseActivity) => void

type Props = {
  exercise: Exercise
  onActivity?: ActivityHandler
  /** False in reviews: hints stand in for the tutor, which is off there. */
  allowHints?: boolean
  /** True in practice only: the tutor is off in proof checks and reviews. */
  allowTutor?: boolean
  /** Where the exercise lives, for the tutor's log and the lab's name. */
  topicId?: string
}

/** One exercise: its instructions, the code runner, hints and, once passed, the answer. */
export function ExerciseView({
  exercise,
  onActivity,
  allowHints = true,
  allowTutor = false,
  topicId = '',
}: Props) {
  // The packages the topic's code imports, loaded before it runs (ADR-0023).
  const packages = getTopic(topicId)?.packages ?? []
  if (exercise.runtime === 'lab') {
    // The tutor is off in labs for now: it has no code to look at (ADR-0018).
    return (
      <LabExercise
        exercise={exercise}
        topicId={topicId}
        onActivity={onActivity}
        allowHints={allowHints}
      />
    )
  }
  if (exercise.stage === 'worked_example') {
    return (
      <WorkedExample
        exercise={exercise}
        onActivity={onActivity}
        packages={packages}
      />
    )
  }
  return (
    <CodingExercise
      exercise={exercise}
      onActivity={onActivity}
      allowHints={allowHints}
      allowTutor={allowTutor}
      topicId={topicId}
      packages={packages}
    />
  )
}

/** A full solution to study and run, explained step by step. */
function WorkedExample({
  exercise,
  onActivity,
  packages,
}: {
  exercise: Exercise
  onActivity?: ActivityHandler
  packages: string[]
}) {
  return (
    <div className="space-y-3">
      <Markdown>{exercise.prompt}</Markdown>
      <CodeRunner
        initialCode={exercise.solution}
        timeLimitMs={exercise.time_limit_ms}
        packages={packages}
        onRun={(outcome, code) => onActivity?.({ kind: 'run', code, outcome })}
        onTrace={(outcome, code) =>
          onActivity?.({ kind: 'trace', code, outcome })
        }
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
  allowHints,
  allowTutor,
  topicId,
  packages,
}: {
  exercise: Exercise
  onActivity?: ActivityHandler
  allowHints: boolean
  allowTutor: boolean
  topicId: string
  packages: string[]
}) {
  const stage = STAGES[exercise.stage]
  const [passed, setPassed] = useState(false)
  // Kept here, not in <Hints> or <TutorBox>, because checks report how many
  // hints of both kinds were used.
  const [hintsShown, setHintsShown] = useState(0)
  const [tutorHints, setTutorHints] = useState(0)
  // What the tutor sees: the code as it is now, and the latest Check.
  const [code, setCode] = useState(exercise.starter)
  const [lastCheck, setLastCheck] = useState<CheckOutcome | null>(null)
  const hintsUsed = hintsShown + tutorHints

  function handleCheck(outcome: CheckOutcome, checked: string) {
    if (allChecksPassed(outcome)) setPassed(true)
    setLastCheck(outcome)
    onActivity?.({ kind: 'check', code: checked, outcome, hintsUsed })
  }

  function showHint() {
    setHintsShown(hintsShown + 1)
    onActivity?.({ kind: 'hint', hintsUsed: hintsUsed + 1 })
  }

  function handleTutorHint(given: TutorHintGiven) {
    setTutorHints(given.count)
    onActivity?.({ kind: 'tutor', hintsUsed: hintsShown + given.count, given })
  }

  const helpOffered = stage.hints && !passed
  return (
    <div className="space-y-3">
      <Markdown>{exercise.prompt}</Markdown>
      <CodeRunner
        initialCode={exercise.starter}
        tests={exercise.tests}
        packages={packages}
        hiddenTests={stage.hiddenTests}
        timeLimitMs={exercise.time_limit_ms}
        onRun={(outcome, ran) =>
          onActivity?.({ kind: 'run', code: ran, outcome })
        }
        onTrace={(outcome, ran) =>
          onActivity?.({ kind: 'trace', code: ran, outcome })
        }
        onCheck={handleCheck}
        onCodeChange={setCode}
      />
      {helpOffered && allowHints && exercise.hints.length > 0 && (
        <Hints
          hints={exercise.hints}
          shown={hintsShown}
          onShowMore={showHint}
        />
      )}
      {helpOffered && allowTutor && (
        <TutorBox
          topicId={topicId}
          itemId={exercise.id}
          exercise={exercise}
          code={code}
          check={lastCheck}
          onHint={handleTutorHint}
        />
      )}
      {passed && <ReferenceSolution code={exercise.solution} />}
    </div>
  )
}
