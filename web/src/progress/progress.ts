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
  /** Where it happened. Placement answers don't count as starting a topic. */
  context?: string
}

/**
 * A time the learner opened a checkpoint's step-by-step help (ADR-0012),
 * saved as a `hint` event (see checkpoints/stepsOpened.ts).
 */
export type StepsOpened = {
  topic_id: string
  /** In ISO format, UTC, so comparing the text compares the times. */
  occurred_at: string
}

export type TopicProgress = {
  /** Any graded attempt at one of the topic's questions or exercises. */
  started: boolean
  /** When each proof check first passed. */
  passed: Partial<Record<Proof, string>>
  /**
   * For a checkpoint: when the learner first opened its steps, if they have.
   * From then on only a fresh version proves its build (ADR-0012).
   */
  stepsOpenedAt?: string
  /**
   * When the last of the three first passed: from then on, the topic is
   * Learned (a checkpoint, Passed).
   */
  learnedAt: string | null
  /** The review sessions since then, oldest first. */
  reviews: Review[]
  /** The review card, once the topic is Learned. Checkpoints have none. */
  card: Card | null
  /**
   * The topic's skills that have an open follow-up (ADR-0011), once
   * withOpenFollowUps has looked. Left out, none are known.
   */
  openFollowUps?: string[]
}

/**
 * A review rated Good this long after the topic became Learned, and after
 * its last failed review, makes a topic Mastered.
 */
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

/**
 * Which proof check, if any, passing this event counts as. `stepsOpenedAt`
 * is when the learner first opened the topic's steps, if they have.
 */
function proofOf(
  topic: Topic,
  event: GradedEvent,
  stepsOpenedAt: string | undefined,
): Proof | undefined {
  if (!event.correct) return undefined
  if (event.type === 'explain_submit') return 'explain'
  if (event.type !== 'code_check' || event.item_id === null) return undefined
  if (event.item_id === topic.prove.build) {
    // Once the steps are opened, a fresh version proves the build instead,
    // as long as there is one to prove it with.
    const counts =
      passedBeforeTheSteps(event, stepsOpenedAt) || !hasFreshVersions(topic)
    return counts ? 'build' : undefined
  }
  // A pass on any fresh version counts as passing the build (ADR-0012).
  if (topic.unstuck?.versions.includes(event.item_id)) return 'build'
  if (event.item_id === topic.prove.debug) return 'debug'
  return undefined
}

/**
 * Whether a pass of a checkpoint's main build came before the learner opened
 * its steps. The steps hand over most of that very program, so a pass after
 * them doesn't show it can be written from a blank editor; from then on a
 * fresh version proves the build (ADR-0012, amended 2026-11-11). Opening the
 * steps was first saved that day, so in older history nothing is known and
 * every pass counts, as it always did.
 */
function passedBeforeTheSteps(
  event: GradedEvent,
  stepsOpenedAt: string | undefined,
): boolean {
  return stepsOpenedAt === undefined || event.occurred_at < stepsOpenedAt
}

/**
 * Whether a topic has a fresh version that can prove its build instead of
 * the main one. Every ready checkpoint has two, but if one ever had none,
 * the main build must keep counting, or the build could never be proved.
 */
function hasFreshVersions(topic: Topic): boolean {
  return (topic.unstuck?.versions.length ?? 0) > 0
}

/** The first time each topic's steps were opened, by topic. */
function firstOpenings(stepsOpened: StepsOpened[]): Map<string, string> {
  const first = new Map<string, string>()
  for (const { topic_id, occurred_at } of stepsOpened) {
    const earlier = first.get(topic_id)
    if (!earlier || occurred_at < earlier) first.set(topic_id, occurred_at)
  }
  return first
}

/**
 * Every topic's progress, from the learner's graded events, and the times
 * they opened a checkpoint's steps. The order of the events doesn't matter:
 * only the first pass of each check counts, and only the first opening of
 * the steps, so an event arriving late (say, from another device's outbox)
 * changes nothing but what it adds.
 */
export function progressOf(
  topics: Topic[],
  events: GradedEvent[],
  stepsOpened: StepsOpened[] = [],
): Map<string, TopicProgress> {
  const progress = new Map<string, TopicProgress>(
    topics.map((topic) => [
      topic.id,
      { started: false, passed: {}, learnedAt: null, reviews: [], card: null },
    ]),
  )
  const topicsById = new Map(topics.map((topic) => [topic.id, topic]))
  for (const [topicId, openedAt] of firstOpenings(stepsOpened)) {
    const entry = progress.get(topicId)
    if (entry) entry.stepsOpenedAt = openedAt
  }

  for (const event of events) {
    const topic = topicsById.get(event.topic_id)
    const entry = progress.get(event.topic_id)
    if (!topic || !entry) continue
    // The placement test asks about topics the learner hasn't opened; its
    // answers say where to start, not that a topic is in progress (ADR-0021).
    if (event.context === 'placement') continue
    if (event.type === 'review') {
      if (event.rating) {
        entry.reviews.push({ at: event.occurred_at, rating: event.rating })
      }
      continue
    }
    entry.started = true
    const proof = proofOf(topic, event, entry.stepsOpenedAt)
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

/**
 * Whether a Learned topic is Mastered (ADR-0002, amended 2026-11-11): it has
 * survived a delayed review, and none of its skills is being relearned.
 */
function isMastered(entry: TopicProgress): boolean {
  return survivedDelayedReview(entry) && !entry.openFollowUps?.length
}

/**
 * Whether a review rated Good came at least a week after the topic was last
 * known to be fresh: when it became Learned, or its most recent review rated
 * Again, whichever is later. A failed review starts the week over, so a
 * relearning review a day or two after it can't count.
 */
function survivedDelayedReview(entry: TopicProgress): boolean {
  if (!entry.learnedAt) return false
  const failures = entry.reviews
    .filter((review) => review.rating === 'again')
    .map((review) => Date.parse(review.at))
  const freshAt = Math.max(Date.parse(entry.learnedAt), ...failures)
  const since = freshAt + MASTERY_DAYS * 24 * 60 * 60 * 1000
  return entry.reviews.some(
    (review) => review.rating === 'good' && Date.parse(review.at) >= since,
  )
}

/**
 * The progress, with each topic's skills that are still being relearned
 * noted on it (ADR-0011), so stateOf can hold Mastered back until they
 * close. `open` is every open follow-up; those of topics not in the map are
 * left out.
 */
export function withOpenFollowUps(
  progress: Map<string, TopicProgress>,
  open: { topicId: string; skillId: string }[],
): Map<string, TopicProgress> {
  const skillsByTopic = new Map<string, string[]>()
  for (const { topicId, skillId } of open) {
    skillsByTopic.set(topicId, [...(skillsByTopic.get(topicId) ?? []), skillId])
  }
  return new Map(
    [...progress].map(([topicId, entry]) => [
      topicId,
      { ...entry, openFollowUps: skillsByTopic.get(topicId) ?? [] },
    ]),
  )
}

/**
 * Where a topic stands at `now`, given everyone's progress (its
 * prerequisites' included). A prerequisite counts once it's Learned or
 * Passed, in any of the learned states, so a later failed review never
 * locks the topics built on it (ADR-0002). For Mastered, the progress must
 * have been through withOpenFollowUps; otherwise no follow-up holds it back.
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
