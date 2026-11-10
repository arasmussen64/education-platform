import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { getTopic } from '../content/content.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import type { Attempt } from '../followups/followUps.ts'
import { fetchAttempts } from '../followups/history.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { MapPage } from './MapPage.tsx'

// The history normally comes from the server; here each test supplies it.
// The topics are the real ones from content/.
vi.mock('../followups/history.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../followups/history.ts')>()),
  fetchAttempts: vi.fn(),
}))

const PRINT = getTopic('py.programs-and-print')!
const TYPES = getTopic('py.values-and-types')!

let lastId = 0
function attempt(
  topicId: string,
  itemId: string | undefined,
  type: Attempt['type'],
  correct: boolean,
): Attempt {
  return {
    id: `attempt-${++lastId}`,
    type,
    topic_id: topicId,
    item_id: itemId ?? '',
    correct,
    occurred_at: '2026-11-06T12:00:00.000Z',
  }
}

function renderMap(
  history: Attempt[] | Error,
  { signedIn = true, path = '/map' } = {},
) {
  vi.mocked(fetchAttempts).mockResolvedValue([])
  if (history instanceof Error) {
    vi.mocked(fetchAttempts).mockRejectedValueOnce(history)
  } else {
    vi.mocked(fetchAttempts).mockResolvedValue(history)
  }
  render(
    <AuthProvider auth={fakeAuth(signedIn ? fakeUser() : null)}>
      <EventLogContext value={recordingEventLog().log}>
        <MemoryRouter initialEntries={[path]}>
          <Routes>
            <Route path="/map/:trackId?" element={<MapPage />} />
          </Routes>
        </MemoryRouter>
      </EventLogContext>
    </AuthProvider>,
  )
}

/** A topic's row on the map. */
function row(title: string): HTMLElement {
  const item = screen.getByRole('link', { name: title }).closest('li')
  if (!item) throw new Error(`No row for ${title}`)
  return item
}

describe('progress on the map', () => {
  beforeEach(() => {
    vi.mocked(fetchAttempts).mockReset()
  })

  it("shows each topic's state, and the proof checks passed so far", async () => {
    renderMap([
      attempt(PRINT.id, PRINT.practice[1], 'answer', false),
      attempt(TYPES.id, TYPES.prove.build, 'code_check', true),
      attempt(TYPES.id, TYPES.prove.debug, 'code_check', false),
    ])

    // Started, but its prerequisite isn't learned, so it's Locked (F8).
    const types = row('Values and types')
    expect(
      await within(types).findByText('Proof checks passed: build'),
    ).toBeInTheDocument()
    expect(within(types).getByText(/Locked/)).toBeInTheDocument()
    expect(
      within(row('Programs and print')).getByText(/In progress/),
    ).toBeInTheDocument()
    expect(within(row('Variables')).getByText(/Locked/)).toBeInTheDocument()
    expect(within(row('Variables')).queryByText(/Proof checks/)).toBeNull()
  })

  it('unlocks the next topic once one is Learned', async () => {
    renderMap([
      attempt(PRINT.id, PRINT.prove.build, 'code_check', true),
      attempt(PRINT.id, PRINT.prove.debug, 'code_check', true),
      attempt(PRINT.id, 'explain', 'explain_submit', true),
    ])
    expect(
      await within(row('Programs and print')).findByText(/Learned/),
    ).toBeInTheDocument()
    expect(
      within(row('Values and types')).getByText(/Available/),
    ).toBeInTheDocument()
    expect(within(row('Variables')).getByText(/Locked/)).toBeInTheDocument()
  })

  it('says when a Learned topic is due for a review', async () => {
    const tenDaysAgo = new Date(Date.now() - 10 * 24 * 60 * 60 * 1000)
    const learned = [
      attempt(PRINT.id, PRINT.prove.build, 'code_check', true),
      attempt(PRINT.id, PRINT.prove.debug, 'code_check', true),
      attempt(PRINT.id, 'explain', 'explain_submit', true),
    ].map((each) => ({ ...each, occurred_at: tenDaysAgo.toISOString() }))
    renderMap(learned)
    expect(
      await within(row('Programs and print')).findByText(/Fading: review due/),
    ).toBeInTheDocument()
    // The living map: how well the topic is predicted to be remembered.
    const memory = within(row('Programs and print')).getByText(/^Memory: \d+%$/)
    expect(Number(/\d+/.exec(memory.textContent ?? '')?.[0])).toBeLessThan(90)
    // A topic that isn't Learned yet has no memory to show.
    expect(within(row('Variables')).queryByText(/Memory:/)).toBeNull()
  })

  it('shows signed-out visitors only whether a topic can be opened', () => {
    renderMap([], { signedIn: false })
    expect(within(row('Variables')).getByText(/Ready/)).toBeInTheDocument()
    expect(within(row('Variables')).queryByText(/Locked/)).toBeNull()
  })

  it('says while the progress loads, and if it fails, with a way to try again', async () => {
    renderMap(new Error('Failed to fetch'))
    expect(screen.getByText('Loading your progress…')).toBeInTheDocument()

    await userEvent.click(
      await screen.findByRole('button', { name: 'Try again' }),
    )
    await waitFor(() =>
      expect(
        screen.queryByRole('button', { name: 'Try again' }),
      ).not.toBeInTheDocument(),
    )
    expect(fetchAttempts).toHaveBeenCalledTimes(2)
  })

  it('shows no progress to a signed-out visitor, and reads no history', () => {
    renderMap([], { signedIn: false })
    expect(screen.queryByText('Loading your progress…')).not.toBeInTheDocument()
    expect(fetchAttempts).not.toHaveBeenCalled()
  })
})

describe('a prerequisite in another track', () => {
  const FRACTIONS = 'Fractions, decimals and percentages'

  it('locks the topic until that prerequisite is learned', async () => {
    renderMap([], { path: '/map/ml-foundations' })
    await waitFor(() => expect(row(FRACTIONS)).toHaveTextContent('Locked'))
  })

  it('unlocks it once the other track has learned it', async () => {
    renderMap(
      [
        attempt(
          'py.strings-and-input',
          'build-km-to-miles',
          'code_check',
          true,
        ),
        attempt('py.strings-and-input', 'debug-shopping', 'code_check', true),
        attempt('py.strings-and-input', 'explain', 'explain_submit', true),
      ],
      { path: '/map/ml-foundations' },
    )
    await waitFor(() => expect(row(FRACTIONS)).toHaveTextContent('Available'))
  })
})

describe('more than one track', () => {
  beforeEach(() => {
    vi.mocked(fetchAttempts).mockReset()
  })

  it('opens on the first track and links to the others', () => {
    renderMap([])
    expect(screen.getByText('Python Foundations:')).toBeInTheDocument()
    const nav = screen.getByRole('navigation', { name: 'Tracks' })
    expect(
      within(nav).getByRole('link', { name: 'Python Foundations' }),
    ).toHaveAttribute('aria-current', 'page')
    expect(
      within(nav).getByRole('link', { name: 'Cloud Solutions Architect' }),
    ).toHaveAttribute('href', '/map/cloud-solutions-architect')
  })

  it('shows another track at its own address, with its capstones, once its outlines load', async () => {
    renderMap([], { path: '/map/cloud-solutions-architect' })
    // The track's name and summary are bundled with the app; its outlines
    // download when the map first shows it.
    expect(screen.getByText('Cloud Solutions Architect:')).toBeInTheDocument()
    expect(screen.getByText("Loading this track's map…")).toBeInTheDocument()
    expect(
      // The first load turns 357 outline files into code, which can take a
      // few seconds on a slow machine (CI); the default wait is one second.
      await screen.findByRole(
        'heading',
        { name: 'Module 1: Linux and the command line' },
        { timeout: 15_000 },
      ),
    ).toBeInTheDocument()
  }, 20_000)

  it('still shows the track when its outlines are already loaded', () => {
    // The test above loaded them; now they're there at once.
    renderMap([], { path: '/map/cloud-solutions-architect' })
    expect(
      screen.getByRole('heading', {
        name: 'Module 1: Linux and the command line',
      }),
    ).toBeInTheDocument()
    // Module 1 has many ready topics now (and a couple still in draft), so
    // the track is no longer "an outline so far". The exact draft count
    // keeps changing as the module fills in, so we don't pin it here.
    expect(screen.queryByText(/an outline so far/)).not.toBeInTheDocument()
    expect(screen.getAllByText(/Ready/).length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByRole('heading', { name: 'Capstone' })).toHaveLength(3)
    expect(
      screen.getByRole('link', {
        name: 'Capstone 1: one product, three clouds',
      }),
    ).toBeInTheDocument()
  })

  it('says when there is no such track', () => {
    renderMap([], { path: '/map/nothing' })
    expect(
      screen.getByRole('heading', { name: 'No such track' }),
    ).toBeInTheDocument()
  })
})
