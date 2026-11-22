// How well each learned topic is remembered right now, and where it will be
// tomorrow (ADR-0030), for the Today page's "Your memory" list.
//
// The review scheduler already predicts the chance of recalling each topic
// (reviews/fsrs.ts), and the map shows it. Here it's put where the learner
// decides whether to study today: the weakest topics first, with what a day
// of waiting costs. People work harder to keep something than to gain it
// (loss aversion; Kahneman & Tversky, 1979), which is why a daily streak
// pulls, but a streak's loss is invented. This one is real: the number is
// the scheduler's own estimate, and a review does bring it back.
import type { Topic } from '../content/types.ts'
import type { TopicProgress } from '../progress/progress.ts'
import { addDays, retrievabilityAt } from './fsrs.ts'

/** One learned topic's memory. */
export type MemoryRow = {
  topic: Topic
  /** The chance it's remembered now, as a whole percentage. */
  percent: number
  /** The same a day from now, if it isn't reviewed. */
  tomorrow: number
  /** Whether its review is due. */
  due: boolean
  /** When its next review is due, in ISO format. */
  dueAt: string
}

/**
 * Every topic with a review card, weakest memory first. `topics` are the
 * ones that can be opened; checkpoints have no card, so they're left out.
 */
export function memoryRows(
  topics: Topic[],
  progress: Map<string, TopicProgress>,
  now: string,
): MemoryRow[] {
  const tomorrow = addDays(now, 1)
  const rows: MemoryRow[] = []
  for (const topic of topics) {
    const card = progress.get(topic.id)?.card
    if (!card) continue
    rows.push({
      topic,
      percent: Math.round(100 * retrievabilityAt(card, now)),
      tomorrow: Math.round(100 * retrievabilityAt(card, tomorrow)),
      due: card.due <= now,
      dueAt: card.due,
    })
  }
  // Weakest first; of two alike, the one due sooner.
  return rows.sort(
    (a, b) => a.percent - b.percent || a.dueAt.localeCompare(b.dueAt),
  )
}

/** How many topics the list shows before "and N more". */
export const MEMORY_ROWS_SHOWN = 5

/**
 * "at 84% and dropping: 82% by tomorrow", or "at 84%, and holding" when a
 * day changes nothing a whole percentage can show.
 */
export function describeDrop(row: MemoryRow): string {
  return row.tomorrow < row.percent
    ? `at ${row.percent}% and dropping: ${row.tomorrow}% by tomorrow`
    : `at ${row.percent}%, and holding for now`
}

/** "3 of your 12 learned topics have faded enough to need a review." */
export function memorySummary(rows: MemoryRow[]): string {
  const due = rows.filter((row) => row.due).length
  const all = `${rows.length} learned ${rows.length === 1 ? 'topic' : 'topics'}`
  if (due === 0) {
    return `None of your ${all} needs a review yet. Weakest first.`
  }
  return `${due} of your ${all} ${due === 1 ? 'has' : 'have'} faded enough to need a review. Weakest first.`
}
