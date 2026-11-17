import { describe, expect, it } from 'vitest'
import type { TopicContent } from '../content/types.ts'
import { itemKey, type ItemState } from '../progress/itemStates.ts'
import { fakeContent, fakeTopic } from '../test/fakeContent.tsx'
import { fakeLongContent, LONG_QUESTIONS } from '../test/fakeLongTopic.ts'
import { itemMinutes, proofMinutes, QUESTION_MINUTES } from './estimates.ts'
import {
  aboutMinutes,
  describeItems,
  type LadderItem,
  partAnchor,
  partOfAnchor,
  partsDone,
  practicePartCount,
  resumePart,
  splitLadder,
  topicParts,
  type TopicPart,
} from './topicParts.ts'

const ladder = (content: TopicContent): LadderItem[] =>
  content.topic.practice.map((itemId) => ({ itemId, content }))

const total = (parts: TopicPart[]) =>
  parts.reduce((sum, part) => sum + part.minutes, 0)

type Practice = Extract<TopicPart, { kind: 'practice' }>
const practiceParts = (parts: TopicPart[]) =>
  parts.filter((part): part is Practice => part.kind === 'practice')

describe('how long things take', () => {
  it('counts a quick question at a minute and a half, and a lab longer than Python', () => {
    const content = fakeLongContent()
    expect(itemMinutes(content, 'q-1')).toBe(QUESTION_MINUTES)
    expect(itemMinutes(content, 'example-lab')).toBeGreaterThan(
      itemMinutes(fakeContent(), 'example-hello'),
    )
    // Build, debug and the explanation.
    expect(proofMinutes(content)).toBe(50 + 40 + 15)
  })

  it('says "about" to the nearest 5 minutes, never under 5', () => {
    expect(aboutMinutes(28.4)).toBe('about 30 min')
    expect(aboutMinutes(1.5)).toBe('about 5 min')
    expect(aboutMinutes(102.5)).toBe('about 105 min')
  })
})

describe('a topic in parts', () => {
  it('is the lesson, the practice and the proofs, adding up to the topic’s total', () => {
    const content = fakeContent()
    const parts = topicParts(content, ladder(content))
    expect(parts.map((part) => [part.id, part.title])).toEqual([
      ['learn', 'Learn'],
      ['practice-1', 'Practice'],
      ['prove', 'Prove it'],
    ])
    expect(total(parts)).toBeCloseTo(content.topic.estimated_minutes)
    // A short Python topic's guesses don't fit in 30 minutes, so they're
    // scaled down and the lesson keeps a quarter.
    expect(parts[0]!.minutes).toBeCloseTo(7.5)
  })

  it('is the lesson alone while the topic is Locked', () => {
    const content = fakeContent()
    expect(
      topicParts(content, ladder(content), { locked: true }).map(
        (part) => part.id,
      ),
    ).toEqual(['learn'])
  })

  it('leaves out the practice or the proofs when the topic has none', () => {
    const content = fakeContent(
      fakeTopic({ practice: [], prove: { build: 'build-hello' } }),
    )
    expect(topicParts(content, []).map((part) => part.id)).toEqual([
      'learn',
      'prove',
    ])
  })

  it('cuts a long practice ladder into parts of about half an hour, in order', () => {
    const content = fakeLongContent()
    const items = ladder(content)
    const parts = topicParts(content, items)
    const practice = practiceParts(parts)
    expect(practice).toHaveLength(4)
    for (const part of practice) {
      expect(part.minutes).toBeGreaterThan(20)
      expect(part.minutes).toBeLessThanOrEqual(40)
    }
    // Every item once, in the ladder's order, and each part knows where it
    // starts.
    expect(practice.flatMap((part) => part.items)).toEqual(items)
    expect(practice.map((part) => part.start)).toEqual([0, 1, 20, 26])
    // Cut where the kind of work changes: the worked example on its own,
    // then questions, then the labs.
    expect(practice.map((part) => part.title)).toEqual([
      'Practice: Worked example',
      'Practice: 19 questions',
      'Practice: 5 questions and fill in the gaps',
      'Practice: Write it and 1 question',
    ])
    expect(total(parts)).toBeCloseTo(300)
    // The guesses fit inside 300 minutes, so nothing is scaled.
    expect(parts.at(-1)!.minutes).toBe(105)
  })
})

describe('cutting the practice', () => {
  it('keeps a ladder of 40 minutes or less in one part', () => {
    expect(practicePartCount(40, 10)).toBe(1)
    expect(practicePartCount(41, 10)).toBe(2)
    expect(practicePartCount(120, 30)).toBe(4)
    // Never more parts than items.
    expect(practicePartCount(200, 3)).toBe(3)
    expect(practicePartCount(0, 0)).toBe(0)
  })

  it('prefers to cut where questions give way to an exercise', () => {
    // Twelve questions (18 minutes), then two exercises of 12 and 15: the
    // even cut would split the questions; the natural one costs a little.
    const minutes = [...Array<number>(12).fill(1.5), 12, 15]
    const kinds = [
      ...Array<'question'>(12).fill('question'),
      'exercise' as const,
      'exercise' as const,
    ]
    const groups = splitLadder(minutes, kinds)
    expect(groups.map((group) => group.length)).toEqual([12, 2])
  })
})

describe('describing a part', () => {
  it('names its exercises and counts its questions, in order', () => {
    const content = fakeContent()
    const items = ladder(content)
    expect(describeItems(items)).toBe(
      'Worked example, 2 questions, fill in the gaps and write it',
    )
    expect(describeItems(items.slice(1, 2))).toBe('1 question')
  })
})

describe('which parts are done', () => {
  const content = fakeContent()
  const items = ladder(content)
  const parts = topicParts(content, items)
  const states = (...done: string[]) =>
    new Map<string, ItemState>(
      done.map((itemId) => [itemKey(content.topic.id, itemId), 'done']),
    )

  it("can't tell while the progress is unknown", () => {
    expect(partsDone(parts, content, null, {})).toBeNull()
    expect(partsDone(parts, content, new Map(), null)).toBeNull()
  })

  it('counts nothing done on a first visit', () => {
    expect([...partsDone(parts, content, new Map(), {})!]).toEqual([
      ['learn', false],
      ['practice-1', false],
      ['prove', false],
    ])
  })

  it('counts the lesson done once anything after it is tried, and practice once every item is right', () => {
    const tried = new Map<string, ItemState>([
      [itemKey(content.topic.id, 'mcq-print'), 'tried'],
    ])
    expect(partsDone(parts, content, tried, {})!.get('learn')).toBe(true)
    expect(partsDone(parts, content, tried, {})!.get('practice-1')).toBe(false)
    const all = states(...content.topic.practice)
    expect(partsDone(parts, content, all, {})!.get('practice-1')).toBe(true)
  })

  it('counts practice the quick check made optional as not holding a part back', () => {
    const allButOne = states(
      ...content.topic.practice.filter((item) => item !== 'write-hello'),
    )
    expect(partsDone(parts, content, allButOne, {})!.get('practice-1')).toBe(
      false,
    )
    const optional = new Set([itemKey(content.topic.id, 'write-hello')])
    expect(
      partsDone(parts, content, allButOne, {}, optional)!.get('practice-1'),
    ).toBe(true)
  })

  it('counts the proofs done once all three have passed', () => {
    const two = { build: '2026-11-06', debug: '2026-11-06' }
    expect(partsDone(parts, content, new Map(), two)!.get('prove')).toBe(false)
    // A passed proof means the lesson was left behind, too.
    expect(partsDone(parts, content, new Map(), two)!.get('learn')).toBe(true)
    const three = { ...two, explain: '2026-11-06' }
    expect(partsDone(parts, content, new Map(), three)!.get('prove')).toBe(true)
  })

  it("doesn't count an earlier topic's answers as starting this one", () => {
    const earlier = new Map<string, ItemState>([
      [itemKey('py.programs-and-print', 'mcq-print'), 'done'],
    ])
    expect(partsDone(parts, content, earlier, {})!.get('learn')).toBe(false)
  })
})

describe('where the page opens', () => {
  const content = fakeLongContent()
  const parts = topicParts(content, ladder(content))
  const done = (...ids: string[]) =>
    new Map(parts.map((part) => [part.id, ids.includes(part.id)]))

  it('opens at the first part while nothing is known', () => {
    expect(resumePart(parts, null, null)).toBe('learn')
    expect(resumePart(parts, null, 'gone-now')).toBe('learn')
    expect(resumePart(parts, null, 'practice-3')).toBe('practice-3')
  })

  it('opens at the first part not done', () => {
    expect(resumePart(parts, done('learn', 'practice-1'), null)).toBe(
      'practice-2',
    )
  })

  it('opens at the part last viewed while it is not done', () => {
    expect(resumePart(parts, done('learn'), 'prove')).toBe('prove')
    expect(resumePart(parts, done('learn', 'practice-2'), 'practice-2')).toBe(
      'practice-1',
    )
  })

  it('opens at the part last viewed once everything is done', () => {
    const all = done(...parts.map((part) => part.id))
    expect(resumePart(parts, all, 'practice-2')).toBe('practice-2')
    expect(resumePart(parts, all, null)).toBe('learn')
  })
})

describe('a link to a place opens its part', () => {
  const content = fakeLongContent()
  const parts = topicParts(content, ladder(content))
  const partFor = (anchor: string) => partOfAnchor(parts, content, anchor)?.id

  it('finds the lesson’s places, the practice items and the proofs', () => {
    expect(partFor('place-recap')).toBe('learn')
    expect(partFor('place-lesson-3')).toBe('learn')
    expect(partFor('place-objectives')).toBe('learn')
    expect(
      partFor(`place-item-py.values-and-types-${LONG_QUESTIONS[20]}`),
    ).toBe('practice-3')
    expect(partFor('item-write-lab')).toBe('practice-4')
    expect(partFor('place-prove-explain')).toBe('prove')
    expect(partFor('item-build-lab')).toBe('prove')
  })

  it('finds each part by its heading', () => {
    expect(parts.map((part) => partAnchor(part))).toEqual([
      'learn',
      'practice',
      'practice-2',
      'practice-3',
      'practice-4',
      'prove-it',
    ])
    for (const part of parts) expect(partFor(partAnchor(part))).toBe(part.id)
  })

  it('opens the lesson for an id it doesn’t know, which is in the lesson’s text', () => {
    expect(partFor('a-heading-in-the-lesson')).toBe('learn')
  })

  it('opens the lesson for practice while the topic is Locked', () => {
    const locked = topicParts(content, ladder(content), { locked: true })
    expect(partOfAnchor(locked, content, 'practice')?.id).toBe('learn')
    expect(partOfAnchor(locked, content, 'place-prove-build')?.id).toBe('learn')
  })
})
