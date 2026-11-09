import { describe, expect, it } from 'vitest'
import type { Topic } from '../content/types.ts'
import { fakeCheckpointContent, fakeTopic } from '../test/fakeContent.tsx'
import { type GradedEvent, nextUp, progressOf, stateOf } from './progress.ts'

// A small map: the first topic, a second built on it, a checkpoint built on
// the second, and a topic after the checkpoint. Every topic's build is
// "build-hello" and its debug "debug-hello"; the checkpoint has its own,
// plus two fresh versions of its build.
const FIRST = fakeTopic({ id: 'py.programs-and-print', prerequisites: [] })
const SECOND = fakeTopic()
const CHECKPOINT: Topic = {
  ...fakeCheckpointContent().topic,
  prerequisites: [SECOND.id],
}
const AFTER = fakeTopic({
  id: 'py.booleans-and-comparisons',
  prerequisites: [CHECKPOINT.id],
})
const TOPICS = [FIRST, SECOND, CHECKPOINT, AFTER]

/** 9:00, 10:00... on one day. */
const at = (hour: number) =>
  `2026-11-06T${String(hour).padStart(2, '0')}:00:00.000Z`

function check(topic: Topic, item: string, passed: boolean, hour = 9) {
  return {
    type: 'code_check',
    topic_id: topic.id,
    item_id: item,
    correct: passed,
    occurred_at: at(hour),
  } satisfies GradedEvent
}

function answer(topic: Topic, item: string, correct: boolean, hour = 9) {
  return { ...check(topic, item, correct, hour), type: 'answer' } as const
}

function explained(topic: Topic, passed: boolean, hour = 9) {
  return {
    type: 'explain_submit',
    topic_id: topic.id,
    item_id: null,
    correct: passed,
    occurred_at: at(hour),
  } satisfies GradedEvent
}

/** All three proof checks passed. */
function proved(topic: Topic, hour = 9): GradedEvent[] {
  return [
    check(topic, topic.prove.build ?? '', true, hour),
    check(topic, topic.prove.debug ?? '', true, hour),
    explained(topic, true, hour),
  ]
}

const progressIn = (events: GradedEvent[], topic: Topic) =>
  progressOf(TOPICS, events).get(topic.id)

const stateIn = (events: GradedEvent[], topic: Topic) =>
  stateOf(topic, progressOf(TOPICS, events))

describe('progressOf', () => {
  it('notes when each proof check first passed', () => {
    const progress = progressIn(
      [
        check(SECOND, 'build-hello', false, 9),
        check(SECOND, 'build-hello', true, 10),
        check(SECOND, 'build-hello', true, 11),
        check(SECOND, 'debug-hello', true, 12),
      ],
      SECOND,
    )
    expect(progress).toEqual({
      started: true,
      passed: { build: at(10), debug: at(12) },
      learnedAt: null,
      reviews: [],
      card: null,
    })
  })

  it('counts only passing proof checks, not practice or failed tries', () => {
    const progress = progressIn(
      [
        answer(SECOND, 'mcq-print', true),
        check(SECOND, 'write-hello', true),
        check(SECOND, 'debug-hello', false),
        explained(SECOND, false),
      ],
      SECOND,
    )
    expect(progress).toEqual({
      started: true,
      passed: {},
      learnedAt: null,
      reviews: [],
      card: null,
    })
  })

  it('is Learned when the last of the three passes, in any order', () => {
    const progress = progressIn(
      [
        explained(SECOND, true, 9),
        check(SECOND, 'debug-hello', true, 11),
        check(SECOND, 'build-hello', true, 10),
      ],
      SECOND,
    )
    expect(progress?.learnedAt).toBe(at(11))
  })

  it("counts a pass on any fresh version as the checkpoint's build", () => {
    const progress = progressIn(
      [check(CHECKPOINT, 'build-fuel', true)],
      CHECKPOINT,
    )
    expect(progress?.passed).toEqual({ build: at(9) })
  })

  it('gives the same result whatever order the events arrive in', () => {
    const events = [
      check(SECOND, 'build-hello', true, 12),
      answer(FIRST, 'mcq-print', false, 8),
      check(SECOND, 'build-hello', true, 10),
      ...proved(FIRST, 11),
      check(CHECKPOINT, 'build-split', true, 13),
      explained(SECOND, true, 9),
    ]
    const inOrder = progressOf(TOPICS, events)
    expect(progressOf(TOPICS, [...events].reverse())).toEqual(inOrder)
    // As if the last few arrived late, from an outbox.
    expect(
      progressOf(TOPICS, [...events.slice(3), ...events.slice(0, 3)]),
    ).toEqual(inOrder)
  })

  it("ignores events for topics that aren't on the map", () => {
    const progress = progressOf(TOPICS, [check(FIRST, 'build-hello', true)])
    expect(
      progressOf(TOPICS, [
        check(FIRST, 'build-hello', true),
        { ...check(FIRST, 'build-hello', true), topic_id: 'py.retired' },
      ]),
    ).toEqual(progress)
  })
})

describe('stateOf', () => {
  it('is Available with nothing to wait for, until started', () => {
    expect(stateIn([], FIRST)).toBe('available')
    expect(stateIn([answer(FIRST, 'mcq-print', false)], FIRST)).toBe(
      'in-progress',
    )
  })

  it('is Locked while a prerequisite is not Learned, even when started', () => {
    expect(stateIn([], SECOND)).toBe('locked')
    expect(
      stateIn(
        [check(FIRST, 'build-hello', true), answer(SECOND, 'mcq-print', true)],
        SECOND,
      ),
    ).toBe('locked')
  })

  it('unlocks once every prerequisite is Learned', () => {
    expect(stateIn(proved(FIRST), SECOND)).toBe('available')
  })

  it('is Learned once all three checks pass', () => {
    expect(stateIn([...proved(FIRST), ...proved(SECOND)], SECOND)).toBe(
      'learned',
    )
    // The rule doesn't ask about prerequisites, so passes made before
    // gating existed count too.
    expect(stateIn(proved(SECOND), SECOND)).toBe('learned')
  })

  it('calls a checkpoint Passed, and unlocks the next module with it', () => {
    const events = [
      ...proved(FIRST),
      ...proved(SECOND),
      check(CHECKPOINT, 'build-split', true),
      check(CHECKPOINT, 'debug-tickets', true),
      explained(CHECKPOINT, true),
    ]
    expect(stateIn(events, CHECKPOINT)).toBe('passed')
    expect(stateIn(events, AFTER)).toBe('available')
    expect(stateIn(events.slice(0, -1), AFTER)).toBe('locked')
  })

  it("stays Locked when a prerequisite isn't on the map", () => {
    const orphan = fakeTopic({ id: 'py.orphan', prerequisites: ['py.gone'] })
    expect(stateOf(orphan, progressOf([orphan], []))).toBe('locked')
  })
})

describe('reviews and the states after Learned', () => {
  const dayAfter = (days: number) =>
    new Date(Date.parse(at(9)) + days * 24 * 60 * 60 * 1000).toISOString()
  const review = (
    topic: Topic,
    rating: 'again' | 'hard' | 'good',
    days: number,
  ): GradedEvent => ({
    type: 'review',
    topic_id: topic.id,
    item_id: 'review',
    correct: rating === 'good',
    occurred_at: dayAfter(days),
    rating,
  })
  const stateAt = (events: GradedEvent[], topic: Topic, days: number) =>
    stateOf(topic, progressOf(TOPICS, events), dayAfter(days))

  it('starts a review card when a topic becomes Learned, but not for checkpoints', () => {
    const progress = progressOf(TOPICS, [
      ...proved(FIRST),
      ...proved(SECOND),
      check(CHECKPOINT, 'build-split', true),
      check(CHECKPOINT, 'debug-tickets', true),
      explained(CHECKPOINT, true),
    ])
    const card = progress.get(FIRST.id)?.card
    expect(card?.lastReview).toBe(at(9))
    expect(card?.due.localeCompare(at(9))).toBeGreaterThan(0)
    expect(progress.get(AFTER.id)?.card).toBeNull()
    expect(progress.get(CHECKPOINT.id)?.card).toBeNull()
  })

  it('is Learned until the review is due, then Fading', () => {
    const events = proved(FIRST)
    expect(stateAt(events, FIRST, 0)).toBe('learned')
    expect(stateAt(events, FIRST, 1)).toBe('learned')
    expect(stateAt(events, FIRST, 30)).toBe('fading')
  })

  it('is Mastered once a review a week or more after Learned is rated Good', () => {
    const early = [...proved(FIRST), review(FIRST, 'good', 4)]
    expect(stateAt(early, FIRST, 5)).toBe('learned')
    const late = [...early, review(FIRST, 'good', 12)]
    expect(stateAt(late, FIRST, 13)).toBe('mastered')
    // A Hard review a week later isn't enough.
    const hard = [...proved(FIRST), review(FIRST, 'hard', 10)]
    expect(stateAt(hard, FIRST, 11)).toBe('learned')
  })

  it('is Relearning after a review rated Again, and stays unlocked below', () => {
    const events = [...proved(FIRST), review(FIRST, 'again', 4)]
    expect(stateAt(events, FIRST, 4)).toBe('relearning')
    // A failed review never re-locks the topics built on it (ADR-0002).
    expect(stateAt(events, SECOND, 4)).toBe('available')
    // The next Good review ends the relearning.
    expect(stateAt([...events, review(FIRST, 'good', 6)], FIRST, 6)).toBe(
      'learned',
    )
  })

  it('ignores reviews from before the topic was Learned', () => {
    const progress = progressOf(TOPICS, [
      review(FIRST, 'again', -3),
      ...proved(FIRST),
    ])
    expect(progress.get(FIRST.id)?.reviews).toEqual([])
    expect(progress.get(FIRST.id)?.card?.lapses).toBe(0)
  })
})

describe('nextUp', () => {
  const next = (events: GradedEvent[]) =>
    nextUp(TOPICS, progressOf(TOPICS, events))
  const checkpointPassed = [
    check(CHECKPOINT, 'build-split', true),
    check(CHECKPOINT, 'debug-tickets', true),
    explained(CHECKPOINT, true),
  ]

  it('starts with the first topic, and stays with it once started', () => {
    expect(next([])).toEqual({ topic: FIRST, state: 'available' })
    expect(next([answer(FIRST, 'mcq-print', false)])).toEqual({
      topic: FIRST,
      state: 'in-progress',
    })
  })

  it('moves on once a topic is Learned', () => {
    expect(next(proved(FIRST))).toEqual({ topic: SECOND, state: 'available' })
  })

  it('prefers a started topic further on to a fresh one', () => {
    const events = [
      ...proved(FIRST),
      ...proved(SECOND),
      check(CHECKPOINT, 'build-receipt', false),
    ]
    expect(next(events)).toEqual({ topic: CHECKPOINT, state: 'in-progress' })
  })

  it('skips a started topic that is still Locked', () => {
    // Started before gating existed, with its prerequisite not yet Learned.
    expect(next([answer(SECOND, 'mcq-print', true)])).toEqual({
      topic: FIRST,
      state: 'available',
    })
  })

  it('has nothing left once everything is Learned', () => {
    const events = [
      ...proved(FIRST),
      ...proved(SECOND),
      ...checkpointPassed,
      ...proved(AFTER),
    ]
    expect(next(events)).toBeNull()
  })
})
