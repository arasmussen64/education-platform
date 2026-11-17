import { useId, useState } from 'react'
import { BUTTON, SECONDARY_BUTTON, TEXT_INPUT } from '../components/styles.ts'
import { APP_NAME } from '../config.ts'
import { downloadText } from '../export/download.ts'
import { calendarFile } from './calendarFile.ts'
import {
  type StudyPlan,
  WEEKDAY_NAMES,
  WEEKDAYS,
  type Weekday,
} from './studyPlan.ts'

// The form that asks "When and where will you study?", and the button that
// turns the answer into a calendar file. Used on the Today page and the
// Account page (studyplan/StudyPlanParts.tsx).

/** The time a new plan starts at, before the learner picks one. */
const DEFAULT_TIME = '19:00'

export function StudyPlanForm({
  initial,
  onSave,
  onCancel,
  cancelLabel,
}: {
  initial: StudyPlan | null
  onSave: (plan: StudyPlan) => void
  onCancel?: () => void
  cancelLabel?: string
}) {
  const id = useId()
  const [days, setDays] = useState<Weekday[]>(initial?.days ?? [])
  const [time, setTime] = useState(initial?.time ?? DEFAULT_TIME)
  const [place, setPlace] = useState(initial?.place ?? '')
  const [problem, setProblem] = useState('')

  function toggle(day: Weekday) {
    setDays((chosen) =>
      chosen.includes(day)
        ? chosen.filter((each) => each !== day)
        : WEEKDAYS.filter((each) => each === day || chosen.includes(each)),
    )
  }

  function submit(event: React.FormEvent) {
    event.preventDefault()
    if (days.length === 0) {
      setProblem('Pick at least one day.')
      return
    }
    if (!/^\d\d:\d\d$/.test(time)) {
      setProblem('Pick a time.')
      return
    }
    setProblem('')
    onSave({ days, time, place: place.trim() })
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <fieldset className="space-y-1">
        <legend className="text-sm font-medium">Days</legend>
        <div className="flex flex-wrap gap-x-4 gap-y-1">
          {WEEKDAYS.map((day) => (
            <label key={day} className="flex items-center gap-1.5 text-sm">
              <input
                type="checkbox"
                checked={days.includes(day)}
                onChange={() => toggle(day)}
              />
              {WEEKDAY_NAMES[day]}
            </label>
          ))}
        </div>
      </fieldset>
      <div className="flex flex-wrap gap-4">
        <label htmlFor={`${id}-time`} className="block text-sm font-medium">
          Time
          <input
            id={`${id}-time`}
            type="time"
            value={time}
            onChange={(event) => setTime(event.target.value)}
            className={TEXT_INPUT}
          />
        </label>
        <label
          htmlFor={`${id}-place`}
          className="block min-w-48 flex-1 text-sm font-medium"
        >
          Where (optional)
          <input
            id={`${id}-place`}
            type="text"
            value={place}
            maxLength={100}
            placeholder="the kitchen table"
            onChange={(event) => setPlace(event.target.value)}
            className={TEXT_INPUT}
          />
        </label>
      </div>
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block text-sm font-medium">{problem}</output>
      <div className="flex flex-wrap gap-3">
        <button type="submit" className={BUTTON}>
          Save my plan
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} className={SECONDARY_BUTTON}>
            {cancelLabel ?? 'Cancel'}
          </button>
        )}
      </div>
    </form>
  )
}

/** A name for one calendar event that no other event will share. */
function eventId(): string {
  const random =
    typeof crypto !== 'undefined' && 'randomUUID' in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2)}`
  return `${random}@study-plan`
}

/** Downloads the plan as a weekly calendar event (studyplan/calendarFile.ts). */
export function CalendarButton({ plan }: { plan: StudyPlan }) {
  function download() {
    const text = calendarFile(plan, {
      now: new Date(),
      title: `${APP_NAME} study session`,
      link: `${window.location.origin}/session`,
      uid: eventId(),
    })
    downloadText('study-plan.ics', text, 'text/calendar')
  }
  return (
    <button type="button" onClick={download} className={SECONDARY_BUTTON}>
      Add to my calendar (.ics)
    </button>
  )
}
