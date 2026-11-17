// "When and where will you study?" A plan of the form "on these days, at
// this time, in this place, I'll study" makes following through far more
// likely than an intention alone (implementation intentions; Gollwitzer and
// Sheeran, 2006). The Today page asks once and shows the plan back as a
// one-line reminder, and the learner can put it in their own calendar.
//
// Kept on this device only, in localStorage: it's a convenience, not a
// record, and saving it with the learner's account would need a new table
// or event type, which is a database change for the owner to decide. The
// page works the same when storage is empty, full or blocked.

/** The days of the week as the calendar format names them, Monday first. */
export const WEEKDAYS = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] as const
export type Weekday = (typeof WEEKDAYS)[number]

export const WEEKDAY_NAMES: Record<Weekday, string> = {
  MO: 'Monday',
  TU: 'Tuesday',
  WE: 'Wednesday',
  TH: 'Thursday',
  FR: 'Friday',
  SA: 'Saturday',
  SU: 'Sunday',
}

export type StudyPlan = {
  /** The days, in week order, Monday first. */
  days: Weekday[]
  /** The time of day, "19:30", on the learner's own clock. */
  time: string
  /** Where, in the learner's words; may be empty. */
  place: string
}

/** How long the calendar event lasts. */
export const SESSION_MINUTES = 30

const PLAN_KEY = 'study-plan'
const DISMISSED_KEY = 'study-plan-dismissed'

type PlanStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>

function defaultStorage(): PlanStorage | null {
  try {
    return typeof localStorage === 'undefined' ? null : localStorage
  } catch {
    return null
  }
}

const TIME = /^([01]\d|2[0-3]):[0-5]\d$/

/** A plan read back from storage, if it is one; anything else is ignored. */
function parsePlan(text: string | null): StudyPlan | null {
  if (!text) return null
  try {
    const value: unknown = JSON.parse(text)
    if (typeof value !== 'object' || value === null) return null
    const { days, time, place } = value as Record<string, unknown>
    if (!Array.isArray(days) || typeof time !== 'string') return null
    const known = WEEKDAYS.filter((day) => days.includes(day))
    if (known.length === 0 || !TIME.test(time)) return null
    return { days: known, time, place: typeof place === 'string' ? place : '' }
  } catch {
    return null
  }
}

/** The plan saved on this device, if any. */
export function loadStudyPlan(
  storage: PlanStorage | null = defaultStorage(),
): StudyPlan | null {
  try {
    return parsePlan(storage?.getItem(PLAN_KEY) ?? null)
  } catch {
    return null
  }
}

/** Saves the plan on this device. False if it couldn't be saved. */
export function saveStudyPlan(
  plan: StudyPlan,
  storage: PlanStorage | null = defaultStorage(),
): boolean {
  try {
    if (!storage) return false
    storage.setItem(PLAN_KEY, JSON.stringify(plan))
    return true
  } catch {
    return false
  }
}

/** Forgets the plan on this device. */
export function clearStudyPlan(
  storage: PlanStorage | null = defaultStorage(),
): void {
  try {
    storage?.removeItem(PLAN_KEY)
  } catch {
    // Blocked storage: nothing was saved to forget.
  }
}

/** Whether the learner said "Not now" to the question on this device. */
export function wasDismissed(
  storage: PlanStorage | null = defaultStorage(),
): boolean {
  try {
    return storage?.getItem(DISMISSED_KEY) === 'yes'
  } catch {
    return false
  }
}

/** Remembers "Not now", so the Today page asks only once. */
export function dismiss(storage: PlanStorage | null = defaultStorage()): void {
  try {
    storage?.setItem(DISMISSED_KEY, 'yes')
  } catch {
    // Not remembered: the question shows again next time, which is harmless.
  }
}

/**
 * "7:30 pm", from "19:30". Written out by hand: browsers differ in the
 * space they put before "PM", and this reads the same everywhere.
 */
export function formatTime(time: string): string {
  const [hours = 0, minutes = 0] = time.split(':').map(Number)
  const hour = hours % 12 === 0 ? 12 : hours % 12
  return `${hour}:${String(minutes).padStart(2, '0')} ${hours < 12 ? 'am' : 'pm'}`
}

/** "Monday", "Monday and Thursday", "Monday, Wednesday and Friday", "every day". */
export function formatDays(days: Weekday[]): string {
  if (days.length === 7) return 'every day'
  const names = days.map((day) => WEEKDAY_NAMES[day])
  if (names.length === 1) return names[0]
  return `${names.slice(0, -1).join(', ')} and ${names.at(-1)}`
}

/**
 * The place, ready to follow a time: ", at the library" for "the library",
 * ", in the kitchen" for "in the kitchen" (it has its own word), or nothing.
 */
export function wherePart(place: string): string {
  const trimmed = place.trim().replace(/[.\s]+$/, '')
  if (!trimmed) return ''
  return /^(at|in|on) /i.test(trimmed) ? `, ${trimmed}` : `, at ${trimmed}`
}

/** The plan as one line: "Monday and Thursday at 7:30 pm, at the library." */
export function describePlan(plan: StudyPlan): string {
  return `${formatDays(plan.days)} at ${formatTime(plan.time)}${wherePart(plan.place)}.`
}
