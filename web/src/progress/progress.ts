// Each topic's progress toward Learned and beyond (v1 spec, F8, F11), worked
// out from the learner's graded events by the rules in
// docs/specs/data-model.md ("Derived progress"). Like mistakes to revisit,
// nothing is stored: it's recalculated from the event log, so earlier passes
// count too.
import type { Topic } from '../content/types.ts'
import {
  type Card,
  type Rating,
  replayCard,
  type Review,
} from '../reviews/fsrs.ts'

/** The three proof checks a topic needs (ADR-0002). */
export type Proof = 'build' | 'debug' | 'explain'
export const PROOFS: Proof[] = ['build', 'debug', 'explain']

/**
 * A graded event: an answer, a Check of code, a graded explanation, or a
 * finished review session. `correct` is whether it passed.
 */
export type GradedEvent = {
  type: 'answer' | 'code_check' | 'explain_submit' | 'review'
  topic_id: string
  item_id: string | null
  correct: boolean
  /** In ISO format, UTC, so comparing the text compares the times. */
  occurred_at: string
  /** For a review session: how it was rated (ADR-0009). */
  rating?: Rating
}

export type TopicProgress = {
  /** Any graded attempt at one of the topic's questions or exercises. */
  started: boolean
  /** When each proof check first passed. */
  passed: Partial<Record<Proof, string>>
  /**
   * When the last of the three first passed: from then on, the topic is
   * Learned (a checkpoint, Passed).
   */
  learnedAt: string | null
  /** The review sessions since then, oldest first. */
  reviews: Review[]
  /** The review card, once the topic is Learned. Checkpoints have none. */
  card: Card | null
}

/** A review rated Good this long after Learned makes a topic Mastered. */
export const MASTERY_DAYS = 7

/**
 * Where a topic stands (ADR-0002, data-model.md "Derived progress").
 * Checkpoints are Passed rather than Learned, and never go further.
 */
export type TopicState =
  | 'locked'
  | 'available'
  | 'in-progress'
  | 'learned'
  | 'mastered'
  | 'fading'
  | 'relearning'
  | 'passed'

/** Which proof check, if any, passing this event counts as. */
function proofOf(topic: Topic, event: GradedEvent): Proof | undefined {
  if (!event.correct) return undefined
  if (event.type === 'explain_submit') return 'explain'
  if (event.type !== 'code_check' || event.item_id === null) return undefined
  if (event.item_id === topic.prove.build) return 'build'
  // A pass on any fresh version counts as passing the build (ADR-0012).
  if (topic.unstuck?.versions.includes(event.item_id)) return 'build'
  if (event.item_id === topic.prove.debug) return 'debug'
  return undefined
}

/**
 * Every topic's progress, from the learner's graded events. The order of
 * the events doesn't matter: only the first pass of each check counts, so
 * an event arriving late (say, from another device's outbox) changes
 * nothing but what it adds.
 */
export function progressOf(
  topics: Topic[],
  events: GradedEvent[],
): Map<string, TopicProgress> {
  const progress = new Map<string, TopicProgress>(
    topics.map((topic) => [
      topic.id,
      { started: false, passed: {}, learnedAt: null, reviews: [], card: null },
    ]),
  )
  const topicsById = new Map(topics.map((topic) => [topic.id, topic]))

  for (const event of events) {
    const topic = topicsById.get(event.topic_id)
    const entry = progress.get(event.topic_id)
    if (!topic || !entry) continue
    if (event.type === 'review') {
      if (event.rating) {
        entry.reviews.push({ at: event.occurred_at, rating: event.rating })
      }
      continue
    }
    entry.started = true
    const proof = proofOf(topic, event)
    const earlier = proof && entry.passed[proof]
    if (proof && (!earlier || event.occurred_at < earlier)) {
      entry.passed[proof] = event.occurred_at
    }
  }

  for (const [topicId, entry] of progress) {
    const times = PROOFS.map((proof) => entry.passed[proof]).filter(
      (time) => time !== undefined,
    )
    // ISO times in UTC sort in time order, so the last is the latest.
    entry.learnedAt =
      times.length === PROOFS.length ? (times.sort().at(-1) ?? null) : null
    entry.reviews.sort((a, b) => a.at.localeCompare(b.at))
    // The card starts when the topic becomes Learned (ADR-0009); reviews
    // from before then can't count.
    if (entry.learnedAt && topicsById.get(topicId)?.kind === 'topic') {
      entry.reviews = entry.reviews.filter(
        (review) => review.at >= (entry.learnedAt ?? ''),
      )
      entry.card = replayCard(entry.learnedAt, entry.reviews)
    }
  }
  return progress
}

/** Whether a Learned topic has survived a review at least a week later. */
function isMastered(entry: TopicProgress): boolean {
  if (!entry.learnedAt) return false
  const since = Date.parse(entry.learnedAt) + MASTERY_DAYS * 24 * 60 * 60 * 1000
  return entry.reviews.some(
    (review) => review.rating === 'good' && Date.parse(review.at) >= since,
  )
}

/**
 * Where a topic stands at `now`, given everyone's progress (its
 * prerequisites' included). A prerequisite counts once it's Learned or
 * Passed, in any of the learned states, so a later failed review never
 * locks the topics built on it (ADR-0002).
 */
export function stateOf(
  topic: Topic,
  progress: Map<string, TopicProgress>,
  now: string = new Date().toISOString(),
): TopicState {
  const own = progress.get(topic.id)
  if (own?.learnedAt) {
    if (topic.kind === 'checkpoint') return 'passed'
    if (own.reviews.at(-1)?.rating === 'again') return 'relearning'
    if (own.card && own.card.due <= now) return 'fading'
    return isMastered(own) ? 'mastered' : 'learned'
  }
  const unlocked = topic.prerequisites.every(
    (id) => progress.get(id)?.learnedAt,
  )
  if (!unlocked) return 'locked'
  return own?.started ? 'in-progress' : 'available'
}

/** Each state's icon and word, so no state is shown by color alone (F9). */
export const STATE_LABELS: Record<TopicState, { icon: string; label: string }> =
  {
    locked: { icon: '🔒', label: 'Locked' },
    available: { icon: '○', label: 'Available' },
    'in-progress': { icon: '◐', label: 'In progress' },
    learned: { icon: '✓', label: 'Learned' },
    mastered: { icon: '★', label: 'Mastered' },
    fading: { icon: '◔', label: 'Fading: review due' },
    relearning: { icon: '↻', label: 'Relearning' },
    passed: { icon: '✓', label: 'Passed' },
  }

/**
 * What to work on next (v1 spec, F12): the first topic in progress, in the
 * order given, or else the first Available one. `topics` are the ones that
 * can be opened, in track order. `progress` must cover what they build on
 * too, so their states can be worked out.
 */
export function nextUp(
  topics: Topic[],
  progress: Map<string, TopicProgress>,
): { topic: Topic; state: 'in-progress' | 'available' } | null {
  for (const wanted of ['in-progress', 'available'] as const) {
    const topic = topics.find((topic) => stateOf(topic, progress) === wanted)
    if (topic) return { topic, state: wanted }
  }
  return null
}
