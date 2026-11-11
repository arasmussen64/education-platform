import { describe, expect, it } from 'vitest'
import type { Topic } from '../content/types.ts'
import { fakeCheckpointContent, fakeTopic } from '../test/fakeContent.tsx'
import {
  type GradedEvent,
  progressOf,
  stateOf,
  type StepsOpened,
} from './progress.ts'

// A checkpoint's steps hand over most of its build's program, so once the
// learner has opened them, a pass of that main build no longer counts as
// the blank-editor proof; a fresh version does (ADR-0012, amended
// 2026-11-11).

// The fake checkpoint's main build is "build-receipt", and its fresh
// versions are "build-split" and "build-fuel".
const CHECKPOINT: Topic = {
  ...fakeCheckpointContent().topic,
  prerequisites: [],
}
const AFTER = fakeTopic({
  id: 'py.booleans-and-comparisons',
  prerequisites: [CHECKPOINT.id],
})
const TOPICS = [CHECKPOINT, AFTER]

/** 9:00, 10:00... on one day. */
const at = (hour: number) =>
  `2026-11-06T${String(hour).padStart(2, '0')}:00:00.000Z`

function check(item: string, passed: boolean, hour: number): GradedEvent {
  return {
    type: 'code_check',
    topic_id: CHECKPOINT.id,
    item_id: item,
    correct: passed,
    occurred_at: at(hour),
  }
}

function opened(hour: number, topicId = CHECKPOINT.id): StepsOpened {
  return { topic_id: topicId, occurred_at: at(hour) }
}

/** The debug and the explanation passed, early: only the build is in question. */
const REST: GradedEvent[] = [
  check('debug-tickets', true, 8),
  {
    type: 'explain_submit',
    topic_id: CHECKPOINT.id,
    item_id: 'explain',
    correct: true,
    occurred_at: at(8),
  },
]

function progressWith(events: GradedEvent[], steps: StepsOpened[]) {
  return progressOf(TOPICS, [...REST, ...events], steps)
}

describe('a checkpoint build after the steps were opened', () => {
  it("doesn't count a pass of the main build", () => {
    const progress = progressWith(
      [check('build-receipt', true, 11)],
      [opened(10)],
    )
    expect(progress.get(CHECKPOINT.id)?.passed.build).toBeUndefined()
    expect(progress.get(CHECKPOINT.id)?.learnedAt).toBeNull()
    // So the checkpoint isn't Passed, and the next module stays Locked.
    expect(stateOf(CHECKPOINT, progress, at(23))).toBe('in-progress')
    expect(stateOf(AFTER, progress, at(23))).toBe('locked')
  })

  it('counts a pass of a fresh version', () => {
    const progress = progressWith(
      [check('build-receipt', true, 11), check('build-fuel', true, 12)],
      [opened(10)],
    )
    expect(progress.get(CHECKPOINT.id)?.passed.build).toBe(at(12))
    expect(stateOf(CHECKPOINT, progress, at(23))).toBe('passed')
    expect(stateOf(AFTER, progress, at(23))).toBe('available')
  })

  it('still counts a pass of the main build from before the steps', () => {
    const progress = progressWith(
      [check('build-receipt', true, 9), check('build-receipt', true, 11)],
      [opened(10)],
    )
    expect(progress.get(CHECKPOINT.id)?.passed.build).toBe(at(9))
    expect(stateOf(CHECKPOINT, progress, at(23))).toBe('passed')
  })

  it('goes by the first time the steps were opened', () => {
    // Opened at 12 on one visit, and at 10 on an earlier one.
    const progress = progressWith(
      [check('build-receipt', true, 11)],
      [opened(12), opened(10)],
    )
    expect(progress.get(CHECKPOINT.id)?.passed.build).toBeUndefined()
    expect(progress.get(CHECKPOINT.id)?.stepsOpenedAt).toBe(at(10))
  })

  it('gives the same result whatever order the events arrive in', () => {
    const events = [
      check('build-receipt', true, 11),
      check('build-receipt', false, 9),
      check('build-split', true, 13),
    ]
    const steps = [opened(12), opened(10)]
    const inOrder = progressWith(events, steps)
    expect(progressWith([...events].reverse(), [...steps].reverse())).toEqual(
      inOrder,
    )
    expect(inOrder.get(CHECKPOINT.id)?.passed.build).toBe(at(13))
  })

  it('only changes the checkpoint whose steps were opened', () => {
    const progress = progressWith(
      [check('build-receipt', true, 11)],
      [opened(10, 'py.m2.checkpoint')],
    )
    expect(progress.get(CHECKPOINT.id)?.passed.build).toBe(at(11))
    expect(progress.get(CHECKPOINT.id)).not.toHaveProperty('stepsOpenedAt')
  })
})

describe('a history with no record of the steps', () => {
  // Opening the steps was first saved on 2026-11-11. Earlier history has no
  // such event, so its main-build passes keep counting, as they always did.
  it('counts every pass of the main build, as before', () => {
    const events = [check('build-receipt', true, 11)]
    const progress = progressOf(TOPICS, [...REST, ...events])
    expect(progress.get(CHECKPOINT.id)?.passed.build).toBe(at(11))
    expect(progress.get(CHECKPOINT.id)).not.toHaveProperty('stepsOpenedAt')
    expect(progressWith(events, [])).toEqual(progress)
  })

  it("doesn't take a Check of a step as a sign the steps were opened", () => {
    // A step's Check shows the steps were open then, but before 2026-11-11
    // nothing said so: reading it that way would rewrite what older history
    // meant. Only a saved opening counts.
    const progress = progressOf(TOPICS, [
      ...REST,
      check('step-read', true, 10),
      check('build-receipt', true, 11),
    ])
    expect(progress.get(CHECKPOINT.id)?.passed.build).toBe(at(11))
  })
})
