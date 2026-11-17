import { describe, expect, it } from 'vitest'
import type { Topic, Track } from '../content/types.ts'
import type { Attempt, FollowUp } from '../followups/followUps.ts'
import { progressOf } from '../progress/progress.ts'
import { fakeTopic } from '../test/fakeContent.tsx'
import {
  nextNewTopic,
  planSession,
  QUICK_REVIEW_COUNT,
  quickCount,
  quickPlan,
  reviewMinutes,
} from './sessionPlan.ts'

// Two small tracks: Python (first, then second built on it) and Cloud (one
// topic). Checkpoints are named but not among the topics, so they're skipped.
const FIRST = fakeTopic({
  id: 'py.programs-and-print',
  title: 'First',
  prerequisites: [],
})
const SECOND = fakeTopic({ title: 'Second' })
const CLOUD = fakeTopic({
  id: 'csa.linux.shell',
  title: 'Cloud',
  prerequisites: [],
})
const TOPICS: Topic[] = [FIRST, SECOND, CLOUD]

function track(id: string, order: number, topics: Topic[]): Track {
  return {
    id,
    title: id,
    summary: '',
    order,
    modules: [
      {
        id: `${id}.m1`,
        title: 'One',
        topics: topics.map((topic) => topic.id),
        checkpoint: `${id}.checkpoint`,
      },
    ],
  }
}
const TRACKS = [track('python', 1, [FIRST, SECOND]), track('cloud', 2, [CLOUD])]

// A fixed afternoon: these tests pass `now` themselves and never read the
// clock.
const NOW = '2026-11-16T15:00:00.000Z'
const daysBefore = (days: number) =>
  new Date(Date.parse(NOW) - days * 86_400_000).toISOString()

let lastId = 0
function attempt(
  topic: Topic,
  when: string,
  overrides: Partial<Attempt> = {},
): Attempt {
  return {
    id: `a${++lastId}`,
    type: 'answer',
    topic_id: topic.id,
    item_id: 'mcq',
    correct: true,
    occurred_at: when,
    ...overrides,
  }
}

/** The three proof checks, passed at `when`. */
function proved(topic: Topic, when: string): Attempt[] {
  return [
    attempt(topic, when, { type: 'code_check', item_id: topic.prove.build }),
    attempt(topic, when, { type: 'code_check', item_id: topic.prove.debug }),
    attempt(topic, when, { type: 'explain_submit', item_id: 'explain' }),
  ]
}

function followUp(topic: Topic, skillId: string, due: string): FollowUp {
  return {
    topicId: topic.id,
    skillId,
    missedOn: '2026-11-01',
    missedItems: [],
    correctOn: [],
    due,
  }
}

function plan(attempts: Attempt[], followUps: FollowUp[] = []) {
  return planSession({
    topics: TOPICS,
    progress: progressOf(TOPICS, attempts),
    attempts,
    followUps,
    now: NOW,
    trackList: TRACKS,
  })
}

describe('nextNewTopic', () => {
  it('starts the first track when nothing has been done', () => {
    const next = nextNewTopic(TRACKS, TOPICS, progressOf(TOPICS, []), [])
    expect(next?.topic.id).toBe(FIRST.id)
    expect(next?.state).toBe('available')
    expect(next?.track.id).toBe('python')
  })

  it('carries on in the track worked in most recently', () => {
    const attempts = [
      attempt(FIRST, daysBefore(3)),
      attempt(CLOUD, daysBefore(1)),
    ]
    const next = nextNewTopic(
      TRACKS,
      TOPICS,
      progressOf(TOPICS, attempts),
      attempts,
    )
    expect(next?.topic.id).toBe(CLOUD.id)
    expect(next?.state).toBe('in-progress')
  })

  it("doesn't count the placement test as working in a track", () => {
    const attempts = [
      attempt(FIRST, daysBefore(3)),
      attempt(CLOUD, daysBefore(1), { context: 'placement' }),
    ]
    const next = nextNewTopic(
      TRACKS,
      TOPICS,
      progressOf(TOPICS, attempts),
      attempts,
    )
    expect(next?.topic.id).toBe(FIRST.id)
  })

  it('passes over a track with nothing left to start', () => {
    // Everything in Python is learned; Cloud is next, though untouched.
    const attempts = [
      ...proved(FIRST, daysBefore(2)),
      ...proved(SECOND, daysBefore(1)),
    ]
    const next = nextNewTopic(
      TRACKS,
      TOPICS,
      progressOf(TOPICS, attempts),
      attempts,
    )
    expect(next?.topic.id).toBe(CLOUD.id)
  })
})

describe('planSession', () => {
  it('puts the most faded review first', () => {
    // Both are due; the one learned longer ago has faded further. (Two
    // topics that don't build on each other: proving SECOND would give
    // FIRST implicit review credit, ADR-0009 amended 2026-11-16.)
    const attempts = [
      ...proved(FIRST, daysBefore(30)),
      ...proved(CLOUD, daysBefore(10)),
    ]
    const { reviews } = plan(attempts)
    expect(reviews.map((review) => review.topic.id)).toEqual([
      FIRST.id,
      CLOUD.id,
    ])
    expect(reviews[0].retrievability).toBeLessThan(reviews[1].retrievability)
  })

  it("stops at what's left of the day's 20 reviews", () => {
    const doneToday = Array.from({ length: 19 }, () =>
      attempt(CLOUD, daysBefore(0), { type: 'review', item_id: 'review' }),
    )
    const attempts = [
      ...proved(FIRST, daysBefore(30)),
      ...proved(CLOUD, daysBefore(10)),
      ...doneToday,
    ]
    expect(plan(attempts).reviews.map((review) => review.topic.id)).toEqual([
      FIRST.id,
    ])
  })

  it('takes the mistakes due by today, and not those due later', () => {
    const { followUps } = plan(
      [],
      [
        followUp(FIRST, 'due-earlier', '2026-11-10'),
        followUp(FIRST, 'due-today', '2026-11-16'),
        followUp(FIRST, 'due-later', '2026-11-20'),
      ],
    )
    expect(followUps.map((each) => each.skillId)).toEqual([
      'due-earlier',
      'due-today',
    ])
  })

  it('ends with the next new topic', () => {
    expect(plan(proved(FIRST, daysBefore(1))).next?.topic.id).toBe(SECOND.id)
  })
})

describe('quickPlan', () => {
  it(`keeps only the ${QUICK_REVIEW_COUNT} most faded reviews, and nothing else`, () => {
    const full = {
      ...plan(
        [...proved(FIRST, daysBefore(30)), ...proved(SECOND, daysBefore(10))],
        [followUp(FIRST, 'skill', '2026-11-10')],
      ),
    }
    // Pretend there were five due, most faded first.
    const five = Array.from({ length: 5 }, (_, i) => ({
      ...full.reviews[0],
      retrievability: i / 10,
    }))
    const quick = quickPlan({ ...full, reviews: five })
    expect(quick.reviews).toEqual(five.slice(0, QUICK_REVIEW_COUNT))
    expect(quick.followUps).toEqual([])
    expect(quick.next).toBeNull()
  })

  it('keeps fewer when fewer are due', () => {
    const full = plan(proved(FIRST, daysBefore(30)))
    expect(quickPlan(full).reviews).toHaveLength(1)
  })
})

describe('the time a session takes', () => {
  /** Review answers that took `seconds` each. */
  const reviewAnswers = (seconds: number) =>
    Array.from({ length: 5 }, () =>
      attempt(FIRST, daysBefore(2), {
        context: 'review',
        duration_ms: seconds * 1000,
      }),
    )

  it('fits two reviews in five minutes until the learner has review times', () => {
    // Two questions a review at a minute each: two reviews.
    expect(quickCount([])).toBe(2)
  })

  it("fits as many as the learner's own review times allow, one to three", () => {
    expect(quickCount(reviewAnswers(30))).toBe(3)
    expect(quickCount(reviewAnswers(180))).toBe(1)
  })

  it('adds up two questions a review and one a mistake', () => {
    const attempts = [
      ...proved(FIRST, daysBefore(30)),
      ...proved(SECOND, daysBefore(10)),
    ]
    const twoReviewsOneMistake = plan(attempts, [
      followUp(FIRST, 'skill', '2026-11-10'),
    ])
    // Five questions at the default minute each.
    expect(reviewMinutes(twoReviewsOneMistake, attempts)).toBe(5)
    // At 30 seconds each, 2.5 minutes, rounded up.
    expect(
      reviewMinutes(twoReviewsOneMistake, [...attempts, ...reviewAnswers(30)]),
    ).toBe(3)
  })
})
