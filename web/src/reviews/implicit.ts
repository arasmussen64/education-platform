// Implicit repetition (ADR-0009, amended 2026-11-16), the platform's
// version of Math Academy's "FIRe": practising a topic also exercises the
// topics it builds on, so those get part of the credit a review would give.
//
// Why it matters: every Learned topic has a card, reviews are capped at 20
// a day, and the cloud track alone will have about 340 topics. Without this,
// a learner deep in the track would spend their reviews on basics they use
// every day anyway.
//
// How much credit, in one sentence: an implicit review moves a
// prerequisite's next review date part of the way (its "share") toward
// where a real review rated Good, on that day, would have put it. A share
// of 0 changes nothing; a share of 1 would be a whole review. Shares here
// are at most 0.5.
//
// What it can never do (each is tested):
// - make a review come sooner: it only ever moves a date later;
// - count as a review: it isn't in the card's list of reviews, so it can't
//   be the review Mastered needs (ADR-0002), and the Today page's daily
//   limit doesn't count it;
// - penalise: a review of the advanced topic rated Again gives nothing, and
//   takes nothing away;
// - help a topic that is relearning (its last real review was Again), or
//   one that was refreshed too recently for another try to do much good.
//
// Like the rest of progress, nothing is stored: credits are worked out from
// the event log and replayed with the card's own reviews, in time order.
import type { Topic } from '../content/types.ts'
import type { GradedEvent } from '../progress/progress.ts'
import {
  addDays,
  type Card,
  daysBetween,
  initialState,
  intervalDays,
  MAX_STABILITY,
  type MemoryState,
  nextState,
  type Rating,
  type Review,
} from './fsrs.ts'

/**
 * The share of a Good review a direct prerequisite gets, by what happened
 * in the topic built on it. A Hard review had a wrong answer in it, so half
 * as much. A passed proof (a build or debug from a blank editor, or a
 * checkpoint's part) uses what it builds on as much as a Good review does.
 */
export const SHARE: Record<'good' | 'hard' | 'proof', number> = {
  good: 0.5,
  hard: 0.25,
  proof: 0.5,
}

/**
 * Each step further down the prerequisites halves the share: a topic two
 * steps below gets half what a direct prerequisite gets, three steps a
 * quarter.
 */
export const STEP_WEIGHT = 0.5

/** Shares smaller than this are dropped, which ends the walk down. */
export const MIN_SHARE = 0.1

/**
 * A card takes credit only once it's at least this far into its interval
 * (half way to due). Right after a review, recalling it again adds little
 * (the spacing effect, which FSRS models as small growth when recall is
 * near 100%), and this stops a burst of practice stacking up credit.
 */
export const HALF_WAY = 0.5

/** And at least this many days after its last review or credit. */
export const MIN_GAP_DAYS = 1

/**
 * At most this many credits between two real reviews. Credit can postpone
 * a topic's own review, but not for ever: after two, the topic waits for a
 * real one, which is the only kind that checks it directly and the only
 * kind that can make it Mastered.
 */
export const MAX_CREDITS_BETWEEN_REVIEWS = 2

/** Part of a review, from practice in a topic built on this one. */
export type Credit = {
  /** In ISO format, UTC: when the practice happened. */
  at: string
  /** The share of a Good review, 0 to 1. */
  share: number
  /** The topic that was practised. */
  from: string
}

/** Looks a topic up by ID; undefined for one that isn't known. */
export type TopicOf = (id: string) => Topic | undefined

/**
 * The topics that practice in `topic` gives credit to, each with its weight:
 * 1 for a direct prerequisite, then halved at each step down, while the
 * share it would carry stays above MIN_SHARE. Where two paths reach the
 * same topic, the shorter counts; weights never add up.
 *
 * Checkpoints are crossed out: they have no card, and the walk doesn't go
 * through them. "Builds on Checkpoint 1" means "comes after Module 1", not
 * "uses every Module 1 topic", so passing through would credit topics the
 * practice never touched. A checkpoint's own proofs do credit its direct
 * prerequisites: its tests use those topics' skills.
 */
export function creditWeights(
  topic: Topic,
  topicOf: TopicOf,
): Map<string, number> {
  const weights = new Map<string, number>()
  const biggest = Math.max(...Object.values(SHARE))
  let frontier = topic.prerequisites
  let weight = 1
  while (frontier.length > 0 && biggest * weight >= MIN_SHARE) {
    const next: string[] = []
    for (const id of frontier) {
      const below = topicOf(id)
      if (!below || below.kind !== 'topic') continue
      // Met already on a shorter path, or the topic itself (a loop).
      if (weights.has(id) || id === topic.id) continue
      weights.set(id, weight)
      next.push(...below.prerequisites)
    }
    frontier = next
    weight *= STEP_WEIGHT
  }
  return weights
}

/** Every exercise whose pass proves part of a topic: its proofs and their versions. */
function proofItems(topic: Topic): Set<string> {
  const { build, debug, more = [] } = topic.prove
  return new Set(
    [
      build,
      debug,
      ...(topic.unstuck?.versions ?? []),
      ...more.flatMap((part) => [part.id, ...(part.versions ?? [])]),
    ].filter((id) => id !== undefined),
  )
}

/**
 * The share of a Good review this event passes to a direct prerequisite of
 * its topic, or null when it passes none: a review rated Good or Hard, or a
 * passed proof. Practice answers don't count: they're made while learning,
 * often with hints. Nor does anything in the placement test (ADR-0021).
 */
function shareOf(event: GradedEvent, topic: Topic): number | null {
  if (event.context === 'placement') return null
  if (event.type === 'review') {
    if (event.rating === 'good') return SHARE.good
    if (event.rating === 'hard') return SHARE.hard
    return null
  }
  if (event.type === 'code_check' && event.correct && event.item_id) {
    return proofItems(topic).has(event.item_id) ? SHARE.proof : null
  }
  return null
}

/**
 * Every credit the events give, by the topic credited. Events in topics
 * that aren't known give none. The order of the events doesn't matter.
 */
export function creditsFrom(
  events: GradedEvent[],
  topicOf: TopicOf,
): Map<string, Credit[]> {
  const credits = new Map<string, Credit[]>()
  const weightsOf = new Map<string, Map<string, number>>()
  for (const event of events) {
    const topic = topicOf(event.topic_id)
    if (!topic) continue
    const share = shareOf(event, topic)
    if (share === null) continue
    let weights = weightsOf.get(topic.id)
    if (!weights) {
      weights = creditWeights(topic, topicOf)
      weightsOf.set(topic.id, weights)
    }
    for (const [id, weight] of weights) {
      const credited = share * weight
      if (credited < MIN_SHARE) continue
      const list = credits.get(id) ?? []
      list.push({ at: event.occurred_at, share: credited, from: topic.id })
      credits.set(id, list)
    }
  }
  return credits
}

/**
 * The memory state after an implicit review `elapsedDays` after the card's
 * last real review. A real review rated Good then would put the next review
 * `good` days after today; without one, it stays `stability` days after the
 * last review. The new stability puts it `share` of the way between the two.
 * The interval is the stability (at 90% retention, fsrs.ts), so moving the
 * due date and moving the stability are the same thing. Difficulty is left
 * alone: an implicit review says nothing about how hard the topic is.
 */
export function implicitState(
  state: MemoryState,
  elapsedDays: number,
  share: number,
): MemoryState {
  const good = nextState(state, 'good', elapsedDays).stability
  const moved = state.stability + share * (elapsedDays + good - state.stability)
  return {
    stability: Math.min(MAX_STABILITY, Math.max(state.stability, moved)),
    difficulty: state.difficulty,
  }
}

/** A real review or a credit, in time order. */
type Step =
  | { kind: 'review'; at: string; rating: Rating }
  | { kind: 'credit'; at: string; credit: Credit }

/**
 * Real reviews before credits at the same moment; then the biggest share
 * first, then by topic, so the result never depends on the input's order.
 */
function byTime(a: Step, b: Step): number {
  if (a.at !== b.at) return a.at.localeCompare(b.at)
  if (a.kind !== b.kind) return a.kind === 'review' ? -1 : 1
  if (a.kind === 'credit' && b.kind === 'credit') {
    return (
      b.credit.share - a.credit.share ||
      a.credit.from.localeCompare(b.credit.from)
    )
  }
  return 0
}

/** A card, and the credits that counted toward it. */
export type Replayed = { card: Card; counted: Credit[] }

/**
 * A topic's card, as fsrs.ts's replayCard makes it from becoming Learned
 * and its reviews, with implicit reviews applied in between. A credit
 * counts only when the topic isn't relearning, the card is at least half
 * way to due and a day past its last review or credit, and fewer than two
 * have counted since the last real review. Without credits, this is
 * replayCard exactly.
 */
export function replayWithCredits(
  learnedAt: string,
  reviews: Review[],
  credits: Credit[] = [],
): Replayed {
  let state = initialState('good')
  let last = learnedAt
  let touched = learnedAt
  let lastRating: Rating = 'good'
  let sinceReview = 0
  let count = 0
  let lapses = 0
  const counted: Credit[] = []
  const steps: Step[] = [
    ...reviews.map((review) => ({ kind: 'review' as const, ...review })),
    ...credits.map((credit) => ({
      kind: 'credit' as const,
      at: credit.at,
      credit,
    })),
  ]
    .filter((step) => step.at >= learnedAt)
    .sort(byTime)
  for (const step of steps) {
    if (step.kind === 'review') {
      state = nextState(state, step.rating, daysBetween(last, step.at))
      last = step.at
      touched = step.at
      lastRating = step.rating
      sinceReview = 0
      count += 1
      if (step.rating === 'again') lapses += 1
      continue
    }
    const elapsed = daysBetween(last, step.at)
    const counts =
      lastRating !== 'again' &&
      sinceReview < MAX_CREDITS_BETWEEN_REVIEWS &&
      daysBetween(touched, step.at) >= MIN_GAP_DAYS &&
      elapsed >= HALF_WAY * state.stability
    if (!counts) continue
    state = implicitState(state, elapsed, step.credit.share)
    touched = step.at
    sinceReview += 1
    counted.push(step.credit)
  }
  return {
    card: {
      ...state,
      lastReview: last,
      due: addDays(last, intervalDays(state.stability)),
      reviews: count,
      lapses,
    },
    counted,
  }
}
