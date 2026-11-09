import type { ParsonsItem } from '../content/types.ts'

// How a Parsons problem's lines get mixed up (ADR-0016). Kept apart from the
// component so the component file exports only a component.

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
export function swap(list: string[], i: number, j: number): void {
  const a = list[i]
  const b = list[j]
  if (a !== undefined && b !== undefined) {
    list[i] = b
    list[j] = a
  }
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
