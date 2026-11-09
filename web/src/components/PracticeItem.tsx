import type { ReactNode } from 'react'
import { STAGES } from '../content/stages.ts'
import type { TopicContent } from '../content/types.ts'
import {
  checkEventData,
  clip,
  MAX_TEXT_CHARS,
  runEventData,
} from '../events/payloads.ts'
import type { EventContext, EventData } from '../events/types.ts'
import { useRecordEvent } from '../events/useEvents.ts'
import { allChecksPassed } from '../python/runner.ts'
import { type ExerciseActivity, ExerciseView } from './ExerciseView.tsx'
import { McqQuestion } from './McqQuestion.tsx'
import { PredictOutput } from './PredictOutput.tsx'
import { CARD } from './styles.ts'
import { useAttemptTimer } from './useAttemptTimer.ts'

type Props = {
  /** The item's ID, as listed in topic.yaml. */
  itemId: string
  content: TopicContent
  /** Whether this is practice or a proof check; saved with each answer. */
  context: Extract<EventContext, 'practice' | 'prove' | 'review'>
  /** Shown above the heading, e.g. "Practice 2 of 5". */
  position?: string
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
}

/** The heading and body for an item, whichever kind it is. */
function describe(
  itemId: string,
  content: TopicContent,
  { onAnswer, onActivity, allowHints, allowTutor }: Handlers,
): { heading: string; body: ReactNode } | null {
  const recall = content.recall[itemId]
  if (recall?.type === 'mcq') {
    return {
      heading: 'Quick check',
      body: (
        <McqQuestion
          item={recall}
          onAnswer={(correct, choice) =>
            onAnswer(correct, {
              choice,
              choice_text: recall.choices[choice] ?? null,
            })
          }
        />
      ),
    }
  }
  if (recall?.type === 'predict_output') {
    return {
      heading: 'Predict the output',
      body: (
        <PredictOutput
          item={recall}
          onAnswer={(correct, prediction) =>
            onAnswer(correct, {
              prediction: clip(prediction, MAX_TEXT_CHARS),
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
  position,
  onCheck,
  onGraded,
}: Props) {
  const record = useRecordEvent()
  const timer = useAttemptTimer()
  const rev = (content.recall[itemId] ?? content.exercises[itemId])?.rev
  const about = {
    topic_id: content.topic.id,
    item_id: itemId,
    item_rev: rev,
    context,
  }

  const item = describe(itemId, content, {
    // No hints in reviews: they stand in for the tutor, which is off there.
    allowHints: context !== 'review',
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
      } else {
        const passed = allChecksPassed(activity.outcome)
        record({
          ...about,
          type: 'code_check',
          correct: passed,
          duration_ms: timer.lap(),
          hints_used: activity.hintsUsed,
          data: checkEventData(activity.code, activity.outcome),
        })
        onCheck?.(passed)
        onGraded?.(passed)
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
      className={CARD}
      onFocus={timer.start}
      onPointerDown={timer.start}
    >
      {position && (
        <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase dark:text-slate-400">
          {position}
        </p>
      )}
      <h3 id={headingId} className="text-lg font-semibold">
        {item.heading}
      </h3>
      {item.body}
    </section>
  )
}
