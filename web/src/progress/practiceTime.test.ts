import { describe, expect, it } from 'vitest'
import type { Attempt } from '../followups/followUps.ts'
import {
  countedMs,
  formatDuration,
  formatHours,
  MAX_ATTEMPT_MS,
  nextMilestone,
  practiceTime,
  practiceTimeByTrack,
} from './practiceTime.ts'

const NOW = '2026-11-09T12:00:00.000Z'
const MINUTE = 60_000

let lastId = 0
function attempt(duration_ms: number | null | undefined, daysAgo = 0): Attempt {
  const when = new Date(NOW)
  when.setUTCDate(when.getUTCDate() - daysAgo)
  return {
    id: `attempt-${++lastId}`,
    type: 'answer',
    topic_id: 'py.variables',
    item_id: 'mcq-one',
    correct: true,
    occurred_at: when.toISOString(),
    duration_ms,
  }
}

describe('what an attempt counts for', () => {
  it('counts its duration, up to the cap', () => {
    expect(countedMs(attempt(90 * 1000))).toBe(90 * 1000)
    expect(countedMs(attempt(3 * 60 * MINUTE))).toBe(MAX_ATTEMPT_MS)
  })

  it('counts nothing without a usable duration', () => {
    expect(countedMs(attempt(null))).toBe(0)
    expect(countedMs(attempt(undefined))).toBe(0)
    expect(countedMs(attempt(0))).toBe(0)
    expect(countedMs(attempt(-5))).toBe(0)
    expect(countedMs(attempt(Number.NaN))).toBe(0)
  })
})

describe('practice time', () => {
  it('adds up the attempts, all time and the last seven days', () => {
    const time = practiceTime(
      [
        attempt(10 * MINUTE, 0),
        attempt(5 * MINUTE, 6),
        attempt(20 * MINUTE, 8),
        attempt(null, 1),
      ],
      NOW,
    )
    expect(time).toEqual({
      totalMs: 35 * MINUTE,
      recentMs: 15 * MINUTE,
      attempts: 3,
    })
  })

  it('is zero with nothing to count', () => {
    expect(practiceTime([], NOW)).toEqual({
      totalMs: 0,
      recentMs: 0,
      attempts: 0,
    })
  })
})

describe('practice time per track', () => {
  const trackOf = (topicId: string) =>
    topicId.startsWith('py.')
      ? 'python'
      : topicId.startsWith('csa.')
        ? 'cloud'
        : undefined
  const on = (topic_id: string, minutes: number, daysAgo = 0): Attempt => ({
    ...attempt(minutes * MINUTE, daysAgo),
    topic_id,
  })

  it('groups each attempt under the track that holds its topic', () => {
    const split = practiceTimeByTrack(
      [
        on('py.variables', 10),
        on('csa.linux.shell', 20, 8),
        on('py.loops', 5, 9),
        on('csa.linux.services', 2),
      ],
      NOW,
      ['python', 'cloud'],
      trackOf,
    )
    expect(split.tracks).toEqual([
      {
        trackId: 'python',
        time: { totalMs: 15 * MINUTE, recentMs: 10 * MINUTE, attempts: 2 },
      },
      {
        trackId: 'cloud',
        time: { totalMs: 22 * MINUTE, recentMs: 2 * MINUTE, attempts: 2 },
      },
    ])
    expect(split.other).toEqual({ totalMs: 0, recentMs: 0, attempts: 0 })
  })

  it('keeps a track with no attempts, at zero, and puts strays under other', () => {
    const split = practiceTimeByTrack(
      [on('gone.topic', 7), on('py.variables', 3)],
      NOW,
      ['python', 'cloud'],
      trackOf,
    )
    expect(
      split.tracks.map((each) => [each.trackId, each.time.totalMs]),
    ).toEqual([
      ['python', 3 * MINUTE],
      ['cloud', 0],
    ])
    expect(split.other).toEqual({
      totalMs: 7 * MINUTE,
      recentMs: 7 * MINUTE,
      attempts: 1,
    })
  })
})

describe('milestones', () => {
  it('starts at one hour and ends at ten thousand', () => {
    expect(nextMilestone(0)).toEqual({ hours: 1, remainingMs: 60 * MINUTE })
    expect(nextMilestone(59 * MINUTE)).toEqual({
      hours: 1,
      remainingMs: MINUTE,
    })
    expect(nextMilestone(60 * MINUTE)).toEqual({
      hours: 5,
      remainingMs: 4 * 60 * MINUTE,
    })
    expect(nextMilestone(10_000 * 60 * MINUTE)).toBeNull()
  })

  it('counts the gap from the whole minutes shown, so the page adds up', () => {
    // 27.6 minutes shows as 27; the gap to the hour must then be 33, not 32.
    expect(nextMilestone(27.6 * MINUTE)).toEqual({
      hours: 1,
      remainingMs: 33 * MINUTE,
    })
  })
})

describe('formatting', () => {
  it('writes durations in whole minutes and hours', () => {
    expect(formatDuration(0)).toBe('under a minute')
    expect(formatDuration(59 * 1000)).toBe('under a minute')
    expect(formatDuration(MINUTE)).toBe('1 minute')
    expect(formatDuration(15 * MINUTE + 59 * 1000)).toBe('15 minutes')
    expect(formatDuration(60 * MINUTE)).toBe('1 hour')
    expect(formatDuration(135 * MINUTE)).toBe('2 hours 15 minutes')
    expect(formatDuration(61 * MINUTE)).toBe('1 hour 1 minute')
  })

  it('writes milestones with their unit', () => {
    expect(formatHours(1)).toBe('1 hour')
    expect(formatHours(10)).toBe('10 hours')
    expect(formatHours(10000)).toBe('10,000 hours')
  })
})
