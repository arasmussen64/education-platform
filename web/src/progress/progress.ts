// Each topic's progress toward Learned (v1 spec, F8), worked out from the
// learner's graded events by the rules in docs/specs/data-model.md
// ("Derived progress"). Like mistakes to revisit, nothing is stored: it's
// recalculated from the event log, so earlier passes count too.
//
// The pages show which proof checks have passed. Topic states, and gating
// by them, appear once explanations are graded: until then no topic can be
// Learned, so every topic after the first would show as Locked.
import type { Topic } from '../content/types.ts'

/** The three proof checks a topic needs (ADR-0002). */
export type Proof = 'build' | 'debug' | 'explain'
export const PROOFS: Proof[] = ['build', 'debug', 'explain']

/**
 * A graded event: an answer, a Check of code, or a graded explanation.
 * `correct` is whether it passed.
 */
export type GradedEvent = {
  type: 'answer' | 'code_check' | 'explain_submit'
  topic_id: string
  item_id: string | null
  correct: boolean
  /** In ISO format, UTC, so comparing the text compares the times. */
  occurred_at: string
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
}

/**
 * Where a topic stands. Mastered, Fading and Relearning arrive with reviews
 * (Milestone C); checkpoints are Passed rather than Learned.
 */
export type TopicState =
  'locked' | 'available' | 'in-progress' | 'learned' | 'passed'

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
      { started: false, passed: {}, learnedAt: null },
    ]),
  )
  const topicsById = new Map(topics.map((topic) => [topic.id, topic]))

  for (const event of events) {
    const topic = topicsById.get(event.topic_id)
    const entry = progress.get(event.topic_id)
    if (!topic || !entry) continue
    entry.started = true
    const proof = proofOf(topic, event)
    const earlier = proof && entry.passed[proof]
    if (proof && (!earlier || event.occurred_at < earlier)) {
      entry.passed[proof] = event.occurred_at
    }
  }

  for (const entry of progress.values()) {
    const times = PROOFS.map((proof) => entry.passed[proof]).filter(
      (time) => time !== undefined,
    )
    // ISO times in UTC sort in time order, so the last is the latest.
    entry.learnedAt =
      times.length === PROOFS.length ? (times.sort().at(-1) ?? null) : null
  }
  return progress
}

/**
 * Where a topic stands, given everyone's progress (its prerequisites'
 * included). A prerequisite counts once it's Learned or Passed, so a later
 * failed review never locks the topics built on it (ADR-0002).
 */
export function stateOf(
  topic: Topic,
  progress: Map<string, TopicProgress>,
): TopicState {
  const own = progress.get(topic.id)
  if (own?.learnedAt) return topic.kind === 'checkpoint' ? 'passed' : 'learned'
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
