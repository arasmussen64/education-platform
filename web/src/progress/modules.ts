import type { Module } from '../content/types.ts'
import type { TopicProgress } from './progress.ts'

// How far through a module the learner is. Progress feels fastest near the
// end of a goal (the "goal gradient"), so the Today page and the map say
// "6 of 8 topics proven in Module 2" rather than a percentage of the whole
// track, which barely moves. And the start of a new module is a natural
// "fresh start", a moment people are more willing to begin again, so the
// Today page says so in a sentence. No points, badges or confetti.

/** A module's topics and its checkpoint, in order. Its capstone is not. */
export function moduleTopicIds(module: Module): string[] {
  return [...module.topics, module.checkpoint]
}

export type ModuleCount = {
  /** Topics proven: Learned, or Passed for a checkpoint, in any later state. */
  proven: number
  /** Topics that can be opened now; the others are still being written. */
  open: number
  /** Every topic in the module, written or not. */
  total: number
}

/** How many of a module's topics are proven, of those that can be opened. */
export function countModule(
  module: Module,
  progress: Map<string, TopicProgress>,
  canOpen: (topicId: string) => boolean,
): ModuleCount {
  const ids = moduleTopicIds(module)
  return {
    proven: ids.filter((id) => progress.get(id)?.learnedAt).length,
    open: ids.filter(canOpen).length,
    total: ids.length,
  }
}

/**
 * One sentence on where the learner stands in the module the next topic
 * belongs to: a fresh start when nothing in it is proven yet, otherwise the
 * count and how many are left.
 */
export function describeModule(
  number: number,
  module: Module,
  { proven, open, total }: ModuleCount,
): string {
  const name = `Module ${number}, ${module.title}`
  const unwritten =
    total > open
      ? ` ${total - open} more ${total - open === 1 ? 'is' : 'are'} still being written.`
      : ''
  if (proven === 0) {
    return `A fresh start: ${name}, begins here, with ${open} ${open === 1 ? 'topic' : 'topics'}.${unwritten}`
  }
  const left = open - proven
  const tail = left > 0 ? `: ${left} to go.` : '.'
  return `${proven} of ${open} topics proven in ${name}${tail}${unwritten}`
}
