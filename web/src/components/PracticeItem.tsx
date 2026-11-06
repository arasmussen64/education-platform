import type { ReactNode } from 'react'
import type { TopicContent } from '../content/types.ts'
import { STAGES } from '../content/stages.ts'
import { ExerciseView } from './ExerciseView.tsx'
import { McqQuestion } from './McqQuestion.tsx'
import { PredictOutput } from './PredictOutput.tsx'
import { CARD } from './styles.ts'

type Props = {
  /** The item's ID, as listed in topic.yaml. */
  itemId: string
  content: TopicContent
  /** Shown above the heading, e.g. "Practice 2 of 5". */
  position?: string
}

/** The heading and body for an item, whichever kind it is. */
function describe(
  itemId: string,
  content: TopicContent,
): { heading: string; body: ReactNode } | null {
  const recall = content.recall[itemId]
  if (recall?.type === 'mcq') {
    return { heading: 'Quick check', body: <McqQuestion item={recall} /> }
  }
  if (recall?.type === 'predict_output') {
    return {
      heading: 'Predict the output',
      body: <PredictOutput item={recall} />,
    }
  }
  const exercise = content.exercises[itemId]
  if (exercise) {
    return {
      heading: `${STAGES[exercise.stage].label}: ${exercise.title}`,
      body: <ExerciseView exercise={exercise} />,
    }
  }
  return null
}

/**
 * One item of a topic's practice ladder or proof: a recall question or an
 * exercise, in a card with a heading.
 */
export function PracticeItem({ itemId, content, position }: Props) {
  const item = describe(itemId, content)
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
    <section aria-labelledby={headingId} className={CARD}>
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
