import { useContext, useId, useState } from 'react'
import { AuthContext } from '../auth/authContext.ts'
import { SECONDARY_BUTTON, TEXT_INPUT } from '../components/styles.ts'
import {
  MAX_REPORT_CHARS,
  type ReportAbout,
  type SendReport,
  sendReport,
} from './report.ts'

type State = 'idle' | 'sending' | 'sent' | 'failed'

/**
 * "Report a problem" (v1 spec, F15): a small link under a lesson, exercise
 * or question that opens a box for the learner to say what's wrong. The
 * report is saved with the item and its revision. Signed-out visitors
 * don't see it: a report needs an account to belong to.
 */
export function ReportProblem({
  about,
  send = sendReport,
}: {
  about: ReportAbout
  /** Tests pass a fake. */
  send?: SendReport
}) {
  // Read directly, not through useAuth(): this renders inside components
  // that are also used where no sign-in exists.
  const auth = useContext(AuthContext)
  const boxId = useId()
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [state, setState] = useState<State>('idle')
  if (!auth || auth.status !== 'signed-in') return null
  const user = auth.user

  async function submit() {
    setState('sending')
    const result = await send(user.id, about, message)
    if (result === 'sent') setMessage('')
    setState(result)
  }

  if (!open) {
    return (
      <p className="text-right">
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="text-xs text-slate-500 underline hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
        >
          Report a problem
        </button>
      </p>
    )
  }

  return (
    <form
      aria-label="Report a problem"
      onSubmit={(event) => {
        event.preventDefault()
        void submit()
      }}
      className="space-y-2 rounded-md border border-slate-200 p-3 text-sm dark:border-slate-700"
    >
      <label htmlFor={boxId} className="block font-medium">
        What's wrong here?
      </label>
      <textarea
        id={boxId}
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        rows={3}
        maxLength={MAX_REPORT_CHARS}
        autoComplete="off"
        className={TEXT_INPUT}
      />
      <p className="text-xs text-slate-500 dark:text-slate-400">
        A wrong answer, a confusing hint, a broken link: anything. The report is
        saved with this item, so it can be fixed.
      </p>
      <div className="flex flex-wrap gap-2">
        <button
          type="submit"
          disabled={state === 'sending' || message.trim() === ''}
          className={SECONDARY_BUTTON}
        >
          Send report
        </button>
        <button
          type="button"
          onClick={() => {
            setOpen(false)
            setState('idle')
          }}
          className={SECONDARY_BUTTON}
        >
          {state === 'sent' ? 'Close' : 'Cancel'}
        </button>
      </div>
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block">{MESSAGES[state]}</output>
    </form>
  )
}

const MESSAGES: Record<State, string> = {
  idle: '',
  sending: 'Sending…',
  sent: 'Thanks. Your report is saved.',
  failed:
    "Your report couldn't be sent. Check your connection, then try again.",
}
