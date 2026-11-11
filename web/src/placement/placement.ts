// The placement test (ADR-0021): a short walk that finds where a learner's
// knowledge runs out, in a track or in the math ladder, without teaching or
// ticking anything off. Everything here is pure, so it can be tested on its
// own; the page drives it.
//
// The idea comes from knowledge space theory (docs/learning-science.md): a
// subject has a prerequisite structure, so what a learner knows is roughly a
// prefix of the topics in order. Finding where the prefix ends is a binary
// search: probe the middle topic with a few of its own review questions, and
// the result rules out half of what's left. Thirty topics take about five
// probes, so ten to fifteen questions.

/**
 * How many of the first items in order the learner knows, as far as the
 * walk has narrowed it down: at least `lo`, at most `hi`.
 */
export type Walk = { lo: number; hi: number }

/** A walk over `count` items in order, before any probe. */
export function startWalk(count: number): Walk {
  return { lo: 0, hi: Math.max(0, count) }
}

/** The index to probe next, or null once the walk has narrowed to one answer. */
export function nextProbe(walk: Walk): number | null {
  if (walk.lo >= walk.hi) return null
  return Math.floor((walk.lo + walk.hi) / 2)
}

/**
 * The walk after probing `index`. Passing it means everything up to and
 * including it counts as known; failing it means it and everything after
 * it doesn't.
 */
export function afterProbe(walk: Walk, index: number, passed: boolean): Walk {
  return passed
    ? { lo: Math.max(walk.lo, index + 1), hi: walk.hi }
    : { lo: walk.lo, hi: Math.min(walk.hi, index) }
}

/** The most probes a walk over `count` items can take. */
export function probesNeeded(count: number): number {
  return count <= 0 ? 0 : Math.ceil(Math.log2(count + 1))
}

/** How many items a probe asks, when the pool has that many. */
export const PROBE_SIZE = 3

export type Verdict = 'pass' | 'fail' | 'open'

/**
 * A probe's verdict from the answers so far, out of `size` questions: it
 * passes once at least half are right, and fails as soon as the questions
 * left can't get it there, so a decided probe stops early. Once every
 * question is answered it's never open.
 *
 * "At least half" means a tie passes: one right and one wrong out of two,
 * or two of four. ADR-0021 gives ties the benefit of the doubt, because a
 * generous estimate is caught by the topic's proofs later, and a stingy one
 * only costs a short lesson on something familiar. With two questions, a
 * first right answer decides it, as the second could only make a tie.
 */
export function verdict(results: boolean[], size: number): Verdict {
  const needed = Math.ceil(size / 2)
  const right = results.filter(Boolean).length
  const left = Math.max(0, size - results.length)
  if (right >= needed) return 'pass'
  if (right + left < needed) return 'fail'
  return 'open'
}

/** Which kind a question is, for mixing a probe. */
export type ItemKind = 'choice' | 'other'

/**
 * The questions a probe asks: up to `size` from the pool, in a shuffled
 * order, with at least one that isn't multiple choice when the pool has
 * one, because guessing a choice is easy and predicting output isn't.
 * `random` is Math.random, or a fixed one in tests.
 */
export function chooseProbeItems(
  pool: string[],
  kindOf: (id: string) => ItemKind,
  random: () => number = Math.random,
  size = PROBE_SIZE,
): string[] {
  const shuffled = shuffle(pool, random)
  const chosen = shuffled.slice(0, Math.min(size, shuffled.length))
  if (!chosen.some((id) => kindOf(id) === 'other')) {
    const other = shuffled.find((id) => kindOf(id) === 'other')
    if (other) chosen[chosen.length - 1] = other
  }
  return shuffle(chosen, random)
}

/** A copy of `list` in a random order (Fisher-Yates). */
export function shuffle<T>(list: T[], random: () => number): T[] {
  const copy = [...list]
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1))
    const a = copy[i]
    const b = copy[j]
    if (a !== undefined && b !== undefined) {
      copy[i] = b
      copy[j] = a
    }
  }
  return copy
}

/** One probe's outcome, as the result keeps it. */
export type ProbeResult = {
  /** The topic's or level's id. */
  id: string
  passed: boolean
  /** The questions asked, in order, and whether each was right. */
  asked: { item: string; correct: boolean }[]
}

/** What a finished walk says. */
export type Placement = {
  /** The items in order that count as known: the prefix the walk settled on. */
  known: string[]
  /** The first item that doesn't, where to start, or null if all are known. */
  next: string | null
  probes: ProbeResult[]
  asked: number
  correct: number
}

/** The result of a walk over `order` that settled at `walk.lo`. */
export function summarize(
  order: string[],
  walk: Walk,
  probes: ProbeResult[],
): Placement {
  const frontier = Math.min(walk.lo, order.length)
  const answers = probes.flatMap((probe) => probe.asked)
  return {
    known: order.slice(0, frontier),
    next: order[frontier] ?? null,
    probes,
    asked: answers.length,
    correct: answers.filter((answer) => answer.correct).length,
  }
}
