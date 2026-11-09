// The review scheduler (ADR-0009): when a Learned topic should be reviewed
// next, from how its reviews went. It implements the published FSRS-4.5
// formulas with their default parameters, which is what "standard FSRS
// parameters" means in the ADR. Fitting the parameters to the owner's own
// history is part of the ML capstone, so the formulas live here, in plain
// sight, rather than in a library.
//
// The model keeps two numbers per topic:
// - stability: the number of days until the chance of remembering drops to
//   90%;
// - difficulty: from 1 (easy) to 10 (hard), which slows how fast stability
//   grows.
//
// Nothing is stored. A topic's card is replayed from its review events each
// time, like the rest of progress (ADR-0008).

/** How a review session went. "Easy" isn't used in v1 (ADR-0009). */
export type Rating = 'again' | 'hard' | 'good'

/** FSRS's grade numbers for each rating; Easy would be 4. */
const GRADE: Record<Rating, 1 | 2 | 3> = { again: 1, hard: 2, good: 3 }

/** The published FSRS-4.5 default parameters, w0 to w16. */
const W = [
  0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031, 1.6474,
  0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755,
]

// The forgetting curve: R = (1 + FACTOR * t / S) ** DECAY. These two
// constants make R exactly 0.9 when t days equal the stability S.
const DECAY = -0.5
const FACTOR = 19 / 81

/** The chance of remembering we aim for at review time (ADR-0009). */
export const REQUESTED_RETENTION = 0.9
/** Reviews are never scheduled further ahead than this. */
export const MAX_INTERVAL_DAYS = 365

export type MemoryState = {
  stability: number
  difficulty: number
}

const DAY_MS = 24 * 60 * 60 * 1000

/** The chance, 0 to 1, of still remembering after `elapsedDays`. */
export function retrievability(elapsedDays: number, stability: number): number {
  return Math.pow(1 + (FACTOR * Math.max(0, elapsedDays)) / stability, DECAY)
}

function clampDifficulty(difficulty: number): number {
  return Math.min(10, Math.max(1, difficulty))
}

/** The memory state after a topic's first review, rated `rating`. */
export function initialState(rating: Rating): MemoryState {
  const grade = GRADE[rating]
  return {
    stability: W[grade - 1] ?? 1,
    difficulty: clampDifficulty((W[4] ?? 5) - (grade - 3) * (W[5] ?? 1)),
  }
}

/**
 * The memory state after another review, `elapsedDays` after the last one.
 * A pass (Hard or Good) grows the stability; a lapse (Again) shrinks it.
 */
export function nextState(
  state: MemoryState,
  rating: Rating,
  elapsedDays: number,
): MemoryState {
  const grade = GRADE[rating]
  const { stability: s, difficulty: d } = state
  const r = retrievability(elapsedDays, s)
  const w = (index: number) => W[index] ?? 0

  const stability =
    grade === 1
      ? w(11) *
        Math.pow(d, -w(12)) *
        (Math.pow(s + 1, w(13)) - 1) *
        Math.exp(w(14) * (1 - r))
      : s *
        (Math.exp(w(8)) *
          (11 - d) *
          Math.pow(s, -w(9)) *
          (Math.exp(w(10) * (1 - r)) - 1) *
          (grade === 2 ? w(15) : 1) +
          1)

  // Difficulty drifts with the grade, then is pulled a little toward the
  // difficulty of a topic that was easy from the start ("mean reversion").
  const drifted = d - w(6) * (grade - 3)
  const easyStart = w(4) - w(5)
  const difficulty = clampDifficulty(w(7) * easyStart + (1 - w(7)) * drifted)
  return { stability, difficulty }
}

/** Days until the chance of remembering drops to the requested retention. */
export function intervalDays(stability: number): number {
  const days =
    (stability / FACTOR) * (Math.pow(REQUESTED_RETENTION, 1 / DECAY) - 1)
  return Math.min(MAX_INTERVAL_DAYS, Math.max(1, Math.round(days)))
}

/** One review session of a topic, as its event records it. */
export type Review = {
  /** In ISO format, UTC. */
  at: string
  rating: Rating
}

/** A topic's review card, replayed from its history. */
export type Card = MemoryState & {
  /** When the topic was last reviewed (or became Learned). */
  lastReview: string
  /** When the next review is due. */
  due: string
  /** How many review sessions there have been, not counting becoming Learned. */
  reviews: number
  /** How many of them were rated Again. */
  lapses: number
}

/** Fractional days from one ISO time to another. */
export function daysBetween(from: string, to: string): number {
  return (Date.parse(to) - Date.parse(from)) / DAY_MS
}

function addDays(iso: string, days: number): string {
  return new Date(Date.parse(iso) + days * DAY_MS).toISOString()
}

/**
 * The card for a topic that became Learned at `learnedAt`, after the given
 * reviews. Becoming Learned counts as a first review rated Good (ADR-0009).
 * Reviews from before then are ignored; the rest are applied in time order.
 */
export function replayCard(learnedAt: string, reviews: Review[]): Card {
  let state = initialState('good')
  let last = learnedAt
  let count = 0
  let lapses = 0
  const ordered = reviews
    .filter((review) => review.at >= learnedAt)
    .sort((a, b) => a.at.localeCompare(b.at))
  for (const review of ordered) {
    state = nextState(state, review.rating, daysBetween(last, review.at))
    last = review.at
    count += 1
    if (review.rating === 'again') lapses += 1
  }
  return {
    ...state,
    lastReview: last,
    due: addDays(last, intervalDays(state.stability)),
    reviews: count,
    lapses,
  }
}

/** The chance, 0 to 1, that the topic is still remembered at `now`. */
export function retrievabilityAt(card: Card, now: string): number {
  return retrievability(daysBetween(card.lastReview, now), card.stability)
}
