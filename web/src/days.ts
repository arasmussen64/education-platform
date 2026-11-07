// Calendar days in the learner's own time zone. Mistakes coming back
// (ADR-0011) and the data export's file name count in these.

/** A calendar day in the learner's own time zone, like "2026-11-06". */
export type Day = string

export function dayOf(time: string | number | Date): Day {
  const date = new Date(time)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

export function addDays(day: Day, days: number): Day {
  const [year = 0, month = 1, date = 1] = day.split('-').map(Number)
  // Noon, so a daylight-saving change can't tip it into another day.
  return dayOf(new Date(year, month - 1, date + days, 12))
}
