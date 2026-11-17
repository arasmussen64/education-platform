import { describe, expect, it } from 'vitest'
import type { Attempt } from '../followups/followUps.ts'
import { fakeTopic } from '../test/fakeContent.tsx'
import {
  DEFAULT_REVIEW_ITEM_MINUTES,
  formatRatio,
  paced,
  reviewItemMinutes,
  stretches,
  timeInTopic,
  topicPace,
} from './pace.ts'
import type { TopicProgress } from './progress.ts'

const MINUTE = 60_000
/** A time on one fixed day, "10:25" → ISO. */
const at = (time: string) => `2026-11-06T${time}:00.000Z`

let lastId = 0
function attempt(time: string, overrides: Partial<Attempt> = {}): Attempt {
  return {
    id: `a${++lastId}`,
    type: 'answer',
    topic_id: 'topic',
    item_id: 'mcq',
    correct: true,
    occurred_at: at(time),
    ...overrides,
  }
}

describe('timeInTopic', () => {
  it('counts a sitting from the start of its first question to its last answer', () => {
    // Two minutes on the first question, then answers until 10:25.
    const events = [
      attempt('10:00', { duration_ms: 2 * MINUTE }),
      attempt('10:10'),
      attempt('10:25'),
    ]
    expect(timeInTopic(events, 'topic', at('23:59'))).toBe(27 * MINUTE)
  })

  it('starts a new sitting after a gap of more than 30 minutes', () => {
    const events = [
      attempt('14:05'),
      attempt('10:00', { duration_ms: 1 * MINUTE }),
      attempt('14:00', { duration_ms: 3 * MINUTE }),
      attempt('10:20'),
    ]
    // (20 + 1) in the morning, (5 + 3) in the afternoon: the order the
    // events arrive in doesn't matter.
    expect(timeInTopic(events, 'topic', at('23:59'))).toBe(29 * MINUTE)
  })

  it('leaves out reviews, the review context, the placement test, other topics and later events', () => {
    const events = [
      attempt('10:00'),
      attempt('10:10'),
      attempt('10:20', { type: 'review' }),
      attempt('10:20', { context: 'review' }),
      attempt('10:20', { context: 'placement' }),
      attempt('10:20', { topic_id: 'another' }),
      attempt('10:30'), // after "until"
    ]
    expect(timeInTopic(events, 'topic', at('10:15'))).toBe(10 * MINUTE)
  })

  it('caps the first question of a sitting like the practice hours do', () => {
    const events = [attempt('10:00', { duration_ms: 5 * 60 * MINUTE })]
    expect(timeInTopic(events, 'topic', at('23:59'))).toBe(30 * MINUTE)
  })
})

describe('topicPace', () => {
  const learned = (learnedAt: string | null): TopicProgress => ({
    started: true,
    passed: {},
    learnedAt,
    reviews: [],
    card: null,
  })
  const ONE = fakeTopic({ id: 'one', estimated_minutes: 10 })
  const TWO = fakeTopic({ id: 'two', estimated_minutes: 20 })
  const THREE = fakeTopic({ id: 'three', estimated_minutes: 30 })
  const FOUR = fakeTopic({ id: 'four', estimated_minutes: 10 })
  // Measured: 20, 20 and 45 minutes, so 2, 1 and 1.5 times the estimates.
  const events = [
    attempt('09:00', { topic_id: 'one' }),
    attempt('09:20', { topic_id: 'one' }),
    attempt('11:00', { topic_id: 'two' }),
    attempt('11:20', { topic_id: 'two' }),
    attempt('13:00', { topic_id: 'three' }),
    attempt('13:25', { topic_id: 'three' }),
    attempt('13:45', { topic_id: 'three' }),
    // Started, not proven: says nothing yet.
    attempt('15:00', { topic_id: 'four' }),
    attempt('15:50', { topic_id: 'four' }),
  ]
  const progress = new Map([
    ['one', learned(at('23:00'))],
    ['two', learned(at('23:00'))],
    ['three', learned(at('23:00'))],
    ['four', learned(null)],
  ])

  it('is the middle of the proven topics’ measured time over their estimates', () => {
    expect(topicPace([ONE, TWO, THREE, FOUR], progress, events)).toEqual({
      ratio: 1.5,
      topics: 3,
    })
  })

  it('waits for three proven topics', () => {
    expect(topicPace([ONE, TWO], progress, events)).toBeNull()
  })

  it('leaves out a proven topic with no time to measure', () => {
    const elsewhere = fakeTopic({ id: 'elsewhere', estimated_minutes: 10 })
    const withIt = new Map([...progress, ['elsewhere', learned(at('23:00'))]])
    expect(topicPace([ONE, TWO, elsewhere], withIt, events)).toBeNull()
  })
})

describe('paced', () => {
  it('stretches an estimate to a pace above 1', () => {
    expect(paced(30, { ratio: 1.5, topics: 3 })).toBe(45)
    expect(stretches({ ratio: 1.5, topics: 3 })).toBe(true)
  })

  it('never shrinks one: the measure is a floor', () => {
    expect(paced(30, { ratio: 0.8, topics: 3 })).toBe(30)
    expect(stretches({ ratio: 0.8, topics: 3 })).toBe(false)
    expect(paced(30, null)).toBe(30)
    expect(stretches(null)).toBe(false)
  })

  it('writes a ratio to one decimal place', () => {
    expect(formatRatio(1.4)).toBe('1.4×')
    expect(formatRatio(2)).toBe('2.0×')
  })
})

describe('reviewItemMinutes', () => {
  const inReview = (seconds: number) =>
    attempt('10:00', { context: 'review', duration_ms: seconds * 1000 })

  it('uses a default until five review answers have times', () => {
    expect(reviewItemMinutes([inReview(30), inReview(30)])).toBe(
      DEFAULT_REVIEW_ITEM_MINUTES,
    )
  })

  it("is the middle of the learner's own review answers", () => {
    const answers = [60, 90, 120, 30, 600].map(inReview)
    // Practice answers don't count.
    const practice = attempt('10:00', { duration_ms: 20 * MINUTE })
    expect(reviewItemMinutes([...answers, practice])).toBe(1.5)
  })
})
