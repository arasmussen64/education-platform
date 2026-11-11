import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import type { EventLog } from '../events/eventLog.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { downloadJson } from '../export/download.ts'
import { collectExport, type DataExport } from '../export/exportData.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { eventRow, recordingEventLog } from '../test/fakeEvents.ts'
import { AccountPage } from './AccountPage.tsx'

// The data normally comes from the server, and the browser saves the file.
// Here each test supplies the data and checks what would have been saved.
vi.mock('../export/exportData.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../export/exportData.ts')>()),
  collectExport: vi.fn(),
  exportFileName: () => 'learning-data.json',
}))
vi.mock('../export/download.ts', () => ({ downloadJson: vi.fn() }))

const ADA = fakeUser()

/** A finished export holding these events. */
function exported(
  events: DataExport['events'],
  refusedEvents: DataExport['refused_events'] = [],
): DataExport {
  return {
    format: 1,
    exported_at: '2026-11-07T09:15:00.000Z',
    content_build: 'abc123',
    user_id: ADA.id,
    profile: null,
    events,
    refused_events: refusedEvents,
  }
}

/** An event log on a device holding this many refused events. */
function logWithRefused(count: number): EventLog {
  const refused = Array.from({ length: count }, (_, index) => ({
    event: eventRow({ id: `refused-${index}` }),
    reason: '400 23514: violates check constraint',
    at: '2026-11-10T08:30:00.000Z',
    attempts: 1,
  }))
  const status = { pending: 0, syncing: false, refused: count }
  return {
    ...recordingEventLog().log,
    getStatus: () => status,
    getRefusedEvents: () => refused,
  }
}

const savedEvent = (id: string) => ({
  ...eventRow({ id }),
  received_at: '2026-11-06T12:00:05+00:00',
})

function renderAccount({
  signedIn = true,
  log = recordingEventLog().log,
}: { signedIn?: boolean; log?: EventLog } = {}) {
  render(
    <AuthProvider auth={fakeAuth(signedIn ? ADA : null)}>
      <EventLogContext value={log}>
        <MemoryRouter>
          <AccountPage />
        </MemoryRouter>
      </EventLogContext>
    </AuthProvider>,
  )
}

const downloadButton = () =>
  screen.getByRole('button', { name: 'Download my data' })

describe('the account page', () => {
  beforeEach(() => {
    vi.mocked(collectExport).mockReset()
    vi.mocked(downloadJson).mockReset()
  })

  it('asks a signed-out visitor to sign in', () => {
    renderAccount({ signedIn: false })
    expect(
      screen.getByText(/to see your account and download your data/),
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Download my data' }),
    ).not.toBeInTheDocument()
  })

  it("downloads the learner's data as a file, and says how much", async () => {
    const data = exported([savedEvent('a'), savedEvent('b')])
    vi.mocked(collectExport).mockResolvedValue(data)
    const log = recordingEventLog().log
    renderAccount({ log })
    expect(screen.getByText('Signed in as ada.')).toBeInTheDocument()
    // Nothing was refused, so there's no warning.
    expect(screen.queryByText(/couldn't be saved/)).not.toBeInTheDocument()

    await userEvent.click(downloadButton())
    // The event log supplies what only this browser holds.
    expect(collectExport).toHaveBeenCalledWith(ADA.id, log)
    expect(downloadJson).toHaveBeenCalledWith('learning-data.json', data)
    expect(
      await screen.findByText('Downloaded 2 events, as learning-data.json.'),
    ).toBeInTheDocument()
  })

  it("includes what's still waiting in this browser, and says so", async () => {
    const waiting = [eventRow({ id: 'not-sent-yet' })]
    const log = { ...recordingEventLog().log, getPendingRows: () => waiting }
    // Like the real thing: whatever the outbox holds has no received_at.
    vi.mocked(collectExport).mockImplementation(async (_userId, browser) =>
      exported([
        savedEvent('a'),
        ...browser
          .getPendingRows()
          .map((event) => ({ ...event, received_at: null })),
      ]),
    )
    renderAccount({ log })

    await userEvent.click(downloadButton())
    expect(
      await screen.findByText(
        "Downloaded 2 events, as learning-data.json. 1 of them wasn't saved to your account yet, so it came from this browser.",
      ),
    ).toBeInTheDocument()
  })

  it('says how much work the server has refused, and that the download includes it', async () => {
    // Like the real thing: the refused events go under their own key.
    vi.mocked(collectExport).mockImplementation(async (_userId, browser) =>
      exported(
        [savedEvent('a')],
        browser.getRefusedEvents().map(({ event, reason, at, attempts }) => ({
          reason,
          last_tried_at: at,
          attempts,
          event,
        })),
      ),
    )
    renderAccount({ log: logWithRefused(3) })
    expect(
      screen.getByText(
        "3 pieces of your work couldn't be saved yet. They're kept on this device and will be tried again.",
      ),
    ).toBeInTheDocument()
    // What it means for the learner, and that the file has the work.
    expect(screen.getByText(/at most once every 12 hours/)).toHaveTextContent(
      '"Download my data" below includes it.',
    )

    await userEvent.click(downloadButton())
    expect(
      await screen.findByText(
        "Downloaded 1 event, as learning-data.json. The file also lists the 3 that couldn't be saved yet, separately.",
      ),
    ).toBeInTheDocument()
  })

  it('says it about a single piece of work in the singular', () => {
    renderAccount({ log: logWithRefused(1) })
    expect(
      screen.getByText(
        "1 piece of your work couldn't be saved yet. It's kept on this device and will be tried again.",
      ),
    ).toBeInTheDocument()
  })

  it("says so when the data can't be read, and lets the learner try again", async () => {
    const quiet = vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.mocked(collectExport)
      .mockRejectedValueOnce(new Error('Failed to fetch'))
      .mockResolvedValueOnce(exported([]))
    renderAccount()

    await userEvent.click(downloadButton())
    expect(
      await screen.findByText(
        "Your data couldn't be downloaded. Check your connection, then try again.",
      ),
    ).toBeInTheDocument()
    expect(downloadJson).not.toHaveBeenCalled()

    await userEvent.click(downloadButton())
    expect(
      await screen.findByText(
        'Downloaded your data, with no events yet, as learning-data.json.',
      ),
    ).toBeInTheDocument()
    quiet.mockRestore()
  })

  it('ignores more clicks while it gathers the data', async () => {
    vi.mocked(collectExport).mockReturnValue(new Promise(() => {}))
    renderAccount()

    await userEvent.click(downloadButton())
    expect(downloadButton()).toBeDisabled()
    expect(screen.getByText('Gathering your data…')).toBeInTheDocument()
    await userEvent.click(downloadButton())
    expect(collectExport).toHaveBeenCalledTimes(1)
  })
})
