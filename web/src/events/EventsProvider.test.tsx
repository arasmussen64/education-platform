import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { SaveStatus } from '../components/SaveStatus.tsx'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeEventsClient } from '../test/fakeEvents.ts'
import { EventsProvider } from './EventsProvider.tsx'
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
        <SaveStatus />
        <AnswerButton />
      </EventsProvider>
    </AuthProvider>,
  )
}

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
