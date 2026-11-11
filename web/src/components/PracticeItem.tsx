import { type ReactNode, useState } from 'react'
import { STAGES } from '../content/stages.ts'
import type { TopicContent } from '../content/types.ts'
import { checkCorrect } from '../events/checkGrade.ts'
import {
  checkEventData,
  clip,
  MAX_CODE_CHARS,
  MAX_TEXT_CHARS,
  runEventData,
  traceEventData,
} from '../events/payloads.ts'
import type { EventContext, EventData } from '../events/types.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import { labEventData } from '../labs/result.ts'
import { PLACE_ATTRIBUTE } from '../place/useCurrentPlace.ts'
import { type ItemState, ITEM_STATE_LABELS } from '../progress/itemStates.ts'
import { ReportProblem } from '../reports/ReportProblem.tsx'
import { type ExerciseActivity, ExerciseView } from './ExerciseView.tsx'
import { McqQuestion } from './McqQuestion.tsx'
import { ParsonsProblem } from './ParsonsProblem.tsx'
import { PredictOutput } from './PredictOutput.tsx'
import { CARD } from './styles.ts'
import { useAttemptTimer } from './useAttemptTimer.ts'

type Props = {
  /** The item's ID, as listed in topic.yaml. */
  itemId: string
  content: TopicContent
  /**
   * Whether this is practice, a proof check, a review or the placement
   * test; saved with each answer.
   */
  context: Extract<EventContext, 'practice' | 'prove' | 'review' | 'placement'>
  /** Saved in the data of every event this item records, e.g. a placement run's id. */
  eventData?: EventData
  /** Shown above the heading, e.g. "Practice 2 of 5". */
  position?: string
  /** Where the learner stands on it, from their saved answers, if known. */
  status?: ItemState
  /**
   * True for an item the learner had already got right before this visit:
   * its body stays out of the way until they ask for it, so a long topic
   * shows what's left to do.
   */
  collapsed?: boolean
  /** A place on the page the outline can point at: the card's id. */
  placeId?: string
  /** Called after each Check of an exercise, with whether every test passed. */
  onCheck?: (passed: boolean) => void
  /**
   * Called after each graded attempt, an answer or a Check, with whether it
   * was correct. Review sessions rate themselves from these (ADR-0009).
   */
  onGraded?: (correct: boolean) => void
}

type Handlers = {
  onAnswer: (correct: boolean, data: EventData) => void
  onActivity: (activity: ExerciseActivity) => void
  allowHints: boolean
  allowTutor: boolean
  /** Take answers without saying whether they were right (the placement test). */
  quiet: boolean
}

/**
 * The mark an answer's data carries when the learner chose "I don't know
 * this" in the placement test (ADR-0021, amended 2026-11-10); nothing when
 * they answered.
 */
function unknownIf(dontKnow: boolean): EventData {
  return dontKnow ? { dont_know: true } : {}
}

/** The heading and body for an item, whichever kind it is. */
function describe(
  itemId: string,
  content: TopicContent,
  { onAnswer, onActivity, allowHints, allowTutor, quiet }: Handlers,
): { heading: string; body: ReactNode } | null {
  const recall = content.recall[itemId]
  if (recall?.type === 'mcq') {
    return {
      heading: 'Quick check',
      body: (
        <McqQuestion
          item={recall}
          quiet={quiet}
          onAnswer={(correct, choice) =>
            onAnswer(correct, {
              choice,
              choice_text:
                choice === null ? null : (recall.choices[choice] ?? null),
              ...unknownIf(choice === null),
            })
          }
        />
      ),
    }
  }
  if (recall?.type === 'predict_output' || recall?.type === 'predict_shell') {
    return {
      heading: 'Predict the output',
      body: (
        <PredictOutput
          item={recall}
          packages={content.topic.packages}
          quiet={quiet}
          onAnswer={(correct, prediction) =>
            onAnswer(correct, {
              prediction:
                prediction === null ? null : clip(prediction, MAX_TEXT_CHARS),
              ...unknownIf(prediction === null),
            })
          }
        />
      ),
    }
  }
  if (recall?.type === 'parsons') {
    return {
      heading: 'Put the lines in order',
      body: (
        <ParsonsProblem
          item={recall}
          quiet={quiet}
          onAnswer={(correct, program) =>
            onAnswer(correct, {
              program:
                program === null
                  ? null
                  : clip(program.join('\n'), MAX_CODE_CHARS),
              ...unknownIf(program === null),
            })
          }
        />
      ),
    }
  }
  const exercise = content.exercises[itemId]
  if (exercise) {
    return {
      heading: `${STAGES[exercise.stage].label}: ${exercise.title}`,
      body: (
        <ExerciseView
          exercise={exercise}
          onActivity={onActivity}
          allowHints={allowHints}
          allowTutor={allowTutor}
          topicId={content.topic.id}
        />
      ),
    }
  }
  return null
}

/**
 * One item of a topic's practice ladder or proof: a recall question or an
 * exercise, in a card with a heading. Saves what the learner does with it.
 */
export function PracticeItem({
  itemId,
  content,
  context,
  eventData,
  position,
  status,
  collapsed = false,
  placeId,
  onCheck,
  onGraded,
}: Props) {
  const recordEvent = useRecordEvent()
  // Every event this item records carries the extra data, if any.
  const record: typeof recordEvent = (event) =>
    recordEvent(
      eventData ? { ...event, data: { ...eventData, ...event.data } } : event,
    )
  const timer = useAttemptTimer()
  const [shown, setShown] = useState(false)
  // True after a Check that couldn't run, until the next one that does.
  const [checkNotRun, setCheckNotRun] = useState(false)
  const rev = (content.recall[itemId] ?? content.exercises[itemId])?.rev
  const about = {
    topic_id: content.topic.id,
    item_id: itemId,
    item_rev: rev,
    context,
  }

  const item = describe(itemId, content, {
    // No hints in reviews, which stand in for the tutor, which is off there;
    // none in the placement test either, which measures.
    allowHints: context !== 'review' && context !== 'placement',
    // The placement test takes answers without a word on whether they were
    // right (ADR-0021).
    quiet: context === 'placement',
    // The tutor is on in practice only (ADR-0015): never in proof checks
    // or reviews.
    allowTutor: context === 'practice',
    onAnswer(correct, data) {
      record({
        ...about,
        type: 'answer',
        correct,
        duration_ms: timer.lap(),
        data,
      })
      onGraded?.(correct)
    },
    onActivity(activity) {
      if (activity.kind === 'hint') {
        record({
          ...about,
          type: 'hint',
          hints_used: activity.hintsUsed,
          data: { level: activity.hintsUsed, source: 'author' },
        })
      } else if (activity.kind === 'tutor') {
        const { given } = activity
        record({
          ...about,
          type: 'hint',
          hints_used: activity.hintsUsed,
          data: {
            level: given.count,
            source: 'tutor',
            rung: given.hint.level,
            replaced: given.hint.replaced,
            question: given.question,
            ai_call_id: given.aiCallId,
            model: given.model,
          },
        })
      } else if (activity.kind === 'run') {
        record({
          ...about,
          type: 'code_run',
          data: runEventData(activity.code, activity.outcome),
        })
      } else if (activity.kind === 'trace') {
        // Stepping through is a run that was watched (ADR-0022).
        record({
          ...about,
          type: 'code_run',
          data: traceEventData(activity.code, activity.outcome),
        })
      } else if (activity.kind === 'lab') {
        // A lab's result is a Check of the learner's work, like a Python
        // Check, so it's the same event (ADR-0018) and counts the same way.
        const passed = activity.result.passed === activity.result.total
        record({
          ...about,
          type: 'code_check',
          correct: passed,
          duration_ms: timer.lap(),
          hints_used: activity.hintsUsed,
          data: labEventData(activity.result),
        })
        onCheck?.(passed)
        onGraded?.(passed)
      } else {
        // Undefined when the Check couldn't run (see checkGrade.ts).
        const correct = checkCorrect(activity.outcome)
        const ran = correct !== undefined
        record({
          ...about,
          type: 'code_check',
          correct,
          // A Check that couldn't run isn't an attempt, so the time so far
          // carries on to the next one.
          duration_ms: ran ? timer.lap() : null,
          hints_used: activity.hintsUsed,
          data: checkEventData(activity.code, activity.outcome),
        })
        setCheckNotRun(!ran)
        // It says nothing about the learner, so a review doesn't rate it and
        // a checkpoint doesn't count it as a failed try.
        if (ran) {
          onCheck?.(correct)
          onGraded?.(correct)
        }
      }
    },
  })

  if (!item) {
    // The validator makes sure every listed item exists, so this only
    // happens while a draft is being written.
    return (
      <p className={CARD}>
        Missing practice item <code>{itemId}</code>.
      </p>
    )
  }

  const headingId = `item-${itemId}`
  return (
    // The attempt timer starts at the first focus or click inside the item.
    // These handlers only time; they aren't controls. Keyboard users start
    // the timer by focusing something inside, mouse users by clicking (which
    // doesn't always move focus, e.g. in Safari).
    // oxlint-disable-next-line jsx-a11y/no-noninteractive-element-interactions
    <section
      aria-labelledby={headingId}
      id={placeId}
      {...(placeId ? { [PLACE_ATTRIBUTE]: placeId } : {})}
      className={CARD}
      onFocus={timer.start}
      onPointerDown={timer.start}
    >
      {position && (
        <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400">
          {position}
          {status && ` · ${ITEM_STATE_LABELS[status]}`}
        </p>
      )}
      <h3 id={headingId} className="text-lg font-semibold">
        {item.heading}
      </h3>
      {collapsed && !shown ? (
        <p className="text-sm text-slate-600 dark:text-slate-400">
          You got this one right already.{' '}
          <button
            type="button"
            onClick={() => setShown(true)}
            className="underline"
          >
            Show it again
          </button>
        </p>
      ) : (
        item.body
      )}
      {/* Only when needed, so cards keep their spacing. The code runner has
          already shown (and announced) what went wrong; this says what it
          means for the learner. */}
      {checkNotRun && (
        <output className="block text-sm text-slate-600 dark:text-slate-400">
          That Check couldn't run, so it doesn't count for or against you. Press
          Check to try again.
        </output>
      )}
      <ReportProblem
        about={{ topicId: content.topic.id, itemId, itemRev: rev }}
      />
    </section>
  )
}
