import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { tracks } from '../content/content.ts'
import { loadDraft, saveDraft } from '../drafts/drafts.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { recallPart, rememberPart } from '../parts/partMemory.ts'
import { recallPlace, rememberPlace } from '../place/placeMemory.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { StartOver } from './StartOver.tsx'

// No history on the server: every track is not started.
vi.mock('../followups/history.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../followups/history.ts')>()),
  fetchAttempts: vi.fn(async () => []),
}))
vi.mock('../checkpoints/stepsOpened.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../checkpoints/stepsOpened.ts')>()),
  fetchStepsOpened: vi.fn(async () => []),
}))

function renderStartOver() {
  const { log, events } = recordingEventLog()
  render(
    <AuthProvider auth={fakeAuth(fakeUser())}>
      <EventLogContext value={log}>
        <StartOver />
      </EventLogContext>
    </AuthProvider>,
  )
  return events
}

describe('starting a track over', () => {
  it('offers every track', async () => {
    renderStartOver()
    // Each button waits for the progress to load.
    for (const track of tracks()) {
      const button = screen.getByRole('button', {
        name: `Start ${track.title} over…`,
      })
      await waitFor(() => expect(button).toBeEnabled())
    }
  })

  it('asks first, says what stays, and records nothing on Cancel', async () => {
    const user = userEvent.setup()
    const events = renderStartOver()
    await user.click(
      await screen.findByRole('button', {
        name: 'Start Python Foundations over…',
      }),
    )
    const ask = screen.getByRole('group', {
      name: 'Start Python Foundations over?',
    })
    expect(within(ask).getByText(/Nothing is deleted/)).toBeInTheDocument()
    expect(within(ask).getByText(/your forgetting curve/)).toBeInTheDocument()
    await user.click(within(ask).getByRole('button', { name: 'Cancel' }))
    expect(events).toEqual([])
    expect(
      screen.queryByRole('group', { name: 'Start Python Foundations over?' }),
    ).not.toBeInTheDocument()
  })

  it("records one reset for that track and forgets its topics' drafts and places on this device", async () => {
    saveDraft({ topicId: 'py.variables', itemId: 'fill-swap', rev: 1 }, 'a = b')
    saveDraft({ topicId: 'csa.intro', itemId: 'write-x', rev: 1 }, 'keep me')
    rememberPart('py.variables', 'practice')
    rememberPlace('py.variables', 'place-recap')
    const user = userEvent.setup()
    const events = renderStartOver()
    await user.click(
      await screen.findByRole('button', {
        name: 'Start Python Foundations over…',
      }),
    )
    await user.click(
      screen.getByRole('button', {
        name: 'Yes, start Python Foundations over',
      }),
    )
    expect(events).toEqual([
      { type: 'track_reset', topic_id: 'python-foundations', context: 'learn' },
    ])
    expect(
      screen.getByText(/Python Foundations has been started over/),
    ).toBeInTheDocument()
    expect(
      loadDraft({ topicId: 'py.variables', itemId: 'fill-swap', rev: 1 }),
    ).toBeNull()
    expect(loadDraft({ topicId: 'csa.intro', itemId: 'write-x', rev: 1 })).toBe(
      'keep me',
    )
    expect(recallPart('py.variables')).toBeNull()
    expect(recallPlace('py.variables')).toBeNull()
  })
})
