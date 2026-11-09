// Interleaved practice (v1 spec, F5): each practice ladder includes one
// recall question from an earlier topic. Mixing topics makes the learner
// decide which idea applies, instead of knowing it from the page they're on,
// and it spaces the earlier topic out a little (docs/learning-science.md).
import { getTopic } from '../content/content.ts'
import type { Topic, TopicContent } from '../content/types.ts'
import type { Day } from '../days.ts'

/** A question from an earlier topic, with the content it belongs to. */
export type Interleaved = {
  content: TopicContent
  itemId: string
}

/**
 * The earlier topic to borrow a question from: the topic's most recent
 * prerequisite, looking through a checkpoint to the last topic before it.
 * Null for the first topic of a track. Whether the topic can be opened is
 * for the caller to check.
 */
export function earlierTopicFor(
  topic: Topic,
  lookup: (id: string) => Topic | undefined = getTopic,
): Topic | null {
  const seen = new Set<string>([topic.id])
  let current: Topic | undefined = topic
  while (current && current.prerequisites.length > 0) {
    const nextId = current.prerequisites.at(-1) ?? ''
    if (seen.has(nextId)) return null
    seen.add(nextId)
    current = lookup(nextId)
    if (current?.kind === 'topic') return current
  }
  return null
}

/**
 * Which of the earlier topic's recall questions to ask: a different one each
 * day, the same one all day, so a page revisited today asks the same thing.
 */
export function interleavedItem(
  content: TopicContent,
  today: Day,
): string | null {
  const recall = Object.keys(content.recall).sort()
  if (recall.length === 0) return null
  const dayNumber = Math.floor(Date.parse(today) / 86_400_000)
  return recall[dayNumber % recall.length] ?? null
}
