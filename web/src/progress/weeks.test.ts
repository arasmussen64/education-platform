import { describe, expect, it } from 'vitest'
import type { Attempt } from '../followups/followUps.ts'
import { describeWeeks, weeksPractised } from './weeks.ts'

// Every test passes "today" itself, and every attempt carries the learner's
// own day (local_day), so nothing here depends on the clock or time zone.
const TODAY = '2026-11-16'

let lastId = 0
/** An answer on the learner's day `day`, at noon UTC that day. */
function on(day: string, overrides: Partial<Attempt> = {}): Attempt {
  return {
    id: `a${++lastId}`,
    type: 'answer',
    topic_id: 'py.programs-and-print',
    item_id: 'mcq',
    correct: true,
    occurred_at: `${day}T12:00:00.000Z`,
    local_day: day,
    ...overrides,
  }
}

describe('weeksPractised', () => {
  it('is null with no practice at all', () => {
    expect(weeksPractised([], TODAY)).toBeNull()
  })

  it('counts rolling weeks of seven days ending today', () => {
    const result = weeksPractised(
      [
        on('2026-11-16'), // today: this week
        on('2026-11-10'), // 6 days ago: still this week
        on('2026-11-09'), // 7 days ago: the week before
        // Nothing 14 to 20 days ago.
        on('2026-10-19'), // 28 days ago: the fifth week back
      ],
      TODAY,
    )
    expect(result).toEqual({
      practised: 3,
      weeks: 5,
      byWeek: [true, true, false, false, true],
    })
  })

  it('ignores practice older than the weeks counted, but not for how long the learner has been here', () => {
    // Started long ago, then only this week.
    const result = weeksPractised([on('2026-01-05'), on('2026-11-15')], TODAY)
    expect(result).toEqual({
      practised: 1,
      weeks: 5,
      byWeek: [true, false, false, false, false],
    })
  })

  it("counts only the weeks since a new learner's first practice", () => {
    // First practice 10 days ago: two weeks so far, both with practice.
    expect(weeksPractised([on('2026-11-06'), on('2026-11-14')], TODAY)).toEqual(
      { practised: 2, weeks: 2, byWeek: [true, true] },
    )
  })

  it("uses the learner's own recorded day, not the UTC date", () => {
    // 03:00 UTC on the 10th was still the 9th where the learner was: 7 days
    // ago, so the week before this one.
    const late = on('2026-11-09', { occurred_at: '2026-11-10T03:00:00.000Z' })
    expect(weeksPractised([late, on('2026-11-16')], TODAY)?.byWeek).toEqual([
      true,
      true,
    ])
  })

  it("doesn't count the placement test as practice", () => {
    expect(
      weeksPractised([on('2026-11-16', { context: 'placement' })], TODAY),
    ).toBeNull()
  })

  it("counts an event dated after today (a fast clock) as today's", () => {
    expect(weeksPractised([on('2026-11-17')], TODAY)).toEqual({
      practised: 1,
      weeks: 1,
      byWeek: [true],
    })
  })
})

describe('describeWeeks', () => {
  it('says how many of the weeks had practice', () => {
    expect(
      describeWeeks({
        practised: 4,
        weeks: 5,
        byWeek: [true, true, false, true, true],
      }),
    ).toEqual({
      summary: 'You practised in 4 of the last 5 weeks.',
      note: null,
    })
  })

  it('says "each" when every week had practice', () => {
    expect(
      describeWeeks({ practised: 3, weeks: 3, byWeek: [true, true, true] })
        .summary,
    ).toBe('You practised in each of the last 3 weeks.')
  })

  it('speaks of this week alone for a learner in their first week', () => {
    expect(
      describeWeeks({ practised: 1, weeks: 1, byWeek: [true] }).summary,
    ).toBe("You've practised this week.")
  })

  it('notes, without warning, that today counts when this week is empty', () => {
    expect(
      describeWeeks({
        practised: 2,
        weeks: 5,
        byWeek: [false, true, true, false, false],
      }).note,
    ).toBe('A session today counts for this week.')
  })
})
