import { useContext, useState } from 'react'
import { Link } from 'react-router'
import { displayName } from '../auth/authContext.ts'
import { useAuth } from '../auth/useAuth.ts'
import { BUTTON, PROSE } from '../components/styles.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { downloadJson } from '../export/download.ts'
import { collectExport, exportFileName } from '../export/exportData.ts'

// The learner's own page: who's signed in, and a copy of everything they've
// done here ("Export my data", v1 spec, F16).
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
      {auth.status === 'signed-in' && <ExportData userId={auth.user.id} />}
    </section>
  )
}

type ExportState =
  | { status: 'idle' }
  | { status: 'working' }
  | { status: 'failed' }
  | { status: 'done'; fileName: string; events: number; notOnServer: number }

function ExportData({ userId }: { userId: string }) {
  const log = useContext(EventLogContext)
  const [state, setState] = useState<ExportState>({ status: 'idle' })

  async function download() {
    setState({ status: 'working' })
    try {
      const data = await collectExport(userId, () => log.getPendingRows())
      const fileName = exportFileName()
      downloadJson(fileName, data)
      setState({
        status: 'done',
        fileName,
        events: data.events.length,
        notOnServer: data.events.filter((event) => event.received_at === null)
          .length,
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
      return `Downloaded ${what}, as ${state.fileName}.${unsavedNote(state.events, state.notOnServer)}`
    }
  }
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
