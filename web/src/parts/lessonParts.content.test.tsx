import type { MDXComponents } from 'mdx/types'
import { Children, isValidElement, type ReactNode } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import { withPlaces } from '../components/lessonSections.ts'
import {
  getTopic,
  loadTopicContent,
  loadTrackTopics,
  topicIdsOf,
  tracks,
} from '../content/content.ts'
import { practiceOutsideLesson } from '../content/lessonChecks.ts'
import type { TopicContent } from '../content/types.ts'
import { LESSON_PLACE_PREFIX } from '../place/useCurrentPlace.ts'
import { type LearnPart, topicParts } from './topicParts.ts'

// Every written lesson, as the app ships it: a long one is cut into parts at
// its questions (ADR-0025, amended 2026-11-21). The cuts are worked out from
// what the build measured in the lesson's source, and made on the page from
// what React is handed, so these tests check the two agree for real lessons.

let lessons: Promise<TopicContent[]> | undefined

/** Every topic with a lesson, across the tracks, loaded once. */
function writtenLessons(): Promise<TopicContent[]> {
  lessons ??= loadLessons()
  return lessons
}

async function loadLessons(): Promise<TopicContent[]> {
  await Promise.all(tracks().map((track) => loadTrackTopics(track.id)))
  const ids = tracks()
    .flatMap((track) => topicIdsOf(track))
    .filter((id) => getTopic(id)?.status === 'ready')
  const loaded = await Promise.all(ids.map((id) => loadTopicContent(id)))
  return loaded.filter(
    (content): content is TopicContent =>
      content !== null && content.Lesson !== null,
  )
}

function learnPartsOf(content: TopicContent): LearnPart[] {
  const items = practiceOutsideLesson(content).map((itemId) => ({
    itemId,
    content,
  }))
  return topicParts(content, items).filter((part) => part.kind === 'learn')
}

/**
 * The numbers of the places one part of a lesson shows, found by running
 * the lesson with stand-in tags (the real ones need a signed-in page).
 */
function placesShown(content: TopicContent, part: LearnPart): number[] {
  const shown: number[] = []
  const Check = () => null
  const Nothing = () => null
  const components = {
    Intro: ({ children }: { children?: ReactNode }) => {
      const kept = withPlaces(
        children,
        (child) => child.type === Check,
        part.sections,
      )
      Children.forEach(kept, (child) => {
        if (!isValidElement<{ id?: string }>(child)) return
        shown.push(Number(child.props.id?.slice(LESSON_PLACE_PREFIX.length)))
      })
      return null
    },
    Recap: Nothing,
    Resource: Nothing,
    Check,
    Puzzle: Nothing,
    Story: Nothing,
    Term: Nothing,
  } as unknown as MDXComponents
  const Lesson = content.Lesson!
  renderToStaticMarkup(<Lesson components={components} />)
  return shown
}

describe('every written lesson, in parts', () => {
  it('has places exactly where the build said they would be', async () => {
    for (const content of await writtenLessons()) {
      for (const part of learnPartsOf(content)) {
        const shown = placesShown(content, part)
        const where = `${content.topic.id}, ${part.id}`
        if (part.places.last === Infinity) {
          // The whole lesson in one part, or the resource and the recap.
          if (part.sections.from > 0) expect(shown, where).toEqual([])
          continue
        }
        expect(shown[0], where).toBe(part.places.first)
        expect(shown.at(-1), where).toBe(part.places.last)
        expect(shown.length, where).toBe(
          part.places.last - part.places.first + 1,
        )
      }
    }
  }, 120_000)

  it('asks each of its questions in exactly one part', async () => {
    for (const content of await writtenLessons()) {
      const asked = learnPartsOf(content).flatMap((part) => part.checks)
      expect([...asked].sort(), content.topic.id).toEqual(
        [...(content.lessonChecks ?? [])].sort(),
      )
    }
  }, 120_000)

  it('cuts every long lesson of the cloud track', async () => {
    for (const content of await writtenLessons()) {
      if (!content.topic.id.startsWith('csa.')) continue
      expect(learnPartsOf(content).length, content.topic.id).toBeGreaterThan(1)
    }
  }, 120_000)

  it('has no part past about 40 minutes that could have been cut', async () => {
    const tooLong: string[] = []
    for (const content of await writtenLessons()) {
      for (const part of learnPartsOf(content)) {
        // One stretch between two questions can't be cut, and neither can
        // the resource and the recap: that's somebody else's page or video.
        const oneStretch = part.sections.to - part.sections.from <= 1
        if (part.minutes > 45 && !oneStretch) {
          tooLong.push(
            `${content.topic.id} ${part.id}: ${Math.round(part.minutes)} min`,
          )
        }
      }
    }
    expect(tooLong).toEqual([])
  }, 120_000)
})
