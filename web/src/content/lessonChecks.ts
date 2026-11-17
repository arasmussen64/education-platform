import type { TopicContent } from './types.ts'

/**
 * The topic's practice items that the lesson doesn't already ask. A question
 * placed in the lesson with <Check item="…" /> (ADR-0026) is still one of
 * the topic's practice items, listed in topic.yaml's `practice:` and counted
 * like any other, but the page shows it once, in the lesson, so the practice
 * ladder leaves it out.
 */
export function practiceOutsideLesson(content: TopicContent): string[] {
  const placed = new Set(content.lessonChecks ?? [])
  return content.topic.practice.filter((itemId) => !placed.has(itemId))
}
