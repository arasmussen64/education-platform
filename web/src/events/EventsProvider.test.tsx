import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { SaveStatus } from '../components/SaveStatus.tsx'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeEventsClient } from '../test/fakeEvents.ts'
import { EventsProvider } from './EventsProvider.tsx'
import { RETRY_REFUSED_AFTER_MS } from './sync.ts'
import { useRecordEvent } from './useEvents.ts'

/** A button that records an answer, standing in for a practice item. */
function AnswerButton() {
  const record = useRecordEvent()
  return (
    <button
      type="button"
      onClick={() =>
        record({
          type: 'answer',
          topic_id: 'py.variables',
          item_id: 'mcq-1',
          context: 'practice',
          correct: true,
        })
      }
    >
      Answer
    </button>
  )
}

function renderApp(
  client: ReturnType<typeof fakeEventsClient>,
  user = fakeUser(),
) {
  render(
    <AuthProvider auth={fakeAuth(user)}>
      <EventsProvider client={client}>
        {/* The status line links to the account page, so it needs a router. */}
        <MemoryRouter>
          <SaveStatus />
          <AnswerButton />
        </MemoryRouter>
      </EventsProvider>
    </AuthProvider>,
  )
}

afterEach(() => {
  vi.useRealTimers()
})

const answer = () =>
  userEvent.click(screen.getByRole('button', { name: 'Answer' }))

describe('saving learner events', () => {
  it("saves answers to the signed-in learner's account", async () => {
    const client = fakeEventsClient()
    renderApp(client)
    await answer()

    await waitFor(() =>
      expect(client.send).toHaveBeenCalledWith([
        expect.objectContaining({
          user_id: fakeUser().id,
          type: 'answer',
          item_id: 'mcq-1',
          // The commit this build came from (vite.config.ts).
          content_build: expect.stringMatching(/^([0-9a-f]{40}|unknown)$/),
        }),
      ]),
    )
    expect(screen.queryByText('Not saved yet')).not.toBeInTheDocument()
  })

  it('keeps work on the device while offline, and saves it when the connection returns', async () => {
    const client = fakeEventsClient({
      ok: false,
      retryLater: true,
      message: '0 : TypeError: Failed to fetch',
    })
    renderApp(client)
    await answer()
    expect(await screen.findByText('Not saved yet')).toBeInTheDocument()

    client.send.mockResolvedValue({ ok: true })
    act(() => {
      window.dispatchEvent(new Event('online'))
    })
    await waitFor(() =>
      expect(screen.queryByText('Not saved yet')).not.toBeInTheDocument(),
    )
    expect(client.send).toHaveBeenLastCalledWith([
      expect.objectContaining({ item_id: 'mcq-1' }),
    ])
  })

  it('says so while the server refuses work, until a later try saves it', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    // Only the clock is faked, so the test can jump half a day ahead.
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2026-11-10T12:00:00.000Z'))
    const client = fakeEventsClient({
      ok: false,
      retryLater: false,
      message: '400 23514: violates check constraint',
    })
    renderApp(client)
    const line = "1 piece of your work couldn't be saved yet"
    expect(screen.queryByText(line)).not.toBeInTheDocument()

    await answer()
    const link = await screen.findByRole('link', { name: line })
    expect(link).toHaveAttribute('href', '/account')
    expect(link).toHaveAttribute(
      'title',
      expect.stringContaining(
        "It's kept on this device and will be tried again.",
      ),
    )
    // It isn't waiting for a connection, so the other badge stays away.
    expect(screen.queryByText('Not saved yet')).not.toBeInTheDocument()

    // A second answer is refused too: the line counts both.
    await answer()
    expect(
      await screen.findByText("2 pieces of your work couldn't be saved yet"),
    ).toBeInTheDocument()

    // Half a day later the server accepts them, and the learner comes back.
    client.send.mockResolvedValue({ ok: true })
    vi.setSystemTime(Date.now() + RETRY_REFUSED_AFTER_MS + 1000)
    act(() => {
      window.dispatchEvent(new Event('online'))
    })
    await waitFor(() =>
      expect(
        screen.queryByText(/couldn't be saved yet/),
      ).not.toBeInTheDocument(),
    )
    expect(client.send).toHaveBeenLastCalledWith([
      expect.objectContaining({ item_id: 'mcq-1' }),
    ])
  })

  it('saves nothing for a signed-out visitor', async () => {
    const client = fakeEventsClient()
    render(
      <AuthProvider auth={fakeAuth(null)}>
        <EventsProvider client={client}>
          <AnswerButton />
        </EventsProvider>
      </AuthProvider>,
    )
    await answer()
    expect(client.send).not.toHaveBeenCalled()
    expect(localStorage.length).toBe(0)
  })
})
