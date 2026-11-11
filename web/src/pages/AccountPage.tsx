import { useContext, useState } from 'react'
import { Link } from 'react-router'
import { displayName } from '../auth/authContext.ts'
import { useAuth } from '../auth/useAuth.ts'
import { BUTTON, PROSE } from '../components/styles.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { couldNotSave, keptAndRetried } from '../events/refusedText.ts'
import { useEventLogStatus } from '../events/useEvents.ts'
import { downloadJson } from '../export/download.ts'
import { collectExport, exportFileName } from '../export/exportData.ts'

// The learner's own page: who's signed in, whether any of their work is
// still only on this device, and a copy of everything they've done here
// ("Export my data", v1 spec, F16).
export function AccountPage() {
  const auth = useAuth()
  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-bold">Your account</h1>
        {auth.status === 'signed-in' && (
          <p className="text-slate-600 dark:text-slate-400">
            Signed in as {displayName(auth.user)}.
          </p>
        )}
      </header>
      {auth.status === 'signed-out' && (
        <p>
          <Link to="/sign-in" className="underline">
            Sign in
          </Link>{' '}
          to see your account and download your data.
        </p>
      )}
      {auth.status === 'signed-in' && (
        <>
          <NotSavedYet />
          <ExportData userId={auth.user.id} />
        </>
      )}
    </section>
  )
}

/**
 * Says how many of the learner's events the server has refused, and what
 * that means for them. Nothing shows when there are none, which is the
 * normal case. <output> is always on the page, so screen readers announce
 * the text when it appears.
 */
function NotSavedYet() {
  const { refused } = useEventLogStatus()
  return (
    <output className="block">
      {refused > 0 && (
        <span className="block space-y-2 rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-100">
          <span className="block font-medium">
            {couldNotSave(refused)}. {keptAndRetried(refused)}
          </span>
          {/* "This work" reads the same for one event or many. */}
          <span className="block">
            It isn't anything you did: the site refused this work when your
            browser tried to save it. Your browser tries again when you use the
            site, at most once every 12 hours, so there's nothing you need to
            do. Until it's saved, this work exists only in this browser: your
            progress may not count it, it won't show on another device, and
            clearing this browser's site data would erase it. "Download my data"
            below includes it.
          </span>
        </span>
      )}
    </output>
  )
}

type ExportState =
  | { status: 'idle' }
  | { status: 'working' }
  | { status: 'failed' }
  | {
      status: 'done'
      fileName: string
      events: number
      notOnServer: number
      refused: number
    }

function ExportData({ userId }: { userId: string }) {
  const log = useContext(EventLogContext)
  const [state, setState] = useState<ExportState>({ status: 'idle' })

  async function download() {
    setState({ status: 'working' })
    try {
      const data = await collectExport(userId, log)
      const fileName = exportFileName()
      downloadJson(fileName, data)
      setState({
        status: 'done',
        fileName,
        events: data.events.length,
        notOnServer: data.events.filter((event) => event.received_at === null)
          .length,
        refused: data.refused_events.length,
      })
    } catch (error) {
      console.error('Exporting data failed', error)
      setState({ status: 'failed' })
    }
  }

  return (
    <section aria-labelledby="export" className="space-y-4">
      <h2 id="export" className="text-xl font-semibold">
        Export my data
      </h2>
      <div className={PROSE}>
        <p>
          Download everything you've done here as one file: every lesson you've
          opened, every answer, Run, Check and hint, and your profile. It's a
          copy, so nothing on the site changes.
        </p>
        <p>
          The file is JSON, a plain-text format that Python and most other
          programs can read. To keep it as a backup, store a copy somewhere
          other than this computer, such as a cloud drive.
        </p>
      </div>
      <button
        type="button"
        onClick={() => void download()}
        disabled={state.status === 'working'}
        className={BUTTON}
      >
        Download my data
      </button>
      {/* <output> is announced by screen readers when its text changes. */}
      <output className="block">{message(state)}</output>
    </section>
  )
}

function message(state: ExportState): string {
  switch (state.status) {
    case 'idle':
      return ''
    case 'working':
      return 'Gathering your data…'
    case 'failed':
      return "Your data couldn't be downloaded. Check your connection, then try again."
    case 'done': {
      const what =
        state.events === 0
          ? 'your data, with no events yet'
          : `${state.events.toLocaleString('en-US')} ${state.events === 1 ? 'event' : 'events'}`
      return `Downloaded ${what}, as ${state.fileName}.${unsavedNote(state.events, state.notOnServer)}${refusedNote(state.refused)}`
    }
  }
}

/** Says the file also lists the events the server refused, if there are any. */
function refusedNote(refused: number): string {
  if (refused === 0) return ''
  const these =
    refused === 1
      ? "the 1 that couldn't be saved yet"
      : `the ${refused.toLocaleString('en-US')} that couldn't be saved yet`
  return ` The file also lists ${these}, separately.`
}

/** Says how many events came from this browser's outbox, if any did. */
function unsavedNote(events: number, notOnServer: number): string {
  if (notOnServer === 0) return ''
  if (events === 1) {
    return " It wasn't saved to your account yet, so it came from this browser."
  }
  if (notOnServer === 1) {
    return " 1 of them wasn't saved to your account yet, so it came from this browser."
  }
  return ` ${notOnServer.toLocaleString('en-US')} of them weren't saved to your account yet, so they came from this browser.`
}
