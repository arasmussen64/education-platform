import {
  Children,
  cloneElement,
  isValidElement,
  type ReactElement,
  type ReactNode,
} from 'react'
import {
  LESSON_PLACE_PREFIX,
  PLACE_ATTRIBUTE,
} from '../place/useCurrentPlace.ts'

/** Which of the intro's sections to show: `from` up to, not including, `to`. */
export type SectionRange = { from: number; to: number }

export const WHOLE_INTRO: SectionRange = { from: 0, to: Infinity }

/**
 * Marks each of the intro's paragraphs (and lists, and code blocks) as a
 * place, so the outline can say how far into the lesson the learner is and
 * the next visit can continue there.
 *
 * A long lesson is shown a few sections at a time (ADR-0025, amended
 * 2026-11-21). A section ends at a question, `isCheck`, so this counts
 * sections as it goes and keeps only the blocks in `range`. Places are
 * numbered across the whole intro before anything is left out, so a place
 * keeps its number whichever part it's shown in.
 *
 * The build measures the same sections from the lesson's source
 * (src/tooling/remarkLessonShape.ts); a test over every lesson checks that
 * the two agree.
 */
export function withPlaces(
  children: ReactNode,
  isCheck: (child: ReactElement) => boolean,
  range: SectionRange = WHOLE_INTRO,
): ReactNode {
  let place = 0
  let section = 0
  return Children.map(children, (child) => {
    const mine = section
    const shown = range.from <= mine && mine < range.to
    if (!isValidElement(child)) return shown ? child : null
    place += 1
    if (isCheck(child)) section += 1
    if (!shown) return null
    const id = `${LESSON_PLACE_PREFIX}${place}`
    return cloneElement(child as ReactElement<Record<string, unknown>>, {
      id,
      [PLACE_ATTRIBUTE]: id,
    })
  })
}
