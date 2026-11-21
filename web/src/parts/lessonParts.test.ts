import { describe, expect, it } from 'vitest'
import type { TopicContent } from '../content/types.ts'
import { itemKey, type ItemState } from '../progress/itemStates.ts'
import { fakeContent, fakeTopic } from '../test/fakeContent.tsx'
import type { LessonSection } from '../tooling/remarkLessonShape.ts'
import { READING_WORDS_A_MINUTE } from './estimates.ts'
import {
  type LearnPart,
  partAnchor,
  partOfAnchor,
  partsDone,
  topicParts,
} from './topicParts.ts'

// A long lesson in parts (ADR-0025, amended 2026-11-21).

/** A section that takes this long to read, then asks a question. */
const section = (minutes: number, check: string | null): LessonSection => ({
  words: minutes * READING_WORDS_A_MINUTE,
  blocks: 3,
  check,
})

/** A topic that is all lesson, so the lesson's time is the topic's. */
function lessonOf(
  minutes: number,
  sections: LessonSection[],
  type: 'video' | 'reading' = 'reading',
): TopicContent {
  const topic = fakeTopic({
    estimated_minutes: minutes,
    practice: [],
    prove: {},
  })
  return {
    ...fakeContent({
      ...topic,
      resources: [{ ...topic.resources[0]!, type }],
    }),
    lessonChecks: sections
      .map((each) => each.check)
      .filter((item) => item !== null),
    lessonShape: { sections, recapWords: 0 },
  }
}

const learnParts = (content: TopicContent, pace?: number) =>
  topicParts(content, [], { pace }).filter(
    (part): part is LearnPart => part.kind === 'learn',
  )

describe('a long lesson in parts', () => {
  it('stays one part at 40 minutes or less', () => {
    const content = lessonOf(40, [section(10, 'a'), section(10, 'b')])
    expect(learnParts(content).map((part) => part.id)).toEqual(['learn'])
    expect(learnParts(content)[0]).toMatchObject({
      title: 'Learn',
      tail: true,
      checks: ['a', 'b'],
    })
  })

  it("stays one part when the build couldn't measure it", () => {
    const content = { ...lessonOf(200, []), lessonShape: undefined }
    expect(learnParts(content).map((part) => part.id)).toEqual(['learn'])
  })

  it('is cut at its questions, with the resource and the recap in a part of their own', () => {
    // Six stretches of 15 minutes and a question each: 99 minutes of
    // lesson text, so three parts of 33. The other 101 minutes are the
    // reading and the recap.
    const content = lessonOf(
      200,
      ['a', 'b', 'c', 'd', 'e', 'f'].map((check) => section(15, check)),
    )
    const parts = learnParts(content)
    expect(
      parts.map((part) => [part.id, part.title, Math.round(part.minutes)]),
    ).toEqual([
      ['learn', 'Learn: section 1 of 3', 33],
      ['learn-2', 'Learn: section 2 of 3', 33],
      ['learn-3', 'Learn: section 3 of 3', 33],
      ['learn-4', 'Learn: the reading and the recap', 101],
    ])
    expect(parts.map((part) => part.checks)).toEqual([
      ['a', 'b'],
      ['c', 'd'],
      ['e', 'f'],
      [],
    ])
    expect(parts.map((part) => part.tail)).toEqual([false, false, false, true])
    // Three blocks a section, numbered across the whole lesson.
    expect(parts.map((part) => part.places)).toEqual([
      { first: 1, last: 6 },
      { first: 7, last: 12 },
      { first: 13, last: 18 },
      { first: Infinity, last: Infinity },
    ])
    expect(parts.reduce((sum, part) => sum + part.minutes, 0)).toBeCloseTo(200)
  })

  it('names a lesson short enough for one part, before a long resource', () => {
    const content = lessonOf(90, [section(15, 'a'), section(15, 'b')], 'video')
    expect(learnParts(content).map((part) => part.title)).toEqual([
      'Learn: the lesson',
      'Learn: the video and the recap',
    ])
  })

  it('keeps a short resource and recap with the last section', () => {
    // 58.5 minutes of text leave a minute and a half for the rest.
    const content = lessonOf(60, [
      section(18, 'a'),
      section(18, 'b'),
      section(18, 'c'),
    ])
    const parts = learnParts(content)
    expect(parts.map((part) => [part.id, part.tail])).toEqual([
      ['learn', false],
      ['learn-2', true],
    ])
    expect(parts[1]!.checks).toEqual(['c'])
  })

  it('makes more, shorter parts for a learner whose topics run long', () => {
    const content = lessonOf(40, [section(15, 'a'), section(15, 'b')])
    expect(learnParts(content)).toHaveLength(1)
    // At twice the estimates the same lesson is 80 minutes of their time.
    const slower = learnParts(content, 2)
    expect(slower.map((part) => Math.round(part.minutes))).toEqual([33, 47])
    // A pace under 1 never shrinks anything.
    expect(learnParts(content, 0.5)[0]!.minutes).toBeCloseTo(40)
  })
})

describe('a lesson in parts: done, and links', () => {
  const content = lessonOf(
    200,
    ['a', 'b', 'c', 'd', 'e', 'f'].map((check) => section(15, check)),
  )
  const parts = topicParts(content, [])
  const right = (...items: string[]) =>
    new Map<string, ItemState>(
      items.map((itemId) => [itemKey(content.topic.id, itemId), 'done']),
    )

  it('counts a part done once each of its questions is right', () => {
    const done = partsDone(parts, content, right('a', 'b', 'c'), {})!
    expect([...done]).toEqual([
      ['learn', true],
      ['learn-2', false],
      ['learn-3', false],
      // It asks nothing, and nothing after the lesson has been tried.
      ['learn-4', false],
    ])
  })

  it('counts every part done once the topic is proven', () => {
    const proven = {
      ...fakeContent(),
      lessonChecks: ['a'],
      lessonShape: content.lessonShape,
    }
    const provenParts = topicParts(proven, [])
    const passed = { build: 'x', debug: 'x', explain: 'x' }
    const done = partsDone(provenParts, proven, new Map(), passed)!
    for (const part of provenParts) expect(done.get(part.id)).toBe(true)
  })

  it('has a heading to link to for each part', () => {
    expect(parts.map((part) => partAnchor(part))).toEqual([
      'learn',
      'learn-2',
      'learn-3',
      'learn-4',
    ])
    for (const part of parts) {
      expect(partOfAnchor(parts, content, partAnchor(part))?.id).toBe(part.id)
    }
  })

  it('opens the part that holds a place, a question, the resource or the recap', () => {
    const partFor = (anchor: string) => partOfAnchor(parts, content, anchor)?.id
    expect(partFor('place-lesson-1')).toBe('learn')
    expect(partFor('place-lesson-7')).toBe('learn-2')
    expect(partFor('place-lesson-18')).toBe('learn-3')
    expect(partFor('item-d')).toBe('learn-2')
    expect(partFor('place-resource')).toBe('learn-4')
    expect(partFor('place-recap')).toBe('learn-4')
    expect(partFor('place-objectives')).toBe('learn')
    // A place the lesson no longer has, or an id from its own text.
    expect(partFor('place-lesson-99')).toBe('learn')
    expect(partFor('a-heading-in-the-lesson')).toBe('learn')
  })
})
