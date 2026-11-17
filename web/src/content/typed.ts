// Grading a typed item (ADR-0027): reading what the learner typed the item's
// way, then comparing it with the accepted answers and the known mistakes.
// tools/typed_answers.py reads answers exactly the same way for the
// validator, and both are tested against tools/tests/typed_cases.json, so
// answers the validator proved different are different here too.
import type { TypedCase, TypedItem, TypedKind } from './types.ts'

/** What a phone's "smart punctuation" types in place of plain quotes. */
const CURLY_QUOTES: Record<string, string> = {
  '“': '"',
  '”': '"',
  '„': '"',
  '‘': "'",
  '’': "'",
  '‚': "'",
}
/** Hyphens and a minus sign that look like "-" but aren't. */
const SHORT_DASHES = /[‐‑‒−]/g
/** What a phone or a Mac types for "--": an en or em dash. */
const LONG_DASHES = /[–—―]/g
/**
 * The characters Python's str.split() and str.strip() count as spaces, so
 * both sides split on exactly the same ones. (JavaScript's \s differs by
 * two: it counts U+FEFF and not U+001C to U+001F or U+0085.)
 */
const SPACE =
  '\\t\\n\\v\\f\\r\\x1c-\\x1f \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000'
const SPACES = new RegExp(`[${SPACE}]+`, 'g')
const ENDS = new RegExp(`^[${SPACE}]+|[${SPACE}]+$`, 'g')
const ONE_SPACE = new RegExp(`^[${SPACE}]`)
/** A shell prompt copied in front of a command. */
const PROMPTS = ['$', '>', 'PS>']
/** Marks a learner may put round a term: "VNet", 'VNet', `VNet`. */
const WRAPPERS = `"'\``
/** An answer shorter than this is never forgiven a slip (typed_answers.py). */
const SHORTEST_FORGIVEN = 5

/** A command's case matters; a term's doesn't. */
export function defaultCase(kind: TypedKind): TypedCase {
  return kind === 'command' ? 'sensitive' : 'insensitive'
}

/** The item's case rule: its own, or its kind's. */
export function caseOf(item: TypedItem): TypedCase {
  return item.case ?? defaultCase(item.kind)
}

function strip(text: string): string {
  return text.replace(ENDS, '')
}

function unwrap(text: string, marks: string): string {
  const first = text[0]
  if (text.length >= 2 && first === text.at(-1) && marks.includes(first!)) {
    return strip(text.slice(1, -1))
  }
  return text
}

function withoutPrompt(text: string): string {
  for (const prompt of PROMPTS) {
    const rest = text.slice(prompt.length)
    if (text.startsWith(prompt) && ONE_SPACE.test(rest)) return strip(rest)
  }
  return text
}

function withoutFullStop(text: string): string {
  return text.endsWith('.') ? strip(text.slice(0, -1)) : text
}

/**
 * The standard form of a typed answer (ADR-0027), step by step as in
 * tools/typed_answers.py: Unicode's compatibility form; straight quotes
 * and plain dashes; one space between words and none at the ends; then for
 * a command, backticks round it and a copied "$ " prompt taken off, and for
 * text, a full stop at the end and quotes round it; lower case when case
 * doesn't matter.
 */
export function normaliseTyped(
  text: string,
  kind: TypedKind,
  textCase: TypedCase,
): string {
  let read = text
    .normalize('NFKC')
    .replace(/[“”„‘’‚]/g, (q) => CURLY_QUOTES[q]!)
    .replace(SHORT_DASHES, '-')
    .replace(LONG_DASHES, kind === 'command' ? '--' : '-')
  read = strip(read.replace(SPACES, ' '))
  read =
    kind === 'command'
      ? withoutPrompt(unwrap(read, '`'))
      : withoutFullStop(unwrap(withoutFullStop(read), WRAPPERS))
  return textCase === 'insensitive' ? read.toLowerCase() : read
}

const isLetter = (character: string | undefined) =>
  character !== undefined && /^\p{L}$/u.test(character)

/**
 * Whether `typed` is `answer` with one slip of the fingers among its
 * letters: one changed, added or left out, or two neighbours swapped. Both
 * are already normalised. Digits, spaces and symbols are never slips, nor
 * is a letter in the other case, and an answer under five characters is
 * never forgiven one. Characters are counted as Python counts them, by code
 * point, so an emoji is one.
 */
export function isSlip(typed: string, answer: string): boolean {
  const a = Array.from(typed)
  const b = Array.from(answer)
  if (b.length < SHORTEST_FORGIVEN || typed === answer) return false
  if (a.length === b.length) {
    const differ = a.flatMap((each, index) =>
      each === b[index] ? [] : [index],
    )
    const [i, j] = differ
    if (differ.length === 1 && i !== undefined) {
      return (
        isLetter(a[i]) &&
        isLetter(b[i]) &&
        a[i]!.toLowerCase() !== b[i]!.toLowerCase()
      )
    }
    if (differ.length === 2 && i !== undefined && j === i + 1) {
      return a[i] === b[j] && a[j] === b[i] && isLetter(a[i]) && isLetter(a[j])
    }
    return false
  }
  const [shorter, longer] = a.length < b.length ? [a, b] : [b, a]
  if (longer.length - shorter.length !== 1) return false
  const joined = shorter.join('')
  for (const [index, letter] of longer.entries()) {
    if (longer.toSpliced(index, 1).join('') === joined) return isLetter(letter)
  }
  return false
}

/** How a typed answer was judged. */
export type TypedGrade = {
  correct: boolean
  /** The known mistake it matched, by id, or null. */
  mistake: string | null
  /** True when it was right but for one slip among its letters. */
  slip: boolean
  /** The accepted answer it matched, as the item writes it, or null. */
  matched: string | null
}

/**
 * Judges what the learner typed. An accepted answer is right. Then a known
 * mistake, so a mistake one letter from an answer is caught as the mistake,
 * not forgiven as a slip. Then, for text only, an accepted answer with one
 * slip among its letters is right too: the term was remembered, and
 * spelling isn't what's being practised. A command is never forgiven one,
 * because a shell would refuse it.
 */
export function gradeTyped(item: TypedItem, typed: string): TypedGrade {
  const textCase = caseOf(item)
  const read = (text: string) => normaliseTyped(text, item.kind, textCase)
  const mine = read(typed)
  const exact = item.answers.find((answer) => read(answer) === mine)
  if (exact !== undefined) {
    return { correct: true, mistake: null, slip: false, matched: exact }
  }
  const mistake = item.mistakes.find(({ answers: wrong }) =>
    wrong.some((each) => read(each) === mine),
  )
  if (mistake) {
    return { correct: false, mistake: mistake.id, slip: false, matched: null }
  }
  const near =
    item.kind === 'text'
      ? item.answers.find((answer) => isSlip(mine, read(answer)))
      : undefined
  if (near !== undefined) {
    return { correct: true, mistake: null, slip: true, matched: near }
  }
  return { correct: false, mistake: null, slip: false, matched: null }
}
