import { describe, expect, it } from 'vitest'
import { fakeCheckpointContent, fakeContent } from '../test/fakeContent.tsx'
import {
  type Attempt,
  candidatesFor,
  chooseQuestion,
  type FollowUp,
  type ItemsOf,
  itemsIn,
  openFollowUps,
  planCards,
  type TopicItems,
  topicsToLoad,
} from './followUps.ts'

const TOPIC = 'py.values-and-types'

// The topic's items and the skills each tests, as a topic would declare
// them. A question has no stage; an exercise has one.
const ITEMS: TopicItems = {
  'mcq-commas': { skills: ['commas'] },
  'predict-commas': { skills: ['commas'] },
  'fill-commas': { skills: ['commas'], stage: 'fill_in' },
  'mcq-quotes': { skills: ['quotes'] },
  'write-card': { skills: ['quotes', 'blank-lines'], stage: 'write' },
  'build-banner': { skills: ['quotes'], stage: 'build' },
  'example-banner': { skills: ['quotes'], stage: 'worked_example' },
}
const itemsOf: ItemsOf = (topicId) => (topicId === TOPIC ? ITEMS : undefined)

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
  it("counts days on the learner's recorded day, not this device's", () => {
    // 06:30 UTC on 7 November was still 6 November in Los Angeles, where the
    // learner was. Whatever zone this device is in, the miss is on the 6th.
    const miss: Attempt = {
      id: 'attempt-recorded-day',
      type: 'answer',
      topic_id: TOPIC,
      item_id: 'mcq-commas',
      correct: false,
      occurred_at: '2026-11-07T06:30:00.000Z',
      local_day: '2026-11-06',
    }
    const [open] = openFollowUps([miss], itemsOf)
    expect(open?.missedOn).toBe('2026-11-06')
    expect(open?.due).toBe('2026-11-07')
  })

  it('opens a follow-up after a wrong answer, due the next day', () => {
    const open = openFollowUps(
      [attempt('mcq-commas', false, '2026-11-06')],
      itemsOf,
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
      itemsOf,
    )
    expect(open[0]).toMatchObject({ correctOn: [], due: '2026-11-07' })
  })

  it('comes back after 3 days, then 7, and closes after 3 correct days', () => {
    const history = [attempt('mcq-commas', false, '2026-11-06')]

    history.push(attempt('predict-commas', true, '2026-11-07'))
    expect(openFollowUps(history, itemsOf)[0]).toMatchObject({
      correctOn: ['2026-11-07'],
      due: '2026-11-10',
    })

    history.push(attempt('fill-commas', true, '2026-11-10'))
    expect(openFollowUps(history, itemsOf)[0]).toMatchObject({
      correctOn: ['2026-11-07', '2026-11-10'],
      due: '2026-11-17',
    })

    history.push(attempt('predict-commas', true, '2026-11-17'))
    expect(openFollowUps(history, itemsOf)).toEqual([])
  })

  it('counts a right day that comes later than due, and spaces from it', () => {
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06'),
        // Due on the 7th; the learner came back on the 9th.
        attempt('predict-commas', true, '2026-11-09'),
      ],
      itemsOf,
    )
    expect(open[0]).toMatchObject({
      correctOn: ['2026-11-09'],
      due: '2026-11-12',
    })
  })

  it("doesn't count a right day that comes before the follow-up is due", () => {
    // Right the next day (due again 3 days later), then right on each of
    // the two days in between: the gaps of 3 and 7 days are the point.
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06'),
        attempt('predict-commas', true, '2026-11-07'),
        attempt('predict-commas', true, '2026-11-08'),
        attempt('predict-commas', true, '2026-11-09'),
      ],
      itemsOf,
    )
    expect(open[0]).toMatchObject({
      correctOn: ['2026-11-07'],
      due: '2026-11-10',
    })
  })

  it("doesn't count the missed question, answered again from memory", () => {
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06'),
        attempt('mcq-commas', true, '2026-11-07'),
        attempt('mcq-commas', true, '2026-11-10'),
        attempt('mcq-commas', true, '2026-11-17'),
      ],
      itemsOf,
    )
    expect(open[0]).toMatchObject({ correctOn: [], due: '2026-11-07' })
  })

  it('counts a day with the missed question and a different one right', () => {
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06'),
        attempt('mcq-commas', true, '2026-11-07', 10),
        attempt('fill-commas', true, '2026-11-07', 11),
      ],
      itemsOf,
    )
    expect(open[0]?.correctOn).toEqual(['2026-11-07'])
  })

  it('counts the missed question when the skill has no other to ask', () => {
    // Both of the skill's questions missed on the same day: one of them has
    // to come back, and getting it right must count, or the follow-up could
    // never close.
    const twoOnly: TopicItems = {
      'mcq-commas': { skills: ['commas'] },
      'predict-commas': { skills: ['commas'] },
    }
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06'),
        attempt('predict-commas', false, '2026-11-06'),
        attempt('mcq-commas', true, '2026-11-07'),
      ],
      () => twoOnly,
    )
    expect(open[0]).toMatchObject({
      missedItems: ['mcq-commas', 'predict-commas'],
      correctOn: ['2026-11-07'],
    })
  })

  it('still needs the one question left when two of three were missed', () => {
    // A missed question counts only when every question on the skill was
    // missed; here fill-commas is still fresh.
    const missedTwo = [
      attempt('mcq-commas', false, '2026-11-06'),
      attempt('predict-commas', false, '2026-11-06'),
    ]
    const again = attempt('mcq-commas', true, '2026-11-07')
    expect(openFollowUps([...missedTwo, again], itemsOf)[0]?.correctOn).toEqual(
      [],
    )
    const fresh = attempt('fill-commas', true, '2026-11-07')
    expect(openFollowUps([...missedTwo, fresh], itemsOf)[0]?.correctOn).toEqual(
      ['2026-11-07'],
    )
  })

  it('learns nothing from a worked example, right or wrong', () => {
    // A worked example shows its answer as it goes (ADR-0011, amended
    // 2026-11-11). A lab walkthrough is Checked like any other exercise.
    expect(
      openFollowUps([attempt('example-banner', false, '2026-11-06')], itemsOf),
    ).toEqual([])
    const open = openFollowUps(
      [
        attempt('mcq-quotes', false, '2026-11-06'),
        attempt('example-banner', true, '2026-11-07'),
      ],
      itemsOf,
    )
    expect(open[0]).toMatchObject({ skillId: 'quotes', correctOn: [] })
  })

  it('starts over after another miss', () => {
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06'),
        attempt('predict-commas', true, '2026-11-07'),
        attempt('mcq-commas', false, '2026-11-10'),
      ],
      itemsOf,
    )
    expect(open[0]).toMatchObject({
      missedOn: '2026-11-10',
      correctOn: [],
      due: '2026-11-11',
    })
  })

  it('reopens a relearned skill that is missed again', () => {
    const relearned = [
      attempt('mcq-commas', false, '2026-11-06'),
      attempt('predict-commas', true, '2026-11-07'),
      attempt('fill-commas', true, '2026-11-10'),
      attempt('predict-commas', true, '2026-11-17'),
    ]
    expect(openFollowUps(relearned, itemsOf)).toEqual([])
    const open = openFollowUps(
      [...relearned, attempt('mcq-commas', false, '2026-12-01')],
      itemsOf,
    )
    expect(open[0]).toMatchObject({ missedOn: '2026-12-01' })
  })

  it("doesn't treat failing Checks as mistakes when the code passes that day", () => {
    const workedItOut = [
      attempt('write-card', false, '2026-11-06', 10),
      attempt('write-card', false, '2026-11-06', 11),
      attempt('write-card', true, '2026-11-06', 12),
    ]
    expect(openFollowUps(workedItOut, itemsOf)).toEqual([])

    const neverPassed = [attempt('write-card', false, '2026-11-06')]
    expect(skills(openFollowUps(neverPassed, itemsOf))).toEqual([
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
      itemsOf,
    )
    expect(skills(open)).toEqual(['quotes'])
  })

  it('opens a follow-up for every skill a missed item tests', () => {
    const open = openFollowUps(
      [attempt('write-card', false, '2026-11-06')],
      itemsOf,
    )
    expect(skills(open)).toEqual(['blank-lines', 'quotes'])
  })

  it('counts proof checks as misses too', () => {
    const open = openFollowUps(
      [attempt('build-banner', false, '2026-11-06')],
      itemsOf,
    )
    expect(skills(open)).toEqual(['quotes'])
  })

  it('ignores items that no longer exist or test no skill', () => {
    expect(
      openFollowUps([attempt('mcq-gone', false, '2026-11-06')], itemsOf),
    ).toEqual([])
    // Not an item at all, though every object has it.
    expect(
      openFollowUps([attempt('constructor', false, '2026-11-06')], itemsOf),
    ).toEqual([])
  })

  it('gives the same result whatever order the history arrives in', () => {
    const history = [
      attempt('mcq-commas', false, '2026-11-06'),
      attempt('predict-commas', true, '2026-11-07'),
      attempt('mcq-quotes', false, '2026-11-08'),
      attempt('fill-commas', true, '2026-11-10'),
    ]
    expect(openFollowUps([...history].reverse(), itemsOf)).toEqual(
      openFollowUps(history, itemsOf),
    )
  })

  it("uses the learner's own calendar days", () => {
    // 11:30 pm and half past midnight are different days, wherever you are.
    const open = openFollowUps(
      [
        attempt('mcq-commas', false, '2026-11-06', 23),
        attempt('predict-commas', true, '2026-11-07', 0),
      ],
      itemsOf,
    )
    expect(open[0]?.correctOn).toEqual(['2026-11-07'])
  })
})

describe('candidatesFor', () => {
  it('lists the questions, fill-ins, writes and reviews on a skill', () => {
    expect(candidatesFor(ITEMS, 'quotes')).toEqual(['mcq-quotes', 'write-card'])
    expect(candidatesFor(ITEMS, 'commas')).toEqual([
      'fill-commas',
      'mcq-commas',
      'predict-commas',
    ])
    expect(candidatesFor(undefined, 'quotes')).toEqual([])
  })
})

describe('topicsToLoad', () => {
  it('names each topic of the follow-ups once', () => {
    const followUp = (topicId: string, skillId: string): FollowUp => ({
      topicId,
      skillId,
      missedOn: '2026-11-06',
      missedItems: [],
      correctOn: [],
      due: '2026-11-07',
    })
    expect(
      topicsToLoad([
        followUp('py.variables', 'names'),
        followUp(TOPIC, 'commas'),
        followUp('py.variables', 'assign'),
      ]),
    ).toEqual(['py.values-and-types', 'py.variables'])
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

describe('planCards', () => {
  /** The sample topic, with each item testing the skills given. */
  function topicWith(skillsByItem: Record<string, string[]>) {
    const content = fakeContent()
    for (const item of [
      ...Object.values(content.recall),
      ...Object.values(content.exercises),
    ]) {
      item.skills = skillsByItem[item.id] ?? []
    }
    return content
  }

  function due(content: ReturnType<typeof fakeContent>, skillIds: string[]) {
    const missed = attempt('write-hello', false, '2026-11-06')
    const attempts = [{ ...missed, topic_id: content.topic.id }]
    const contents = new Map([[content.topic.id, content]])
    const open = openFollowUps(attempts, itemsIn(contents)).filter((followUp) =>
      skillIds.includes(followUp.skillId),
    )
    return planCards(open, contents, attempts)
  }

  it('gives each skill a different question when one miss opens several', () => {
    const content = topicWith({
      'write-hello': ['a', 'b'],
      'mcq-print': ['a'],
      'predict-print': ['a', 'b'],
      'fill-hello': ['b'],
    })
    const cards = due(content, ['a', 'b'])
    expect(cards.map((card) => card.itemId)).toEqual([
      'mcq-print',
      'fill-hello',
    ])
  })

  it('asks a shared question once when a skill has no other left', () => {
    const content = topicWith({
      'write-hello': ['a', 'b'],
      'mcq-print': ['a', 'b'],
      'predict-print': ['a'],
    })
    const cards = due(content, ['a', 'b'])
    expect(cards).toHaveLength(1)
    expect(cards[0]?.itemId).toBe('mcq-print')
    expect(cards[0]?.followUps.map((followUp) => followUp.skillId)).toEqual([
      'a',
      'b',
    ])
  })
})

describe('itemsIn', () => {
  it('looks up the questions and exercises of loaded topics', () => {
    const content = fakeContent()
    const items = itemsIn(new Map([[content.topic.id, content]]))
    expect(items(content.topic.id)?.['mcq-print']?.skills).toEqual([
      'print-text',
    ])
    expect(items(content.topic.id)?.['write-hello']).toMatchObject({
      skills: ['print-text'],
      stage: 'write',
    })
    expect(items('py.nothing')).toBeUndefined()
  })
})

describe('checkpoint tests (ADR-0012)', () => {
  const CHECKPOINT = 'py.m1.checkpoint'
  const STRINGS = 'py.strings-and-input'
  // Test -> the skills it checks, as a checkpoint's exercise.yaml names them.
  const RECEIPT: Record<string, string[]> = {
    test_subtotal: [`${STRINGS}/convert`],
    test_tip: ['py.arithmetic/precedence', `${STRINGS}/convert`],
    test_format: [`${STRINGS}/fstrings`],
  }
  const BY_TOPIC: Record<string, TopicItems> = {
    [CHECKPOINT]: {
      'build-receipt': { skills: [], stage: 'build', test_skills: RECEIPT },
      // A fresh version of the build: the same tests, another story.
      'build-fuel': { skills: [], stage: 'build', test_skills: RECEIPT },
    },
    // The skill's own topic, with questions of its own.
    [STRINGS]: {
      'mcq-fstrings': { skills: ['fstrings'] },
      'fill-fstrings': { skills: ['fstrings'], stage: 'fill_in' },
    },
  }
  const items: ItemsOf = (topicId) => BY_TOPIC[topicId]

  /** A Check that failed `failing`; undefined if the tests couldn't run. */
  function check(
    failing: string[] | undefined,
    day: string,
    hour = 10,
    item = 'build-receipt',
  ) {
    return {
      ...attempt(item, failing?.length === 0, day, hour),
      topic_id: CHECKPOINT,
      failing,
    }
  }
  const open = (history: Attempt[]) => openFollowUps(history, items)
  const names = (followUps: FollowUp[]) =>
    followUps.map((followUp) => `${followUp.topicId}/${followUp.skillId}`)

  it('brings back the skills a failed test names, from their own topics', () => {
    const followUps = open([check(['test_tip'], '2026-11-06')])
    expect(names(followUps)).toEqual([
      'py.arithmetic/precedence',
      'py.strings-and-input/convert',
    ])
    expect(followUps[0]).toMatchObject({
      missedOn: '2026-11-06',
      due: '2026-11-07',
      // In full, so it can't be mistaken for a question in py.arithmetic.
      missedItems: ['py.m1.checkpoint/build-receipt'],
    })
  })

  it("doesn't count a test that a later Check passed that day", () => {
    const history = [
      check(['test_tip', 'test_format'], '2026-11-06', 10),
      check(['test_format'], '2026-11-06', 11),
    ]
    expect(names(open(history))).toEqual(['py.strings-and-input/fstrings'])
  })

  it("learns nothing from a Check whose tests couldn't run", () => {
    expect(open([check(undefined, '2026-11-06')])).toEqual([])
  })

  it("counts a passed test of a fresh version, not the same build's", () => {
    const missed = check(['test_format'], '2026-11-06')
    // The same build passing the next day is the learner's own fix, seen
    // before: the skill's topic has questions of its own to ask.
    expect(open([missed, check([], '2026-11-07')])[0]?.correctOn).toEqual([])
    expect(open([missed, check([], '2026-11-07', 10, 'build-fuel')])).toEqual([
      expect.objectContaining({
        skillId: 'fstrings',
        correctOn: ['2026-11-07'],
        due: '2026-11-10',
      }),
    ])
  })

  it("counts the skill's own questions in its topic", () => {
    const answer: Attempt = {
      ...attempt('mcq-fstrings', true, '2026-11-07'),
      topic_id: STRINGS,
    }
    expect(open([check(['test_format'], '2026-11-06'), answer])).toEqual([
      expect.objectContaining({
        skillId: 'fstrings',
        correctOn: ['2026-11-07'],
      }),
    ])
  })

  it("reads a further part's tests the same way, whatever slot names it", () => {
    // A checkpoint's further part (prove.more, ADR-0012 amended 2026-11-11)
    // is one more exercise with test_skills, here a lab's, by check id.
    // Follow-ups look tests up by exercise and never ask which slot of
    // prove names it, so nothing about them changes for parts.
    const withPart: ItemsOf = (topicId) =>
      topicId === CHECKPOINT
        ? {
            ...BY_TOPIC[CHECKPOINT],
            'build-domain': {
              skills: [],
              stage: 'build',
              test_skills: { 'names-the-domain': [`${STRINGS}/fstrings`] },
            },
          }
        : BY_TOPIC[topicId]
    const missed = check(['names-the-domain'], '2026-11-06', 10, 'build-domain')
    expect(openFollowUps([missed], withPart)).toEqual([
      expect.objectContaining({
        topicId: STRINGS,
        skillId: 'fstrings',
        missedItems: ['py.m1.checkpoint/build-domain'],
      }),
    ])
  })

  it('looks up test skills in loaded content', () => {
    const checkpoint = fakeCheckpointContent()
    const contents = new Map([[checkpoint.topic.id, checkpoint]])
    expect(
      itemsIn(contents)(CHECKPOINT)?.['build-receipt']?.test_skills,
    ).toEqual({
      test_total: ['py.arithmetic/operators'],
      test_format: ['py.strings-and-input/fstrings'],
    })
  })
})

describe('placement answers', () => {
  it('open no follow-up (ADR-0021)', () => {
    const miss: Attempt = {
      ...attempt('mcq-commas', false, '2026-11-06'),
      context: 'placement',
    }
    expect(openFollowUps([miss], itemsOf)).toEqual([])
  })
})
