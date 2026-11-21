// What proving a topic changed (ADR-0030), for the moment the topic page
// shows when the last proof passes: the topics it opened, and how far it
// moved the module along. People judge an experience by its best moment and
// by how it ended (the peak-end rule; Kahneman et al., 1993), and proving a
// topic is this app's best moment, so the page says plainly what it earned.
// Everything here is a fact from the learner's own progress: no points, no
// badges, nothing that could be had without the proof.
import type { Module, Topic } from '../content/types.ts'
import { type ModuleCount, countModule } from './modules.ts'
import type { TopicProgress } from './progress.ts'

/**
 * The topics that proving `topicId` opened: those built directly on it
 * whose other prerequisites were already learned, and that aren't learned
 * themselves. `topics` are the ones that can be opened, in track order.
 */
export function openedBy(
  topicId: string,
  topics: Topic[],
  progress: Map<string, TopicProgress>,
): Topic[] {
  const learned = (id: string) => Boolean(progress.get(id)?.learnedAt)
  if (!learned(topicId)) return []
  return topics.filter(
    (topic) =>
      topic.prerequisites.includes(topicId) &&
      !learned(topic.id) &&
      topic.prerequisites.every(learned),
  )
}

/** A module's count before and after one more of its topics was proven. */
export type ModuleStep = {
  number: number
  module: Module
  count: ModuleCount
  /** How many were proven before this one. */
  before: number
  /** Every topic of the module that can be opened is now proven. */
  complete: boolean
}

/** Where proving a topic left its module. `number` is the module's, from 1. */
export function moduleStep(
  number: number,
  module: Module,
  progress: Map<string, TopicProgress>,
  canOpen: (topicId: string) => boolean,
): ModuleStep {
  const count = countModule(module, progress, canOpen)
  return {
    number,
    module,
    count,
    before: Math.max(0, count.proven - 1),
    complete: count.open > 0 && count.proven >= count.open,
  }
}
