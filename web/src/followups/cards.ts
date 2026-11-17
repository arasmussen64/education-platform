import { getTopic } from '../content/content.ts'
import type { TopicContent } from '../content/types.ts'
import { addDays, type Day } from '../days.ts'
import {
  type Attempt,
  type FollowUp,
  type PlannedCard,
  planCards,
} from './followUps.ts'

// Helpers for showing a mistake coming back as a fresh question (ADR-0011),
// shared by the Today page and the guided session (pages/SessionPage.tsx).
// The card itself is FollowUpCard.tsx.

/** A question to ask today, with the follow-ups it answers. */
export type Card = PlannedCard & { key: string }

export const keyOf = (followUp: FollowUp) =>
  `${followUp.topicId}/${followUp.skillId}`

/** Today's questions for these due follow-ups, each with a React key. */
export function dueCards(
  due: FollowUp[],
  contents: Map<string, TopicContent>,
  attempts: Attempt[],
): Card[] {
  return planCards(due, contents, attempts).map((card) => ({
    ...card,
    key: `${card.topicId}/${card.itemId}`,
  }))
}

/** "today", "tomorrow", or "on Mon, Nov 9". */
export function whenDue(day: Day, today: Day): string {
  if (day <= today) return 'today'
  if (day === addDays(today, 1)) return 'tomorrow'
  const [year = 0, month = 1, date = 1] = day.split('-').map(Number)
  const noon = new Date(year, month - 1, date, 12)
  return `on ${noon.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}`
}

/** A skill's description, from its topic's outline (always bundled in). */
export function skillName(followUp: FollowUp) {
  const skill = getTopic(followUp.topicId)?.skills.find(
    (candidate) => candidate.id === followUp.skillId,
  )
  return skill?.description ?? followUp.skillId
}
