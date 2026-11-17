import { APP_NAME } from '../config.ts'
import { SESSION_MINUTES, type StudyPlan, WEEKDAYS } from './studyPlan.ts'

// The study plan as a calendar file (.ics, the iCalendar format of RFC 5545
// that Google Calendar, Outlook and Apple Calendar all import): one event
// that repeats every week on the chosen days at the chosen time. It's made
// in the browser and downloaded; no calendar service is asked for anything.
//
// The time is "floating": written without a time zone, so a calendar shows
// it at that time on the learner's own clock, wherever they are, which is
// what "I study at 7:30 pm" means.

/** Text as the format needs it: backslashes, commas, semicolons escaped. */
function escapeText(text: string): string {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\r?\n/g, '\\n')
}

/**
 * Lines longer than 75 characters are folded: broken, and the rest carried
 * on a line that starts with a space (RFC 5545, section 3.1). Counted in
 * characters, which is safe for the ASCII this mostly is; a long line of
 * accented text may fold a little early, which the format allows.
 */
function fold(line: string): string {
  const parts: string[] = []
  let rest = line
  while (rest.length > 74) {
    parts.push(rest.slice(0, 74))
    rest = rest.slice(74)
  }
  parts.push(rest)
  return parts.join('\r\n ')
}

const pad = (n: number) => String(n).padStart(2, '0')

/** "20261117T193000": a floating local date and time. */
function localStamp(date: Date): string {
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}T${pad(date.getHours())}${pad(date.getMinutes())}00`
}

/** "20261116T150000Z": a moment in UTC. */
function utcStamp(date: Date): string {
  return `${date.toISOString().slice(0, 19).replace(/[-:]/g, '')}Z`
}

/**
 * The first study session on or after `now`: the earliest chosen day at
 * the chosen time that hasn't passed yet. A repeating event starts on one
 * of its own days, as the format expects.
 */
export function firstSession(plan: StudyPlan, now: Date): Date {
  const [hours = 0, minutes = 0] = plan.time.split(':').map(Number)
  for (let ahead = 0; ahead < 8; ahead += 1) {
    const day = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate() + ahead,
      hours,
      minutes,
    )
    // getDay() counts from Sunday (0); WEEKDAYS starts on Monday.
    const weekday = WEEKDAYS[(day.getDay() + 6) % 7]
    if (plan.days.includes(weekday) && day >= now) return day
  }
  // Unreachable for a plan with at least one day.
  return now
}

/**
 * The calendar file's text. `title` is the event's name, `link` where it
 * sends the learner, and `uid` a name for the event no other will share.
 */
export function calendarFile(
  plan: StudyPlan,
  {
    now,
    title,
    link,
    uid,
  }: { now: Date; title: string; link: string; uid: string },
): string {
  const start = firstSession(plan, now)
  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    `PRODID:-//${APP_NAME}//Study plan//EN`,
    'CALSCALE:GREGORIAN',
    'BEGIN:VEVENT',
    `UID:${uid}`,
    `DTSTAMP:${utcStamp(now)}`,
    `DTSTART:${localStamp(start)}`,
    `DURATION:PT${SESSION_MINUTES}M`,
    `RRULE:FREQ=WEEKLY;BYDAY=${plan.days.join(',')}`,
    `SUMMARY:${escapeText(title)}`,
    ...(plan.place.trim() ? [`LOCATION:${escapeText(plan.place.trim())}`] : []),
    `DESCRIPTION:${escapeText(`Start today's session: ${link}`)}`,
    `URL:${link}`,
    'END:VEVENT',
    'END:VCALENDAR',
  ]
  // The format's lines end in CRLF, the last one included.
  return `${lines.map(fold).join('\r\n')}\r\n`
}
