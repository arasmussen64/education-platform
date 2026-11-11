// Grading an estimate question (ADR-0024): reading what the learner typed as
// a number, and judging it against the item's tolerance. The validator
// (tools/validate_content.py) proved that the tolerance accepts the answer
// and none of the known mistakes, judging the edges the same way as here.
import type { EstimateItem, EstimateMistake } from './types.ts'

/** What the learner typed, read as a number, or what to say if it can't be. */
export type Reading =
  { ok: true; number: number } | { ok: false; message: string }

/**
 * Digits, with commas only between groups of three, and a point for
 * decimals: 1168, 1,168, 27.5 and .5. Not 11,68, which in much of Europe
 * means 11.68, so reading it as 1168 would be a guess.
 */
const PLAIN_NUMBER = /^(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)$/
/** A plus or minus sign (− too, as some keyboards type it), then a currency sign. */
const SIGN_AND_CURRENCY = /^([-+−]?)\s*\p{Sc}?\s*/u

export const NOT_A_NUMBER =
  'Type a number, like 1168, 1,168 or 27.5: a point for decimals, and commas only between thousands.'

/** Whether the answer is a percentage, so a % typed after it belongs there. */
export function isPercentUnit(unit: string): boolean {
  return /^\s*(?:%|percent(?:age)?\b)/i.test(unit)
}

/**
 * Reads what the learner typed as a number, forgiving the ways people
 * write one: spaces around it, a currency sign in front ($1,168), commas
 * between thousands, and a % after it when the answer is a percentage.
 * Anything else ("about 1200", "1.2k") isn't guessed at: the message says
 * how to type it, and nothing is counted.
 */
export function readNumber(typed: string, unit: string): Reading {
  let text = typed.trim()
  if (text === '') return { ok: false, message: 'Type a number first.' }
  if (text.endsWith('%')) {
    if (!isPercentUnit(unit)) {
      return {
        ok: false,
        message: `Leave out the %: the answer is in ${unit}.`,
      }
    }
    text = text.slice(0, -1).trimEnd()
  }
  const [front = '', sign = ''] = SIGN_AND_CURRENCY.exec(text) ?? []
  const digits = text.slice(front.length)
  if (!PLAIN_NUMBER.test(digits)) return { ok: false, message: NOT_A_NUMBER }
  const number = Number(digits.replaceAll(',', ''))
  // Four hundred digits are too many for the computer's numbers.
  if (!Number.isFinite(number)) return { ok: false, message: NOT_A_NUMBER }
  return { ok: true, number: sign === '' || sign === '+' ? number : -number }
}

/** How far from the answer a number may be and still count as right. */
export function allowance(item: EstimateItem): number {
  const { tolerance } = item
  return 'absolute' in tolerance
    ? tolerance.absolute
    : (Math.abs(item.answer) * tolerance.percent) / 100
}

/**
 * A hair of slack at the edges, because sums of decimals are a hair off in
 * the computer's binary numbers: 27.4 - 27.5 is -0.10000000000000142, which
 * would put 27.4 just outside "within 0.1 of 27.5". The validator works the
 * edges out exactly, so a number on the edge is accepted by both.
 */
function slack(around: number): number {
  return 1e-9 * Math.max(1, Math.abs(around))
}

/** Whether a number counts as right: inside the tolerance, edges included. */
export function withinTolerance(number: number, item: EstimateItem): boolean {
  return Math.abs(number - item.answer) <= allowance(item) + slack(item.answer)
}

/** The lowest and highest numbers that count as right. */
export function acceptedRange(item: EstimateItem): [number, number] {
  return [item.answer - allowance(item), item.answer + allowance(item)]
}

/**
 * How far off a number is, as a share of the answer: 0.22 for 22% high,
 * -0.1 for 10% low. Null when the answer is 0, which has no shares.
 */
export function relativeError(number: number, answer: number): number | null {
  return answer === 0 ? null : (number - answer) / Math.abs(answer)
}

/**
 * How near a typed number must be to a mistake's value to be taken for it:
 * half a percent, which allows for rounding along the way but not for a
 * different slip. A wrong claim about what the learner did would mislead.
 */
export const MISTAKE_MATCH = 0.005

/** The known mistake a typed number matches, the nearest if two do, or null. */
export function matchingMistake(
  number: number,
  mistakes: EstimateMistake[],
): EstimateMistake | null {
  let nearest: EstimateMistake | null = null
  for (const mistake of mistakes) {
    const gap = Math.abs(number - mistake.value)
    const near =
      gap <= MISTAKE_MATCH * Math.abs(mistake.value) + slack(mistake.value)
    if (near && (!nearest || gap < Math.abs(number - nearest.value))) {
      nearest = mistake
    }
  }
  return nearest
}

/** How many decimal places a number is written with: 27.5 has 1. */
function decimalsOf(number: number): number {
  const [, decimals = ''] = String(number).split('.')
  return String(number).includes('e') ? 10 : decimals.length
}

/** A number as the page shows it, with commas between thousands: 1,916. */
export function formatNumber(number: number): string {
  return number.toLocaleString('en-US', { maximumFractionDigits: 10 })
}

/**
 * A number worked out from the answer (a range's edge, a gap), shown to two
 * places more than the answer has, so 87.6 less 10% is 78.84, not the
 * computer's 78.83999999999999.
 */
export function formatNear(number: number, answer: number): string {
  return number.toLocaleString('en-US', {
    maximumFractionDigits: Math.min(10, decimalsOf(answer) + 2),
  })
}

/** A number with its unit: "28 core licences", or "20%" for a percentage. */
export function withUnit(number: string, unit: string): string {
  return unit.startsWith('%') ? `${number}${unit}` : `${number} ${unit}`
}
