import { describe, expect, it } from 'vitest'
import type { Topic } from '../content/types.ts'
import type { TopicProgress } from '../progress/progress.ts'
import { replayCard } from './fsrs.ts'
import { describeDrop, memoryRows, memorySummary } from './memory.ts'

const NOW = '2026-11-21T12:00:00.000Z'

function topic(id: string): Topic {
  return { id, title: id.toUpperCase(), kind: 'topic' } as unknown as Topic
}

/** A topic learned at `at` and never reviewed since. */
function learnedAt(at: string): TopicProgress {
  return {
    started: true,
    passed: {},
    learnedAt: at,
    reviews: [],
    card: replayCard(at, []),
  }
}

const progress = new Map<string, TopicProgress>([
  // Learned a month ago and never reviewed: long overdue.
  ['old', learnedAt('2026-10-21T12:00:00.000Z')],
  // Learned an hour ago: as fresh as it gets.
  ['new', learnedAt('2026-11-21T11:00:00.000Z')],
  // Started, not learned: no card.
  [
    'open',
    { started: true, passed: {}, learnedAt: null, reviews: [], card: null },
  ],
])
const topics = [topic('new'), topic('open'), topic('old')]

describe('how well each learned topic is remembered', () => {
  it('lists the topics with a review card, weakest first', () => {
    const rows = memoryRows(topics, progress, NOW)
    expect(rows.map((row) => row.topic.id)).toEqual(['old', 'new'])
    const [old, fresh] = rows
    expect(old.due).toBe(true)
    expect(old.percent).toBeLessThan(90)
    expect(fresh.due).toBe(false)
    expect(fresh.percent).toBe(100)
  })

  it('says where each will be tomorrow if left alone', () => {
    const [old, fresh] = memoryRows(topics, progress, NOW)
    expect(old.tomorrow).toBeLessThanOrEqual(old.percent)
    expect(fresh.tomorrow).toBeLessThan(fresh.percent)
  })

  it('puts the drop in words, and says when a day changes nothing', () => {
    const row = memoryRows(topics, progress, NOW)[1]
    expect(describeDrop({ ...row, percent: 84, tomorrow: 82 })).toBe(
      'at 84% and dropping: 82% by tomorrow',
    )
    expect(describeDrop({ ...row, percent: 61, tomorrow: 61 })).toBe(
      'at 61%, and holding for now',
    )
  })

  it('sums up how many have faded enough to review', () => {
    const rows = memoryRows(topics, progress, NOW)
    expect(memorySummary(rows)).toMatch(
      /^1 of your 2 learned topics has faded enough to need a review\./,
    )
    expect(memorySummary(rows.slice(1))).toMatch(
      /^None of your 1 learned topic needs a review yet\./,
    )
  })
})
