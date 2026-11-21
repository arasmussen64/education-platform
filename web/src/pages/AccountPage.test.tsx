import { fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { fetchRatedAnswers } from '../confidence/confidence.ts'
import type { EventLog } from '../events/eventLog.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { downloadJson, downloadText } from '../export/download.ts'
import { collectExport, type DataExport } from '../export/exportData.ts'
import type { Attempt } from '../followups/followUps.ts'
import { fetchAttempts } from '../followups/history.ts'
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
vi.mock('../export/download.ts', () => ({
  downloadJson: vi.fn(),
  downloadText: vi.fn(),
}))
// The forgetting curve reads the review history from the server: none here.
vi.mock('../followups/history.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../followups/history.ts')>()),
  fetchAttempts: vi.fn(async () => []),
}))
vi.mock('../checkpoints/stepsOpened.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../checkpoints/stepsOpened.ts')>()),
  fetchStepsOpened: vi.fn(async () => []),
}))
// The calibration summary reads the learner's answers from the server.
vi.mock('../confidence/confidence.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../confidence/confidence.ts')>()),
  fetchRatedAnswers: vi.fn(),
}))

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
    vi.mocked(fetchRatedAnswers).mockReset().mockResolvedValue([])
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

  it('says the forgetting curve is the average one until there are 100 reviews', async () => {
    renderAccount()
    expect(
      screen.getByRole('heading', { name: 'Your forgetting curve' }),
    ).toBeInTheDocument()
    expect(
      await screen.findByText(
        /timed by the average forgetting curve for now\. After 100 reviews the app fits the curve to you; 100 more to go\./,
      ),
    ).toBeInTheDocument()
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

describe("the account page's calibration summary (ADR-0028)", () => {
  const rated = (
    confidence: 'guess' | 'fair' | 'sure',
    right: number,
    wrong: number,
  ) =>
    Array.from({ length: right + wrong }, (_, index) => ({
      id: `${confidence}-${index}`,
      confidence,
      correct: index < right,
    }))

  beforeEach(() => {
    vi.mocked(fetchRatedAnswers).mockReset()
  })

  it('says how often the learner is right at each level they have used enough', async () => {
    vi.mocked(fetchRatedAnswers).mockResolvedValue([
      ...rated('sure', 23, 2),
      ...rated('guess', 4, 6),
      ...rated('fair', 3, 0),
    ])
    // An answer only this browser holds counts too. The same array every
    // time, as the real event log gives it (useSyncExternalStore needs it).
    const here = [
      eventRow({ id: 'here', correct: true, data: { confidence: 'guess' } }),
    ]
    const log = { ...recordingEventLog().log, getLocalRows: () => here }
    renderAccount({ log })
    expect(
      await screen.findByText(
        "When you're certain, you're right 92% of the time (25 answers).",
      ),
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        "When you guess, you're right 45% of the time (11 answers).",
      ),
    ).toBeInTheDocument()
    // Three answers is too few to say anything about.
    expect(
      screen.queryByText(/fairly sure, you're right/),
    ).not.toBeInTheDocument()
  })

  it('says when there are too few answers yet', async () => {
    vi.mocked(fetchRatedAnswers).mockResolvedValue(rated('fair', 2, 1))
    renderAccount()
    expect(
      await screen.findByText(/Not enough answers yet/),
    ).toBeInTheDocument()
  })

  it("says so when the answers can't be read", async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.mocked(fetchRatedAnswers).mockRejectedValue(new Error('offline'))
    renderAccount()
    expect(
      await screen.findByText(/Your answers couldn't be read/),
    ).toBeInTheDocument()
  })
})

describe('the study plan on the account page', () => {
  const section = () => screen.getByRole('region', { name: 'Study plan' })

  it('makes, changes and forgets a plan kept on this device', async () => {
    renderAccount()
    await userEvent.click(
      within(section()).getByRole('checkbox', { name: 'Tuesday' }),
    )
    fireEvent.change(within(section()).getByLabelText('Time'), {
      target: { value: '07:15' },
    })
    await userEvent.click(
      within(section()).getByRole('button', { name: 'Save my plan' }),
    )
    expect(section()).toHaveTextContent('Tuesday at 7:15 am.')
    expect(section()).toHaveTextContent('kept on this device only')

    await userEvent.click(
      within(section()).getByRole('button', {
        name: 'Add to my calendar (.ics)',
      }),
    )
    expect(downloadText).toHaveBeenCalledWith(
      'study-plan.ics',
      expect.stringContaining('RRULE:FREQ=WEEKLY;BYDAY=TU'),
      'text/calendar',
    )

    await userEvent.click(
      within(section()).getByRole('button', { name: 'Change my plan' }),
    )
    await userEvent.click(
      within(section()).getByRole('checkbox', { name: 'Friday' }),
    )
    await userEvent.click(
      within(section()).getByRole('button', { name: 'Save my plan' }),
    )
    expect(section()).toHaveTextContent('Tuesday and Friday at 7:15 am.')

    await userEvent.click(
      within(section()).getByRole('button', { name: 'Forget my plan' }),
    )
    expect(localStorage.getItem('study-plan')).toBeNull()
    expect(
      within(section()).getByRole('button', { name: 'Save my plan' }),
    ).toBeInTheDocument()
  })
})

describe('how hard it has been, on the account page (ADR-0030)', () => {
  beforeEach(() => {
    vi.mocked(fetchRatedAnswers).mockReset().mockResolvedValue([])
  })
  afterEach(() => {
    vi.mocked(fetchAttempts).mockResolvedValue([])
  })

  const section = () =>
    screen.getByRole('region', { name: "How hard it's been" })

  /** First tries at `count` questions of a topic, `right` of them right. */
  function tries(count: number, right: number, topicId: string): Attempt[] {
    return Array.from({ length: count }, (_, index) => ({
      id: `${topicId}-${index}`,
      type: 'answer' as const,
      topic_id: topicId,
      item_id: `q${index}`,
      correct: index < right,
      occurred_at: new Date(Date.UTC(2026, 10, 1, 12, index)).toISOString(),
      context: 'practice' as const,
    }))
  }

  it('says there are too few first tries until there are 20', async () => {
    renderAccount()
    expect(
      await within(section()).findByText(/Too few first tries to say yet/),
    ).toBeInTheDocument()
  })

  it('gives the share right first time, what it means, and the topics furthest off', async () => {
    vi.mocked(fetchAttempts).mockResolvedValue([
      ...tries(12, 4, 'py.programs-and-print'),
      ...tries(12, 12, 'py.values-and-types'),
    ])
    renderAccount()
    expect(
      await within(section()).findByText(/16 of 24 right first time \(67%\)/),
    ).toBeInTheDocument()
    expect(section()).toHaveTextContent('That is on the hard side')
    const topics = within(section()).getAllByRole('listitem')
    expect(topics.map((topic) => topic.textContent)).toEqual([
      'Programs and print: 4 of 12 right first time (33%), hard for you.',
      'Values and types: 12 of 12 right first time (100%), easy for you.',
    ])
  })
})
