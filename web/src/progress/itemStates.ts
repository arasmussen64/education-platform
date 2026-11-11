// Where the learner stands on each practice item, from their graded
// attempts: done once any answer or Check of it was correct, tried if there
// were only wrong ones. Like the rest of progress, nothing is stored; it's
// worked out from the event log, so a learner can't tick an item off
// without getting it right (ADR-0002).
import type { Attempt } from '../followups/followUps.ts'

export type ItemState = 'done' | 'tried'

/** The key an item's state is filed under: its topic and its ID. */
export function itemKey(topicId: string, itemId: string): string {
  return `${topicId}/${itemId}`
}

/**
 * Every attempted item's state, by itemKey. Graded explanations and review
 * sessions aren't items, so they're left out. The order of the attempts
 * doesn't matter: one correct attempt makes an item done for good.
 */
export function itemStates(attempts: Attempt[]): Map<string, ItemState> {
  const states = new Map<string, ItemState>()
  for (const attempt of attempts) {
    if (attempt.type !== 'answer' && attempt.type !== 'code_check') continue
    // The placement test asks review questions of topics the learner may not
    // have opened yet. Its answers say where to start, not that a practice
    // question is done (ADR-0021), so they leave the ladder as it was.
    if (attempt.context === 'placement') continue
    const key = itemKey(attempt.topic_id, attempt.item_id)
    if (attempt.correct) states.set(key, 'done')
    else if (!states.has(key)) states.set(key, 'tried')
  }
  return states
}

/** How an item's state reads on the page. */
export const ITEM_STATE_LABELS: Record<ItemState, string> = {
  done: 'Done ✓',
  tried: 'Tried, not right yet',
}
