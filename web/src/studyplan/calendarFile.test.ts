import { describe, expect, it } from 'vitest'
import { APP_NAME } from '../config.ts'
import { calendarFile, firstSession } from './calendarFile.ts'
import type { StudyPlan } from './studyPlan.ts'

// Local times on this machine's clock: new Date(y, m, d, h, min) is local,
// and the calendar file's times are local ("floating") too. 16 November
// 2026 is a Monday.
const MONDAY_3PM = new Date(2026, 10, 16, 15, 0)
const PLAN: StudyPlan = {
  days: ['MO', 'TH'],
  time: '19:30',
  place: 'the library, upstairs; by the window',
}

function file(plan = PLAN, now = MONDAY_3PM) {
  return calendarFile(plan, {
    now,
    title: `${APP_NAME} study session`,
    link: 'https://example.org/session',
    uid: 'test-uid@study-plan',
  })
}

/** The file's lines, with folded lines joined back up. */
const lines = (text: string) => text.replace(/\r\n /g, '').split('\r\n')

describe('firstSession', () => {
  it('is later today when today is a study day and the time is still ahead', () => {
    expect(firstSession(PLAN, MONDAY_3PM)).toEqual(
      new Date(2026, 10, 16, 19, 30),
    )
  })

  it('is the next study day once today’s time has passed', () => {
    expect(firstSession(PLAN, new Date(2026, 10, 16, 20, 0))).toEqual(
      new Date(2026, 10, 19, 19, 30),
    )
  })

  it('can be almost a week away', () => {
    expect(
      firstSession({ ...PLAN, days: ['MO'] }, new Date(2026, 10, 16, 20, 0)),
    ).toEqual(new Date(2026, 10, 23, 19, 30))
  })
})

describe('calendarFile', () => {
  it('is one weekly event on the chosen days, at the chosen local time', () => {
    const text = file()
    expect(lines(text)).toEqual([
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      `PRODID:-//${APP_NAME}//Study plan//EN`,
      'CALSCALE:GREGORIAN',
      'BEGIN:VEVENT',
      'UID:test-uid@study-plan',
      `DTSTAMP:${MONDAY_3PM.toISOString().slice(0, 19).replace(/[-:]/g, '')}Z`,
      'DTSTART:20261116T193000',
      'DURATION:PT30M',
      'RRULE:FREQ=WEEKLY;BYDAY=MO,TH',
      `SUMMARY:${APP_NAME} study session`,
      // Commas and semicolons in the learner's words are escaped.
      'LOCATION:the library\\, upstairs\\; by the window',
      "DESCRIPTION:Start today's session: https://example.org/session",
      'URL:https://example.org/session',
      'END:VEVENT',
      'END:VCALENDAR',
      '',
    ])
  })

  it('ends every line with CRLF and folds long ones at 75 characters', () => {
    const text = file({ ...PLAN, place: 'x'.repeat(200) })
    expect(text.endsWith('\r\n')).toBe(true)
    expect(text.replace(/\r\n/g, '')).not.toMatch(/[\r\n]/)
    for (const line of text.split('\r\n')) {
      expect(line.length).toBeLessThanOrEqual(75)
    }
    expect(lines(text)).toContain(`LOCATION:${'x'.repeat(200)}`)
  })

  it('leaves the place out when there is none', () => {
    expect(file({ ...PLAN, place: ' ' })).not.toContain('LOCATION')
  })
})
