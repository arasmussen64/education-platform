// The review scheduler (ADR-0009): when a Learned topic should be reviewed
// next, from how its reviews went. It implements the FSRS-4.5 memory model
// with its default parameters, which is what "standard FSRS parameters"
// means in the ADR. Fitting the parameters to the owner's own history is
// part of the ML capstone, so the formulas live here, in plain sight,
// rather than in a library.
//
// Where the formulas come from (checked line by line on 2026-11-11, see
// ADR-0009's amendment):
// - the open-spaced-repetition wiki page "The Algorithm", sections FSRS v4
//   and FSRS-4.5;
// - fsrs-optimizer 4.29.0, the code that fitted the default parameters, and
//   fsrs-rs 0.6.4, the FSRS-4.5 that Anki ships. Both add two limits the
//   wiki leaves out: a lapse never raises stability, and stability stays
//   between 0.01 and 36,500 days.
// The tests compare this file with values from py-fsrs 2.5.1, the Python
// package's FSRS-4.5 release.
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

/**
 * Every grade the formulas know. Easy is here so the whole published
 * algorithm can be checked against the reference; no session is rated Easy
 * in v1.
 */
export type Grade = Rating | 'easy'

/** FSRS's grade numbers for each rating. */
const GRADE: Record<Grade, 1 | 2 | 3 | 4> = {
  again: 1,
  hard: 2,
  good: 3,
  easy: 4,
}

/** The published FSRS-4.5 default parameters, w0 to w16. */
const W = [
  0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031, 1.6474,
  0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755,
]

// The forgetting curve: R = (1 + FACTOR * t / S) ** DECAY. These two
// constants make R exactly 0.9 when t days equal the stability S.
const DECAY = -0.5
const FACTOR = 19 / 81

/** Stability never leaves this range, in days (fsrs-optimizer, fsrs-rs). */
const MIN_STABILITY = 0.01
const MAX_STABILITY = 36_500

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

/** Parameter w<index>. */
function w(index: number): number {
  return W[index] ?? 0
}

function clampDifficulty(difficulty: number): number {
  return Math.min(10, Math.max(1, difficulty))
}

function clampStability(stability: number): number {
  return Math.min(MAX_STABILITY, Math.max(MIN_STABILITY, stability))
}

/** The memory state after a topic's first review, rated `rating`. */
export function initialState(rating: Grade): MemoryState {
  const grade = GRADE[rating]
  return {
    // S0(G) = w(G-1)
    stability: clampStability(w(grade - 1)),
    // D0(G) = w4 - (G-3) * w5
    difficulty: clampDifficulty(w(4) - (grade - 3) * w(5)),
  }
}

/** S'r: the stability after a review that was passed (Hard, Good, Easy). */
function stabilityAfterPass(
  s: number,
  d: number,
  r: number,
  grade: number,
): number {
  const hardPenalty = grade === 2 ? w(15) : 1
  const easyBonus = grade === 4 ? w(16) : 1
  return (
    s *
    (1 +
      Math.exp(w(8)) *
        (11 - d) *
        Math.pow(s, -w(9)) *
        (Math.exp(w(10) * (1 - r)) - 1) *
        hardPenalty *
        easyBonus)
  )
}

/** S'f: the stability after a lapse (Again). */
function stabilityAfterLapse(s: number, d: number, r: number): number {
  const relearned =
    w(11) *
    Math.pow(d, -w(12)) *
    (Math.pow(s + 1, w(13)) - 1) *
    Math.exp(w(14) * (1 - r))
  // Forgetting never makes a memory more stable than it was. This only
  // matters after a long break, when R is low and the formula above can
  // come out higher than S (fsrs-optimizer and fsrs-rs both cap it).
  return Math.min(relearned, s)
}

/**
 * D': the difficulty moves with the grade (up after Again and Hard, down
 * after Easy, unchanged after Good), then is pulled a little (w7, 3%) back
 * toward D0(3) = w4, the difficulty a first review rated Good gives. That
 * pull is FSRS's "mean reversion": it keeps difficulty from drifting to an
 * extreme over many reviews.
 */
function nextDifficulty(d: number, grade: number): number {
  const moved = d - w(6) * (grade - 3)
  return clampDifficulty(w(7) * w(4) + (1 - w(7)) * moved)
}

/**
 * The memory state after another review, `elapsedDays` after the last one.
 * A pass (Hard, Good or Easy) grows the stability; a lapse (Again) shrinks
 * it.
 */
export function nextState(
  state: MemoryState,
  rating: Grade,
  elapsedDays: number,
): MemoryState {
  const grade = GRADE[rating]
  const { stability: s, difficulty: d } = state
  const r = retrievability(elapsedDays, s)
  const stability =
    grade === 1
      ? stabilityAfterLapse(s, d, r)
      : stabilityAfterPass(s, d, r, grade)
  return {
    stability: clampStability(stability),
    difficulty: nextDifficulty(d, grade),
  }
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
