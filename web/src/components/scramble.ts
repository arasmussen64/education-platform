import type { McqItem, ParsonsItem } from '../content/types.ts'

// How a Parsons problem's lines get mixed up (ADR-0016), and the order a
// multiple-choice item's choices are shown in. Kept apart from the components
// so the component files export only components.

/**
 * A small repeatable random-number generator, seeded from text, so an item
 * is scrambled the same way every time it comes back.
 */
function seededRandom(seed: string): () => number {
  let h = 1779033703 ^ seed.length
  for (const char of seed) {
    h = Math.imul(h ^ char.charCodeAt(0), 3432918353)
    h = (h << 13) | (h >>> 19)
  }
  let state = h >>> 0
  return () => {
    state = (state + 0x6d2b79f5) >>> 0
    let t = state
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/** Swaps two entries of a list, in place. */
export function swap<T>(list: T[], i: number, j: number): void {
  const a = list[i]
  const b = list[j]
  if (a !== undefined && b !== undefined) {
    list[i] = b
    list[j] = a
  }
}

/**
 * The order to show a multiple-choice item's choices in, as the author's
 * indexes. Authors tend to write the right answer first and longest, so
 * showing the choices as written gives it away; a shuffle seeded from the
 * item's id puts it anywhere, and the same item looks the same every time it
 * comes back. Answers are still recorded by the author's index.
 */
export function choiceOrder(item: McqItem): number[] {
  const order = item.choices.map((_, index) => index)
  const random = seededRandom(`${item.id}/choices`)
  for (let i = order.length - 1; i > 0; i--) {
    swap(order, i, Math.floor(random() * (i + 1)))
  }
  return order
}

/** The lines and decoys, mixed up, and never already in the right order. */
export function scramble(item: ParsonsItem): string[] {
  const all = [...item.lines, ...item.distractors]
  const random = seededRandom(item.id)
  for (let i = all.length - 1; i > 0; i--) {
    swap(all, i, Math.floor(random() * (i + 1)))
  }
  const solved = item.lines.every((line, index) => all[index] === line)
  if (solved) {
    const first = all.shift()
    if (first !== undefined) all.push(first)
  }
  return all
}
