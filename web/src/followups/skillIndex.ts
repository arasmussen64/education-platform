// The skill index: what follow-ups need to know about every question and
// exercise (ItemFacts in followUps.ts), gathered from content/ while the app
// is built (vite.config.ts, "skill index"). With it, the app can work out
// the open follow-ups, and so whether a topic is Mastered (ADR-0011),
// without downloading whole topics. Only the topics whose questions are on
// the page load in full.
import { getTopic, isOpen } from '../content/content.ts'
import type { ItemsOf, TopicItems } from './followUps.ts'

/** Every topic's questions and exercises, by topic ID and then item ID. */
export type SkillIndex = Readonly<Record<string, TopicItems>>

let loading: Promise<SkillIndex> | null = null

/**
 * The skill index. It downloads the first time, as a file of its own, so a
 * visitor who never signs in never fetches it; after that it's shared. A
 * failed download is tried again on the next call.
 */
export function loadSkillIndex(): Promise<SkillIndex> {
  loading ??= import('virtual:skill-index').then(
    (module) => module.default as SkillIndex,
    (error: unknown) => {
      loading = null
      throw error
    },
  )
  return loading
}

/**
 * The index's questions and exercises, in the topics that can be opened.
 * A topic that can't be opened brings nothing back, because its questions
 * couldn't be asked (as before the index, when only open topics loaded).
 */
export function openItemsOf(index: SkillIndex): ItemsOf {
  return (topicId) => {
    const topic = getTopic(topicId)
    if (!topic || !isOpen(topic) || !Object.hasOwn(index, topicId)) {
      return undefined
    }
    return index[topicId]
  }
}
