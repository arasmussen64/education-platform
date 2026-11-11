import { describe, expect, it } from 'vitest'
import { addDays, dayAtOffset, dayOf, utcOffsetMinutes } from './days.ts'

/**
 * Runs `check` with this device's clock in another time zone, then puts the
 * zone back. Node changes zone as soon as TZ is set.
 */
function inZone(zone: string, check: () => void) {
  const before = Intl.DateTimeFormat().resolvedOptions().timeZone
  process.env.TZ = zone
  try {
    check()
  } finally {
    process.env.TZ = before
  }
}

const HOUR_MINUTES = 60
/** 22:30 on 6 November in Los Angeles; 15:30 on the 7th in Tokyo. */
const EVENING_IN_LA = '2026-11-07T06:30:00.000Z'

describe('days', () => {
  it('adds days across months and years', () => {
    expect(addDays('2026-11-30', 1)).toBe('2026-12-01')
    expect(addDays('2026-12-31', 1)).toBe('2027-01-01')
    expect(addDays('2026-11-06', 3)).toBe('2026-11-09')
  })

  it('names the local calendar day of a moment', () => {
    expect(dayOf(new Date(2026, 10, 6, 23, 59))).toBe('2026-11-06')
  })

  it("names a time's day on this device's clock", () => {
    inZone('America/Los_Angeles', () => {
      expect(dayOf(EVENING_IN_LA)).toBe('2026-11-06')
    })
    inZone('Asia/Tokyo', () => {
      expect(dayOf(EVENING_IN_LA)).toBe('2026-11-07')
    })
  })
})

describe('the day of an event', () => {
  it("is the learner's own day, recorded with it, on a device in any zone", () => {
    const event = { occurred_at: EVENING_IN_LA, local_day: '2026-11-06' }
    for (const zone of ['America/Los_Angeles', 'UTC', 'Asia/Tokyo']) {
      inZone(zone, () => expect(dayOf(event)).toBe('2026-11-06'))
    }
  })

  it("is this device's day for an event from before days were recorded", () => {
    const event = { occurred_at: EVENING_IN_LA }
    inZone('America/Los_Angeles', () => {
      expect(dayOf(event)).toBe('2026-11-06')
    })
    inZone('Asia/Tokyo', () => {
      expect(dayOf(event)).toBe('2026-11-07')
    })
  })

  it.each([
    ['a word', 'yesterday'],
    ['a number', 20261106],
    ['nothing', null],
    ['a day two weeks away', '2026-11-20'],
    ['a day two days back', '2026-11-05'],
  ])(
    "uses this device's day when the recorded one can't be right: %s",
    (_what, localDay) => {
      inZone('UTC', () => {
        expect(dayOf({ occurred_at: EVENING_IN_LA, local_day: localDay })).toBe(
          '2026-11-07',
        )
      })
    },
  )

  it('keeps each day as the learner lived it when their device changes zone', () => {
    // 23:30 in New York (UTC-5) on the 6th, recorded there...
    const lateInNewYork = Date.parse('2026-11-07T04:30:00.000Z')
    // ...then the device is set to Tokyo (UTC+9), where it's the 7th.
    const inTokyo = Date.parse('2026-11-07T05:30:00.000Z')
    const events = [
      { at: lateInNewYork, offset: -5 * HOUR_MINUTES },
      { at: inTokyo, offset: 9 * HOUR_MINUTES },
    ].map(({ at, offset }) => ({
      occurred_at: new Date(at).toISOString(),
      local_day: dayAtOffset(at, offset),
    }))

    // Viewed later in Los Angeles, where both times fall on the 6th.
    inZone('America/Los_Angeles', () => {
      expect(events.map((event) => dayOf(event))).toEqual([
        '2026-11-06',
        '2026-11-07',
      ])
      expect(events.map((event) => dayOf(event.occurred_at))).toEqual([
        '2026-11-06',
        '2026-11-06',
      ])
    })
  })
})

describe('what is recorded about the time zone', () => {
  it("counts this device's offset in minutes ahead of UTC", () => {
    const november = Date.parse(EVENING_IN_LA)
    const july = Date.parse('2026-07-01T12:00:00.000Z')
    inZone('America/Los_Angeles', () => {
      expect(utcOffsetMinutes(november)).toBe(-8 * HOUR_MINUTES)
      // Summer time.
      expect(utcOffsetMinutes(july)).toBe(-7 * HOUR_MINUTES)
    })
    inZone('Asia/Kolkata', () => {
      expect(utcOffsetMinutes(november)).toBe(5.5 * HOUR_MINUTES)
    })
    inZone('UTC', () => {
      // Plain 0, not -0, so it reads and compares as 0.
      expect(Object.is(utcOffsetMinutes(november), 0)).toBe(true)
    })
  })

  it('gives the day on a clock that many minutes ahead of UTC', () => {
    const at = Date.parse(EVENING_IN_LA)
    expect(dayAtOffset(at, -8 * HOUR_MINUTES)).toBe('2026-11-06')
    expect(dayAtOffset(at, 9 * HOUR_MINUTES)).toBe('2026-11-07')
    // The zones furthest from UTC: 14 hours ahead and 12 behind.
    expect(dayAtOffset(Date.parse('2026-11-06T10:30:00Z'), 14 * 60)).toBe(
      '2026-11-07',
    )
    expect(dayAtOffset(Date.parse('2026-11-06T11:30:00Z'), -12 * 60)).toBe(
      '2026-11-05',
    )
  })

  it("agrees with this device's own day, around midnight too", () => {
    inZone('America/Los_Angeles', () => {
      for (const time of [
        '2026-11-07T07:59:00.000Z',
        '2026-11-07T08:00:00.000Z',
        '2026-03-08T09:59:00.000Z',
        '2026-03-08T10:00:00.000Z',
      ]) {
        const at = Date.parse(time)
        expect(dayAtOffset(at, utcOffsetMinutes(at))).toBe(dayOf(at))
      }
    })
  })
})
