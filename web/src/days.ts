// Calendar days in the learner's own time zone. Mistakes coming back
// (ADR-0011) and the data export's file name count in these.
//
// An event's time is saved in UTC, which is the same everywhere, but a
// learner's day depends on where they are: 22:30 on Friday in Los Angeles is
// already Saturday in UTC. So since 2026-11-11 every event also records the
// learner's own calendar day and how far their clock was from UTC
// (ADR-0008). An event's day is then the same on any device, in any zone.

/** A calendar day in the learner's own time zone, like "2026-11-06". */
export type Day = string

/** What dayOf needs from an event. */
export type EventTime = {
  /** When it happened, in ISO format. */
  occurred_at: string
  /**
   * The learner's calendar day then, as recorded with the event. Events from
   * before 2026-11-11 don't have it.
   */
  local_day?: unknown
}

const MINUTE_MS = 60 * 1000
const DAY_MINUTES = 24 * 60

/**
 * The calendar day of a time on this device's clock, or of an event.
 *
 * For an event, it's the day the learner recorded with it, whichever device
 * is showing it now. An event without one (from before 2026-11-11), or with
 * one that can't be right, falls back to this device's clock.
 */
export function dayOf(time: string | number | Date | EventTime): Day {
  if (typeof time === 'object' && !(time instanceof Date)) {
    return recordedDay(time) ?? deviceDay(time.occurred_at)
  }
  return deviceDay(time)
}

/** The day of a moment on this device's clock, in its time zone. */
function deviceDay(time: string | number | Date): Day {
  const date = new Date(time)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

/** The day recorded with an event, if it has one that could be right. */
function recordedDay(event: EventTime): Day | undefined {
  const day = event.local_day
  const time = Date.parse(event.occurred_at)
  if (typeof day !== 'string' || Number.isNaN(time)) return undefined
  // Clocks run from 12 hours behind UTC to 14 ahead, so the learner's day is
  // the UTC day or one either side of it. Anything else is damaged.
  const possible = [-1, 0, 1].map((days) =>
    dayAtOffset(time, days * DAY_MINUTES),
  )
  return possible.includes(day) ? day : undefined
}

/**
 * How many minutes this device's clock is ahead of UTC at `time`: -480 in
 * Los Angeles in winter (UTC-8), 330 in India (UTC+5:30), 0 in London in
 * winter. Recorded with every event.
 */
export function utcOffsetMinutes(time: number): number {
  // getTimezoneOffset counts the other way, in minutes behind UTC.
  const behind = new Date(time).getTimezoneOffset()
  // In UTC itself, -behind would be -0, which prints as 0 but isn't quite.
  return behind === 0 ? 0 : -behind
}

/** The calendar day at `time` on a clock `offsetMinutes` ahead of UTC. */
export function dayAtOffset(time: number, offsetMinutes: number): Day {
  // Move the moment by the offset, then read its date in UTC.
  return new Date(time + offsetMinutes * MINUTE_MS).toISOString().slice(0, 10)
}

export function addDays(day: Day, days: number): Day {
  const [year = 0, month = 1, date = 1] = day.split('-').map(Number)
  // Noon, so a daylight-saving change can't tip it into another day.
  return dayOf(new Date(year, month - 1, date + days, 12))
}
