import { describe, expect, it } from 'vitest'
import type { Topic } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import type { TopicProgress } from '../progress/progress.ts'
import { replayCard } from '../reviews/fsrs.ts'
import { fakeTopic } from '../test/fakeContent.tsx'
import { BREAK_DAYS, dayLabel, welcomeBack } from './welcomeBack.ts'

// A fixed afternoon, passed in: nothing here reads the clock. 15:00 UTC is
// the same calendar day in every time zone from UTC-12 to UTC+8, so dayOf
// gives 2026-11-16 on any machine that runs this.
const NOW = '2026-11-16T15:00:00.000Z'
const TODAY = '2026-11-16'
const daysBefore = (days: number) =>
  new Date(Date.parse(NOW) - days * 86_400_000).toISOString()

/**
 * `count` topics Learned on different days, all due by now: topic t0 was
 * learned longest ago, so it has faded furthest.
 */
function learnedTopics(count: number): {
  topics: Topic[]
  progress: Map<string, TopicProgress>
} {
  const topics = Array.from({ length: count }, (_, i) =>
    fakeTopic({ id: `t${i}`, title: `Topic ${i}`, prerequisites: [] }),
  )
  const progress = new Map(
    topics.map((topic, i) => {
      const learnedAt = daysBefore(60 - i)
      const entry: TopicProgress = {
        started: true,
        passed: {},
        learnedAt,
        reviews: [],
        card: replayCard(learnedAt, []),
      }
      return [topic.id, entry]
    }),
  )
  return { topics, progress }
}

let lastId = 0
function practice(when: string, overrides: Partial<Attempt> = {}): Attempt {
  return {
    id: `a${++lastId}`,
    type: 'answer',
    topic_id: 'elsewhere',
    item_id: 'mcq',
    correct: true,
    occurred_at: when,
    ...overrides,
  }
}

/** Review sessions finished today. */
const reviewedToday = (count: number) =>
  Array.from({ length: count }, () =>
    practice(NOW, { type: 'review', item_id: 'review' }),
  )

describe('welcomeBack', () => {
  it('stays away after a short gap with no more due than a day can clear', () => {
    const { topics, progress } = learnedTopics(3)
    expect(
      welcomeBack({
        topics,
        progress,
        attempts: [practice(daysBefore(2))],
        now: NOW,
      }),
    ).toBeNull()
  })

  it(`welcomes the learner back after ${BREAK_DAYS} days or more, with the plan for today`, () => {
    const { topics, progress } = learnedTopics(3)
    const plan = welcomeBack({
      topics,
      progress,
      attempts: [practice(daysBefore(10))],
      now: NOW,
    })
    expect(plan?.breakDays).toBe(10)
    expect(plan?.due).toBe(3)
    expect(plan?.days).toHaveLength(1)
    expect(plan?.days[0].day).toBe(TODAY)
    // Most faded first: the one learned longest ago.
    expect(plan?.days[0].reviews.map((review) => review.topic.id)).toEqual([
      't0',
      't1',
      't2',
    ])
    // Two questions a review, a minute each until there are review times.
    expect(plan?.days[0].minutes).toBe(6)
  })

  it("doesn't count a gap of six days as a break", () => {
    const { topics, progress } = learnedTopics(1)
    expect(
      welcomeBack({
        topics,
        progress,
        attempts: [practice(daysBefore(6))],
        now: NOW,
      }),
    ).toBeNull()
  })

  it('says nothing about a break once the learner has practised today', () => {
    const { topics, progress } = learnedTopics(1)
    expect(
      welcomeBack({
        topics,
        progress,
        attempts: [practice(daysBefore(10)), practice(NOW)],
        now: NOW,
      }),
    ).toBeNull()
  })

  it("doesn't count the placement test as practice", () => {
    const { topics, progress } = learnedTopics(1)
    const plan = welcomeBack({
      topics,
      progress,
      attempts: [
        practice(daysBefore(10)),
        practice(daysBefore(1), { context: 'placement' }),
      ],
      now: NOW,
    })
    expect(plan?.breakDays).toBe(10)
  })

  it('welcomes back with no plan when nothing is due', () => {
    const plan = welcomeBack({
      topics: [],
      progress: new Map(),
      attempts: [practice(daysBefore(10))],
      now: NOW,
    })
    expect(plan).toEqual({ breakDays: 10, due: 0, days: [] })
  })

  it("spreads more than a day's limit over the next days, after what's left of today", () => {
    // A limit of 3 a day, one review already done today: 2 today, then 3,
    // then the last 2.
    const { topics, progress } = learnedTopics(7)
    const plan = welcomeBack({
      topics,
      progress,
      attempts: reviewedToday(1),
      now: NOW,
      limit: 3,
    })
    expect(plan?.breakDays).toBeNull()
    expect(plan?.due).toBe(7)
    expect(
      plan?.days.map(({ day, reviews }) => [
        day,
        reviews.map((review) => review.topic.id),
      ]),
    ).toEqual([
      ['2026-11-16', ['t0', 't1']],
      ['2026-11-17', ['t2', 't3', 't4']],
      ['2026-11-18', ['t5', 't6']],
    ])
  })

  it("starts tomorrow when today's reviews are all done", () => {
    const { topics, progress } = learnedTopics(4)
    const plan = welcomeBack({
      topics,
      progress,
      attempts: reviewedToday(3),
      now: NOW,
      limit: 3,
    })
    expect(plan?.days.map(({ day }) => day)).toEqual([
      '2026-11-17',
      '2026-11-18',
    ])
  })

  it("uses the learner's own review times for each day's minutes", () => {
    const { topics, progress } = learnedTopics(3)
    const quick = Array.from({ length: 5 }, () =>
      practice(daysBefore(10), { context: 'review', duration_ms: 30_000 }),
    )
    const plan = welcomeBack({ topics, progress, attempts: quick, now: NOW })
    // Six questions at half a minute each.
    expect(plan?.days[0].minutes).toBe(3)
  })
})

describe('dayLabel', () => {
  it('names today and tomorrow, then the weekday and date', () => {
    expect(dayLabel('2026-11-16', TODAY)).toBe('Today')
    expect(dayLabel('2026-11-17', TODAY)).toBe('Tomorrow')
    expect(dayLabel('2026-11-19', TODAY)).toBe('Thursday, Nov 19')
  })
})
