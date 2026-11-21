import { useState } from 'react'
import { CARD, SECONDARY_BUTTON } from '../components/styles.ts'
import { CalendarButton, StudyPlanForm } from './StudyPlanForm.tsx'
import {
  describePlan,
  formatTime,
  type StudyPlan,
  WEEKDAYS,
  wherePart,
} from './studyPlan.ts'
import type { StudyPlanState } from './useStudyPlan.ts'

// Where the study plan shows (studyplan/studyPlan.ts): a one-line reminder
// at the top of the Today page, the question asked once at its foot, and a
// section on the Account page to change or forget it.

const ASK =
  'Choosing the days, a time and a place in advance makes it much more likely to happen. Your plan stays on this device.'

/** "Your plan for today: 7:30 pm, at the library." or the whole week's. */
function reminder(plan: StudyPlan, now: Date): string {
  const today = WEEKDAYS[(now.getDay() + 6) % 7]
  if (!plan.days.includes(today)) return `Your plan: ${describePlan(plan)}`
  return `Your plan for today: ${formatTime(plan.time)}${wherePart(plan.place)}.`
}

/** Said when the browser wouldn't keep the plan (a private window, say). */
function NotKept() {
  return (
    <p className="text-sm text-muted">
      This browser couldn't keep your plan, so it lasts until you leave the
      page. The calendar file keeps it for good.
    </p>
  )
}

/** The plan as one line at the top of the Today page, with a way to change it. */
export function StudyPlanReminder({ state }: { state: StudyPlanState }) {
  const [editing, setEditing] = useState(false)
  const [now] = useState(() => new Date())
  const { plan, kept, save } = state
  if (!plan) return null
  if (editing) {
    return (
      <section aria-labelledby="study-plan" className={CARD}>
        <h2 id="study-plan" className="text-xl font-semibold">
          When and where will you study?
        </h2>
        <StudyPlanForm
          initial={plan}
          onSave={(next) => {
            save(next)
            setEditing(false)
          }}
          onCancel={() => setEditing(false)}
        />
      </section>
    )
  }
  return (
    <div className="space-y-2">
      <p className="text-ink">{reminder(plan, now)}</p>
      <div className="flex flex-wrap gap-2">
        <CalendarButton plan={plan} />
        <button
          type="button"
          onClick={() => setEditing(true)}
          className={SECONDARY_BUTTON}
        >
          Change my plan
        </button>
      </div>
      {!kept && <NotKept />}
    </div>
  )
}

/**
 * "When and where will you study?", asked once at the foot of the Today
 * page: until the learner makes a plan or says "Not now".
 */
export function StudyPlanQuestion({ state }: { state: StudyPlanState }) {
  const { plan, dismissed, save, notNow } = state
  if (plan || dismissed) return null
  return (
    <section aria-labelledby="study-plan-question" className={CARD}>
      <h2 id="study-plan-question" className="text-xl font-semibold">
        When and where will you study?
      </h2>
      <p className="text-muted">{ASK}</p>
      <StudyPlanForm
        initial={null}
        onSave={save}
        onCancel={notNow}
        cancelLabel="Not now"
      />
    </section>
  )
}

/** The plan on the Account page: make it, change it, or forget it. */
export function StudyPlanSection({ state }: { state: StudyPlanState }) {
  const [editing, setEditing] = useState(false)
  const { plan, kept, save, forget } = state
  return (
    <section aria-labelledby="study-plan-account" className="space-y-3">
      <h2 id="study-plan-account" className="text-xl font-semibold">
        Study plan
      </h2>
      {plan && !editing ? (
        <>
          <p>{describePlan(plan)}</p>
          <div className="flex flex-wrap gap-2">
            <CalendarButton plan={plan} />
            <button
              type="button"
              onClick={() => setEditing(true)}
              className={SECONDARY_BUTTON}
            >
              Change my plan
            </button>
            <button type="button" onClick={forget} className={SECONDARY_BUTTON}>
              Forget my plan
            </button>
          </div>
          {!kept && <NotKept />}
          <p className="text-sm text-muted">
            It's kept on this device only, not with your account.
          </p>
        </>
      ) : (
        <>
          <p className="text-muted">{ASK}</p>
          <StudyPlanForm
            initial={plan}
            onSave={(next) => {
              save(next)
              setEditing(false)
            }}
            onCancel={editing ? () => setEditing(false) : undefined}
          />
        </>
      )}
    </section>
  )
}
