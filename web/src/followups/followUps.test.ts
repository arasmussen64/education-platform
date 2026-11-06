import { describe, expect, it } from 'vitest'
import { fakeContent } from '../test/fakeContent.tsx'
import {
  addDays,
  type Attempt,
  chooseQuestion,
  dayOf,
  type FollowUp,
  openFollowUps,
  skillsIn,
  topicsWithMisses,
} from './followUps.ts'

const TOPIC = 'py.values-and-types'

// Item -> skills, as a topic would declare them.
const SKILLS: Record<string, string[]> = {
  'mcq-commas': ['commas'],
  'predict-commas': ['commas'],
  'mcq-quotes': ['quotes'],
  'write-card': ['quotes', 'blank-lines'],
  'build-banner': ['quotes'],
}
const skillsOf = (_topic: string, item: string) => SKILLS[item] ?? []

let lastId = 0

/** An attempt at `hour` o'clock, local time, on `day` (like "2026-11-06"). */
function attempt(
  item: string,
  correct: boolean,
  day: string,
  hour = 10,
  type: Attempt['type'] = item.startsWith('mcq') || item.startsWith('predict')
    ? 'answer'
    : 'code_check',
): Attempt {
  const [year = 0, month = 1, date = 1] = day.split('-').map(Number)
  return {
    id: `attempt-${++lastId}`,
    type,
    topic_id: TOPIC,
    item_id: item,
    correct,
    occurred_at: new Date(year, month - 1, date, hour).toISOString(),
  }
}

const skills = (followUps: FollowUp[]) =>
  followUps.map((followUp) => followUp.skillId)

describe('openFollowUps', () => {
  it('opens a follow-up after a wrong answer, due the next day', () => {
    const open = openFollowUps(
      [attempt('mcq-commas', false, '2026-11-06')],
      skillsOf,
    )
    expect(open).toEqual([
      {
        topicId: TOPIC,
        skillId: 'commas',
        missedOn: '2026-11-06',
        missedItems: ['mcq-commas'],
        correctOn: [],
        due: '2026-11-07',
      },
    ])
  })

  it("doesn't count a correct answer on the same day as the miss", () => {
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06', 10),
        attempt('predict-commas', true, '2026-11-06', 11),
      ],
      skillsOf,
    )
    expect(open[0]).toMatchObject({ correctOn: [], due: '2026-11-07' })
  })

  it('comes back 3 days after a correct day, and closes after 2 correct days', () => {
    const missed = attempt('mcq-commas', false, '2026-11-06')
    const firstRight = attempt('predict-commas', true, '2026-11-07')
    expect(openFollowUps([missed, firstRight], skillsOf)[0]).toMatchObject({
      correctOn: ['2026-11-07'],
      due: '2026-11-10',
    })

    const secondRight = attempt('mcq-commas', true, '2026-11-10')
    expect(openFollowUps([missed, firstRight, secondRight], skillsOf)).toEqual(
      [],
    )
  })

  it('starts over after another miss', () => {
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06'),
        attempt('predict-commas', true, '2026-11-07'),
        attempt('mcq-commas', false, '2026-11-10'),
      ],
      skillsOf,
    )
    expect(open[0]).toMatchObject({
      missedOn: '2026-11-10',
      correctOn: [],
      due: '2026-11-11',
    })
  })

  it('reopens a relearned skill that is missed again', () => {
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06'),
        attempt('predict-commas', true, '2026-11-07'),
        attempt('predict-commas', true, '2026-11-10'),
        attempt('mcq-commas', false, '2026-12-01'),
      ],
      skillsOf,
    )
    expect(open[0]).toMatchObject({ missedOn: '2026-12-01' })
  })

  it("doesn't treat failing Checks as mistakes when the code passes that day", () => {
    const workedItOut = [
      attempt('write-card', false, '2026-11-06', 10),
      attempt('write-card', false, '2026-11-06', 11),
      attempt('write-card', true, '2026-11-06', 12),
    ]
    expect(openFollowUps(workedItOut, skillsOf)).toEqual([])

    const neverPassed = [attempt('write-card', false, '2026-11-06')]
    expect(skills(openFollowUps(neverPassed, skillsOf))).toEqual([
      'blank-lines',
      'quotes',
    ])
  })

  it('treats any wrong answer to a question that day as a miss', () => {
    const open = openFollowUps(
      [
        attempt('mcq-quotes', true, '2026-11-06', 10),
        attempt('mcq-quotes', false, '2026-11-06', 11),
      ],
      skillsOf,
    )
    expect(skills(open)).toEqual(['quotes'])
  })

  it('opens a follow-up for every skill a missed item tests', () => {
    const open = openFollowUps(
      [attempt('write-card', false, '2026-11-06')],
      skillsOf,
    )
    expect(skills(open)).toEqual(['blank-lines', 'quotes'])
  })

  it('counts proof checks as misses too', () => {
    const open = openFollowUps(
      [attempt('build-banner', false, '2026-11-06')],
      skillsOf,
    )
    expect(skills(open)).toEqual(['quotes'])
  })

  it('ignores items that no longer exist or test no skill', () => {
    expect(
      openFollowUps([attempt('mcq-gone', false, '2026-11-06')], skillsOf),
    ).toEqual([])
  })

  it('gives the same result whatever order the history arrives in', () => {
    const history = [
      attempt('mcq-commas', false, '2026-11-06'),
      attempt('predict-commas', true, '2026-11-07'),
      attempt('mcq-quotes', false, '2026-11-08'),
    ]
    expect(openFollowUps([...history].reverse(), skillsOf)).toEqual(
      openFollowUps(history, skillsOf),
    )
  })

  it("uses the learner's own calendar days", () => {
    // 11:30 pm and half past midnight are different days, wherever you are.
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06', 23),
        attempt('predict-commas', true, '2026-11-07', 0),
      ],
      skillsOf,
    )
    expect(open[0]?.correctOn).toEqual(['2026-11-07'])
  })
})

describe('topicsWithMisses', () => {
  it('lists only topics where something was missed', () => {
    const elsewhere = {
      ...attempt('mcq-x', true, '2026-11-06'),
      topic_id: 'py.variables',
    }
    expect(
      topicsWithMisses([elsewhere, attempt('mcq-commas', false, '2026-11-06')]),
    ).toEqual([TOPIC])
  })
})

describe('chooseQuestion', () => {
  // The sample topic: every item tests 'print-text'. The worked example and
  // the build and debug exercises can never come back as follow-ups.
  const content = fakeContent()
  const topicId = content.topic.id
  const followUp: FollowUp = {
    topicId,
    skillId: 'print-text',
    missedOn: '2026-11-06',
    missedItems: ['mcq-print'],
    correctOn: [],
    due: '2026-11-07',
  }
  const answered = (item: string, day: string): Attempt => ({
    ...attempt(item, true, day),
    topic_id: topicId,
  })

  it('picks a different question, one never answered first', () => {
    // fill-hello, predict-print and write-hello are all fresh: the first by
    // name wins.
    expect(chooseQuestion(followUp, content, [])).toBe('fill-hello')
  })

  it('then the one answered longest ago', () => {
    const history = [
      answered('fill-hello', '2026-11-05'),
      answered('predict-print', '2026-11-03'),
      answered('write-hello', '2026-11-04'),
    ]
    expect(chooseQuestion(followUp, content, history)).toBe('predict-print')
  })

  it('never picks a proof check or the worked example', () => {
    const history = [
      answered('fill-hello', '2026-11-05'),
      answered('predict-print', '2026-11-05'),
      answered('write-hello', '2026-11-05'),
    ]
    expect(['fill-hello', 'predict-print', 'write-hello']).toContain(
      chooseQuestion(followUp, content, history),
    )
  })

  it('brings back the missed question only when nothing else tests the skill', () => {
    const onlyOne = fakeContent()
    for (const item of [
      ...Object.values(onlyOne.recall),
      ...Object.values(onlyOne.exercises),
    ]) {
      if (item.id !== 'mcq-print') item.skills = []
    }
    expect(chooseQuestion(followUp, onlyOne, [])).toBe('mcq-print')
  })
})

describe('skillsIn', () => {
  it('looks up the skills of questions and exercises in loaded topics', () => {
    const content = fakeContent()
    const lookUp = skillsIn(new Map([[content.topic.id, content]]))
    expect(lookUp(content.topic.id, 'mcq-print')).toEqual(['print-text'])
    expect(lookUp(content.topic.id, 'write-hello')).toEqual(['print-text'])
    expect(lookUp('py.nothing', 'mcq-print')).toEqual([])
  })
})

describe('days', () => {
  it('adds days across months and years', () => {
    expect(addDays('2026-11-30', 1)).toBe('2026-12-01')
    expect(addDays('2026-12-31', 1)).toBe('2027-01-01')
    expect(addDays('2026-11-06', 3)).toBe('2026-11-09')
  })

  it('names the local calendar day of a moment', () => {
    expect(dayOf(new Date(2026, 10, 6, 23, 59))).toBe('2026-11-06')
  })
})
