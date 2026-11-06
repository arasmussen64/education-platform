import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { EventsProvider } from '../events/EventsProvider.tsx'
import type { Attempt } from '../followups/followUps.ts'
import { fetchAttempts } from '../followups/history.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeEventsClient } from '../test/fakeEvents.ts'
import { setFakeRunner } from '../test/mockPython.ts'
import { TodayPage } from './TodayPage.tsx'

// The history normally comes from the server; here each test supplies it.
// The questions are the real ones from content/ (Programs and print).
vi.mock('../followups/history.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../followups/history.ts')>()),
  fetchAttempts: vi.fn(),
}))
vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock(
  '../components/CodeEditor.tsx',
  () => import('../test/FakeCodeEditor.tsx'),
)

const COMMAS =
  'Print several pieces of text on one line, with commas between them'

/** Noon, `days` days ago, local time. */
function daysAgo(days: number): string {
  const date = new Date()
  date.setDate(date.getDate() - days)
  date.setHours(12, 0, 0, 0)
  return date.toISOString()
}

let lastId = 0
function answer(item: string, correct: boolean, when: string): Attempt {
  return {
    id: `attempt-${++lastId}`,
    type: 'answer',
    topic_id: 'py.programs-and-print',
    item_id: item,
    correct,
    occurred_at: when,
  }
}

function renderToday(history: Attempt[] | Error, { signedIn = true } = {}) {
  if (history instanceof Error) {
    vi.mocked(fetchAttempts).mockRejectedValueOnce(history)
  } else {
    vi.mocked(fetchAttempts).mockResolvedValue(history)
  }
  const client = fakeEventsClient()
  render(
    <AuthProvider auth={fakeAuth(signedIn ? fakeUser() : null)}>
      <EventsProvider client={client}>
        <MemoryRouter>
          <TodayPage />
        </MemoryRouter>
      </EventsProvider>
    </AuthProvider>,
  )
  return { client }
}

const revisitSection = () =>
  screen.findByRole('region', { name: 'Mistakes to revisit' })

async function choose(section: HTMLElement, choice: string) {
  await userEvent.click(within(section).getByRole('radio', { name: choice }))
  await userEvent.click(within(section).getByRole('button', { name: 'Check' }))
}

describe('the Today page', () => {
  beforeEach(() => {
    setFakeRunner()
    vi.mocked(fetchAttempts).mockReset()
  })

  it('brings a missed skill back the next day, as a different question', async () => {
    const { client } = renderToday([
      answer('predict-four-lines', false, daysAgo(1)),
    ])
    const revisit = await revisitSection()
    expect(revisit).toHaveTextContent(COMMAS)
    // Not the question that was missed, but another on the same skill.
    expect(
      within(revisit).getByText('What does this line print?'),
    ).toBeInTheDocument()

    await choose(revisit, 'Hi, Ada!')
    expect(
      await within(revisit).findByText(/^Right! It comes back on /),
    ).toBeInTheDocument()
    // Saved as a review, like any other answer.
    await waitFor(() =>
      expect(client.send).toHaveBeenCalledWith([
        expect.objectContaining({
          item_id: 'review-mcq-commas',
          context: 'review',
          correct: true,
        }),
      ]),
    )
  })

  it('brings it back tomorrow after another wrong answer', async () => {
    renderToday([answer('predict-four-lines', false, daysAgo(1))])
    const revisit = await revisitSection()
    await choose(revisit, 'Hi,Ada!')
    expect(
      await within(revisit).findByText('Not quite. It comes back tomorrow.'),
    ).toBeInTheDocument()
  })

  it('says a skill is relearned after the second right day', async () => {
    renderToday([
      answer('predict-four-lines', false, daysAgo(4)),
      answer('review-predict-commas', true, daysAgo(3)),
    ])
    const revisit = await revisitSection()
    await choose(revisit, 'Hi, Ada!')
    expect(
      await within(revisit).findByText(
        "Relearned: you've got this right on 2 different days.",
      ),
    ).toBeInTheDocument()
  })

  it('lists what comes back later when nothing is due today', async () => {
    renderToday([answer('predict-four-lines', false, daysAgo(0))])
    const revisit = await revisitSection()
    expect(revisit).toHaveTextContent('Nothing to revisit today.')
    expect(
      screen.getByRole('region', { name: 'Coming back later' }),
    ).toHaveTextContent(`${COMMAS} (Programs and print): tomorrow`)
  })

  it('has nothing to revisit without any mistakes', async () => {
    renderToday([answer('mcq-quotes', true, daysAgo(1))])
    expect(await revisitSection()).toHaveTextContent(
      'Nothing to revisit today.',
    )
    expect(
      screen.queryByRole('region', { name: 'Coming back later' }),
    ).not.toBeInTheDocument()
  })

  it('offers to try again when the history fails to load', async () => {
    renderToday(new Error('offline'))
    vi.mocked(fetchAttempts).mockResolvedValue([])
    await userEvent.click(
      await screen.findByRole('button', { name: 'Try again' }),
    )
    expect(await revisitSection()).toHaveTextContent(
      'Nothing to revisit today.',
    )
  })

  it('asks signed-out visitors to sign in', async () => {
    renderToday([], { signedIn: false })
    expect(
      await screen.findByText(/to see what to revisit today/),
    ).toBeInTheDocument()
    expect(fetchAttempts).not.toHaveBeenCalled()
  })
})
