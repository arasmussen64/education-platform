import { type RefObject, useEffect, useState } from 'react'
import { rememberPlace } from './placeMemory.ts'

/**
 * The parts of a topic page a learner can be "at": each has an element
 * with this attribute, whose value is also the element's id, so the outline
 * can link to it. The names:
 *   place-objectives, place-lesson-1 … place-lesson-N (the lesson's
 *   paragraphs), place-resource, place-recap, place-item-<topic>-<item>,
 *   place-prove-build, place-prove-debug, place-prove-explain
 */
export const PLACE_ATTRIBUTE = 'data-place'

/** The page's first place; being there isn't worth remembering. */
export const START_PLACE = 'place-objectives'

export const LESSON_PLACE_PREFIX = 'place-lesson-'

export function itemPlace(topicId: string, itemId: string): string {
  return `place-item-${topicId}-${itemId}`
}

export function provePlace(proof: 'build' | 'debug' | 'explain'): string {
  return `place-prove-${proof}`
}

export type CurrentPlace = {
  /** The place the learner is looking at, if the page can tell. */
  current: string | null
  /** How many parts the lesson has, once the page has counted them. */
  lessonParts: number
}

const UNKNOWN: CurrentPlace = { current: null, lessonParts: 0 }

/**
 * Which place the learner is looking at: the first one, in page order, that
 * reaches into the top part of the screen. Remembered for the next visit.
 * Where nothing can be observed (the test environment lays nothing out),
 * it stays unknown.
 *
 * `refresh` is anything whose change means the page's places may have
 * changed (the progress loading, say); the places are found again then.
 */
export function useCurrentPlace(
  topicId: string,
  container: RefObject<HTMLElement | null>,
  refresh: unknown,
): CurrentPlace {
  const [place, setPlace] = useState<CurrentPlace>(UNKNOWN)

  useEffect(() => {
    const root = container.current
    if (!root || typeof IntersectionObserver === 'undefined') return
    const elements = [
      ...root.querySelectorAll<HTMLElement>(`[${PLACE_ATTRIBUTE}]`),
    ]
    const lessonParts = elements.filter((element) =>
      element.dataset.place?.startsWith(LESSON_PLACE_PREFIX),
    ).length
    const order = new Map(elements.map((element, index) => [element, index]))
    const inView = new Set<HTMLElement>()
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          const element = entry.target as HTMLElement
          if (entry.isIntersecting) inView.add(element)
          else inView.delete(element)
        }
        // The topmost of those in view. Between two places, the last one
        // stays current.
        const first = [...inView].sort(
          (a, b) => (order.get(a) ?? 0) - (order.get(b) ?? 0),
        )[0]
        const current = first?.dataset.place
        if (current) setPlace({ current, lessonParts })
      },
      // Only the top 45% of the screen counts, so "where you are" is what
      // you're reading, not what's coming up at the bottom.
      { rootMargin: '0px 0px -55% 0px' },
    )
    for (const element of elements) observer.observe(element)
    return () => observer.disconnect()
  }, [container, refresh])

  useEffect(() => {
    if (place.current && place.current !== START_PLACE) {
      rememberPlace(topicId, place.current)
    }
  }, [topicId, place])

  return place
}
