import { describe, expect, it } from 'vitest'
import type { Topic } from '../content/types.ts'
import { fakeCheckpointContent, fakeTopic } from '../test/fakeContent.tsx'
import {
  furtherParts,
  type GradedEvent,
  progressOf,
  stateOf,
  type StepsOpened,
} from './progress.ts'

// A checkpoint can have further parts after its build and debug, in
// prove.more, and it's Passed only once every one of them has passed too
// (ADR-0012, amended 2026-11-11).

// The fake checkpoint's build is "build-receipt", with fresh versions
// "build-split" and "build-fuel", and its debug is "debug-tickets".
const PLAIN: Topic = { ...fakeCheckpointContent().topic, prerequisites: [] }
// The same, with Part 3, a build with one fresh version, and Part 4, a
// debug with none (topic.yaml leaves its versions out).
const WITH_PARTS: Topic = {
  ...PLAIN,
  prove: {
    ...PLAIN.prove,
    more: [
      { id: 'build-badge', versions: ['build-badge-b'] },
      { id: 'debug-badge' },
    ],
  },
}
const AFTER = fakeTopic({
  id: 'py.booleans-and-comparisons',
  prerequisites: [WITH_PARTS.id],
})

/** 9:00, 10:00... on one day. */
const at = (hour: number) =>
  `2026-11-06T${String(hour).padStart(2, '0')}:00:00.000Z`

function check(item: string, passed: boolean, hour: number): GradedEvent {
  return {
    type: 'code_check',
    topic_id: WITH_PARTS.id,
    item_id: item,
    correct: passed,
    occurred_at: at(hour),
  }
}

/** The build, the debug and the explain, all passed at 9. */
const FIRST_THREE: GradedEvent[] = [
  check('build-receipt', true, 9),
  check('debug-tickets', true, 9),
  {
    type: 'explain_submit',
    topic_id: WITH_PARTS.id,
    item_id: 'explain',
    correct: true,
    occurred_at: at(9),
  },
]

function progressWith(
  topic: Topic,
  events: GradedEvent[],
  steps: StepsOpened[] = [],
) {
  return progressOf([topic, AFTER], events, steps)
}

describe('furtherParts', () => {
  it('numbers the parts from 3, after the build and the debug', () => {
    expect(furtherParts(WITH_PARTS)).toEqual([
      { id: 'build-badge', versions: ['build-badge-b'], number: 3 },
      { id: 'debug-badge', versions: [], number: 4 },
    ])
  })

  it('has none for a checkpoint without them, or a topic', () => {
    expect(furtherParts(PLAIN)).toEqual([])
    expect(furtherParts(fakeTopic())).toEqual([])
  })
})

describe('a checkpoint with further parts', () => {
  it('is Passed only once every part has passed, at the last of them', () => {
    const halfway = progressWith(WITH_PARTS, [
      ...FIRST_THREE,
      check('build-badge', true, 10),
    ])
    expect(halfway.get(WITH_PARTS.id)?.learnedAt).toBeNull()
    expect(stateOf(WITH_PARTS, halfway, at(23))).toBe('in-progress')
    expect(stateOf(AFTER, halfway, at(23))).toBe('locked')

    const done = progressWith(WITH_PARTS, [
      ...FIRST_THREE,
      check('build-badge', true, 10),
      check('debug-badge', true, 11),
    ])
    expect(done.get(WITH_PARTS.id)).toMatchObject({
      passed: { build: at(9), debug: at(9), explain: at(9) },
      partsPassed: { 'build-badge': at(10), 'debug-badge': at(11) },
      learnedAt: at(11),
    })
    expect(stateOf(WITH_PARTS, done, at(23))).toBe('passed')
    expect(stateOf(AFTER, done, at(23))).toBe('available')
  })

  it('waits for the first three too, however many parts have passed', () => {
    const progress = progressWith(WITH_PARTS, [
      check('build-badge', true, 10),
      check('debug-badge', true, 11),
      check('debug-tickets', true, 12),
    ])
    expect(progress.get(WITH_PARTS.id)?.learnedAt).toBeNull()
  })

  it("counts a pass on a part's fresh version as the part", () => {
    const progress = progressWith(WITH_PARTS, [
      ...FIRST_THREE,
      check('build-badge-b', true, 10),
      check('debug-badge', true, 11),
    ])
    expect(progress.get(WITH_PARTS.id)?.partsPassed).toEqual({
      'build-badge': at(10),
      'debug-badge': at(11),
    })
    expect(progress.get(WITH_PARTS.id)?.learnedAt).toBe(at(11))
  })

  it('keeps the first pass of each part, and only passes', () => {
    const progress = progressWith(WITH_PARTS, [
      check('build-badge', false, 8),
      check('build-badge', true, 12),
      check('build-badge-b', true, 10),
      check('debug-badge', false, 9),
    ])
    expect(progress.get(WITH_PARTS.id)?.partsPassed).toEqual({
      'build-badge': at(10),
    })
  })

  it("doesn't take a part's pass for the build or the debug, or the other way round", () => {
    const progress = progressWith(WITH_PARTS, [
      check('build-badge', true, 9),
      check('debug-badge', true, 9),
    ])
    expect(progress.get(WITH_PARTS.id)?.passed).toEqual({})

    const theFirstTwo = progressWith(WITH_PARTS, FIRST_THREE.slice(0, 2))
    expect(theFirstTwo.get(WITH_PARTS.id)?.partsPassed).toEqual({})
  })

  it('counts a part passed after the steps were opened: the steps are for the build', () => {
    const progress = progressWith(
      WITH_PARTS,
      [
        // The build passed before the steps, the parts after them.
        ...FIRST_THREE,
        check('build-badge', true, 11),
        check('debug-badge', true, 12),
      ],
      [{ topic_id: WITH_PARTS.id, occurred_at: at(10) }],
    )
    expect(progress.get(WITH_PARTS.id)?.learnedAt).toBe(at(12))
  })

  it('gives the same result whatever order the events arrive in', () => {
    const events = [
      ...FIRST_THREE,
      check('debug-badge', true, 13),
      check('build-badge-b', true, 11),
      check('build-badge', true, 10),
    ]
    const forwards = progressWith(WITH_PARTS, events)
    const backwards = progressWith(WITH_PARTS, events.toReversed())
    expect(backwards).toEqual(forwards)
    expect(forwards.get(WITH_PARTS.id)?.learnedAt).toBe(at(13))
  })
})

// Every checkpoint written before further parts existed has none, and
// nothing about it changes.
describe('a checkpoint without further parts', () => {
  it('is Passed on its build, debug and explain, as before', () => {
    const progress = progressWith(PLAIN, FIRST_THREE)
    expect(progress.get(PLAIN.id)).toEqual({
      started: true,
      passed: { build: at(9), debug: at(9), explain: at(9) },
      learnedAt: at(9),
      reviews: [],
      card: null,
    })
    expect(stateOf(PLAIN, progress, at(23))).toBe('passed')
  })

  it('notes no parts for a topic either', () => {
    const topic = fakeTopic()
    const progress = progressOf([topic], [])
    expect(progress.get(topic.id)).not.toHaveProperty('partsPassed')
  })
})
