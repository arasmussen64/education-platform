// How hard the practice has been for this learner (ADR-0030): the share of
// quick questions they got right on the first try, against a target of
// about 85%.
//
// Why 85%: for a wide class of learning systems, training goes fastest when
// about 85% of answers are right, a little over one mistake in seven
// (Wilson, Shenhav, Straccia & Cohen, 2019, "The Eighty Five Percent Rule
// for optimal learning"). Much higher and little is being learned; much
// lower and there's too little to build on. The figure was derived for
// simple learners and yes-or-no questions, so here it's a guide with a wide
// band around it, never a grade: nothing that counts as learned depends on
// it. It only decides which of two existing suggestions a page makes: skip
// practice you don't need ("Check what you know", "Prove it now"), or go
// back over the lesson first.
//
// Only first tries count, because a second try at the same question is
// easier than the question. Only quick questions (multiple choice, predict
// the output, typed answers and the like), asked in a lesson or in practice:
// a first Check of a program often fails on a typo, a review is scheduled to
// be right about 90% of the time, the placement test is meant to find the
// edge of what's known, and "Check what you know" is a test taken before
// practice.
import type { Attempt } from '../followups/followUps.ts'

/** The share of first tries right that learning is thought to go fastest at. */
export const TARGET_RATE = 0.85
/** From here up, the practice is on the easy side. */
export const EASY_FROM = 0.95
/** Below here, on the hard side. */
export const HARD_BELOW = 0.7

/** The overall figure looks at this many of the most recent first tries. */
export const RECENT_TRIES = 40
/** And says nothing until there are this many. */
export const FEWEST_TRIES = 20
/** A single topic's figure needs this many first tries in the topic. */
export const FEWEST_TOPIC_TRIES = 8

export type Band = 'easy' | 'about-right' | 'hard'

export type Difficulty = {
  /** First tries counted. */
  tries: number
  /** How many of them were right. */
  right: number
  /** right / tries, 0 to 1. */
  rate: number
  band: Band
}

/** One question's first try. */
export type FirstTry = {
  topicId: string
  itemId: string
  correct: boolean
  /** In ISO format. */
  at: string
}

/**
 * The learner's first try at each quick question asked in a lesson or in
 * practice, oldest first. See the note at the top for what's left out.
 */
export function firstTries(attempts: Attempt[]): FirstTry[] {
  const first = new Map<string, FirstTry>()
  for (const attempt of attempts) {
    if (attempt.type !== 'answer') continue
    if (attempt.quick_check) continue
    // Older answers were saved without a context; they were practice.
    const context = attempt.context ?? 'practice'
    if (context !== 'practice' && context !== 'learn') continue
    const key = `${attempt.topic_id}/${attempt.item_id}`
    const earlier = first.get(key)
    if (earlier && earlier.at <= attempt.occurred_at) continue
    first.set(key, {
      topicId: attempt.topic_id,
      itemId: attempt.item_id,
      correct: attempt.correct,
      at: attempt.occurred_at,
    })
  }
  return [...first.values()].sort((a, b) => a.at.localeCompare(b.at))
}

/** Which band a share of right answers falls in. */
export function bandOf(rate: number): Band {
  if (rate >= EASY_FROM) return 'easy'
  return rate < HARD_BELOW ? 'hard' : 'about-right'
}

/** The figure for some first tries, or null when there are fewer than `fewest`. */
function difficultyOf(tries: FirstTry[], fewest: number): Difficulty | null {
  if (tries.length < fewest) return null
  const right = tries.filter((each) => each.correct).length
  const rate = right / tries.length
  return { tries: tries.length, right, rate, band: bandOf(rate) }
}

/**
 * How hard practice has been lately: the most recent RECENT_TRIES first
 * tries, or null while there are fewer than FEWEST_TRIES.
 */
export function recentDifficulty(attempts: Attempt[]): Difficulty | null {
  return difficultyOf(firstTries(attempts).slice(-RECENT_TRIES), FEWEST_TRIES)
}

/** How hard one topic's quick questions have been, or null with too few. */
export function topicDifficulty(
  attempts: Attempt[],
  topicId: string,
): Difficulty | null {
  const own = firstTries(attempts).filter((each) => each.topicId === topicId)
  return difficultyOf(own, FEWEST_TOPIC_TRIES)
}

/**
 * The topics whose quick questions were easy or hard for this learner, the
 * furthest from the target first: where the content, or the learner's way
 * through it, may want a look.
 */
export function topicsOffTarget(
  attempts: Attempt[],
): { topicId: string; difficulty: Difficulty }[] {
  const byTopic = new Map<string, FirstTry[]>()
  for (const each of firstTries(attempts)) {
    byTopic.set(each.topicId, [...(byTopic.get(each.topicId) ?? []), each])
  }
  return [...byTopic]
    .map(([topicId, tries]) => ({
      topicId,
      difficulty: difficultyOf(tries, FEWEST_TOPIC_TRIES),
    }))
    .filter(
      (each): each is { topicId: string; difficulty: Difficulty } =>
        each.difficulty !== null && each.difficulty.band !== 'about-right',
    )
    .sort(
      (a, b) =>
        Math.abs(b.difficulty.rate - TARGET_RATE) -
          Math.abs(a.difficulty.rate - TARGET_RATE) ||
        a.topicId.localeCompare(b.topicId),
    )
}

/** "36 of 40 right first time (90%)". */
export function describeRate({ tries, right, rate }: Difficulty): string {
  return `${right} of ${tries} right first time (${Math.round(100 * rate)}%)`
}
