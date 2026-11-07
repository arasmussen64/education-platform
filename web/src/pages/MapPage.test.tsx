import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
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

function renderMap(history: Attempt[] | Error, { signedIn = true } = {}) {
  vi.mocked(fetchAttempts).mockResolvedValue([])
  if (history instanceof Error) {
    vi.mocked(fetchAttempts).mockRejectedValueOnce(history)
  } else {
    vi.mocked(fetchAttempts).mockResolvedValue(history)
  }
  render(
    <AuthProvider auth={fakeAuth(signedIn ? fakeUser() : null)}>
      <EventLogContext value={recordingEventLog().log}>
        <MemoryRouter>
          <MapPage />
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

  it("shows what the learner has done on each topic they've started", async () => {
    renderMap([
      attempt(PRINT.id, PRINT.practice[1], 'answer', false),
      attempt(TYPES.id, TYPES.prove.build, 'code_check', true),
      attempt(TYPES.id, TYPES.prove.debug, 'code_check', false),
    ])

    expect(
      await within(row('Values and types')).findByText(
        'In progress · Proof checks passed: build',
      ),
    ).toBeInTheDocument()
    expect(
      within(row('Programs and print')).getByText('In progress'),
    ).toBeInTheDocument()
    expect(within(row('Variables')).queryByText(/In progress/)).toBeNull()
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
