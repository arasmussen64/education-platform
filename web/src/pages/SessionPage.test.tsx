import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { getTopic } from '../content/content.ts'
import { EventsProvider } from '../events/EventsProvider.tsx'
import type { Attempt } from '../followups/followUps.ts'
import { fetchAttempts } from '../followups/history.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeEventsClient } from '../test/fakeEvents.ts'
import { allPassed, fakeRunner } from '../test/fakePython.ts'
import { setFakeRunner } from '../test/mockPython.ts'
import { SessionPage } from './SessionPage.tsx'

// The history normally comes from the server; here each test supplies it.
// The questions are the real ones from content/ (Programs and print).
vi.mock('../followups/history.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../followups/history.ts')>()),
  fetchAttempts: vi.fn(),
}))
vi.mock('../checkpoints/stepsOpened.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../checkpoints/stepsOpened.ts')>()),
  fetchStepsOpened: vi.fn(async () => []),
}))
vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock(
  '../components/CodeEditor.tsx',
  () => import('../test/FakeCodeEditor.tsx'),
)

// Every test sees the same afternoon. Only Date is pinned, so timers run.
beforeEach(() => {
  vi.useFakeTimers({ toFake: ['Date'] })
  vi.setSystemTime(new Date(2026, 10, 11, 15, 0))
  setFakeRunner()
  vi.mocked(fetchAttempts).mockReset()
})
afterEach(() => {
  vi.useRealTimers()
})

const PRINT = getTopic('py.programs-and-print')!

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
    topic_id: PRINT.id,
    item_id: item,
    correct,
    occurred_at: when,
  }
}

/** Programs and print, proved `days` ago: its review is due by now. */
function learnedDaysAgo(days: number): Attempt[] {
  const check = (item: string) => ({
    ...answer(item, true, daysAgo(days)),
    type: 'code_check' as const,
  })
  return [
    check(PRINT.prove.build ?? ''),
    check(PRINT.prove.debug ?? ''),
    { ...answer('explain', true, daysAgo(days)), type: 'explain_submit' },
  ]
}

/** A missed question yesterday, back today as a different one. */
const missedYesterday = () => answer('predict-four-lines', false, daysAgo(1))

function renderSession(history: Attempt[], path = '/session') {
  vi.mocked(fetchAttempts).mockResolvedValue(history)
  const client = fakeEventsClient()
  render(
    <AuthProvider auth={fakeAuth(fakeUser())}>
      <EventsProvider client={client}>
        <MemoryRouter initialEntries={[path]}>
          <SessionPage />
        </MemoryRouter>
      </EventsProvider>
    </AuthProvider>,
  )
  return { client }
}

// A step shows once its topics' questions have downloaded, which can take
// more than the default second on a busy machine.
const stepHeading = (name: string) =>
  screen.findByRole('heading', { name, level: 2 }, { timeout: 5000 })
const next = () => userEvent.click(screen.getByRole('button', { name: 'Next' }))

describe('the guided session', () => {
  it('goes through a review, then a mistake coming back, then the next topic', async () => {
    renderSession([...learnedDaysAgo(10), missedYesterday()])

    expect(await stepHeading('Step 1 of 3 · Review')).toBeInTheDocument()
    expect(
      await screen.findByRole('region', { name: 'Review: A postcard' }),
    ).toBeInTheDocument()

    await next()
    const second = await stepHeading('Step 2 of 3 · A mistake coming back')
    // Focus moves to the new step, for keyboards and screen readers.
    expect(second).toHaveFocus()
    expect(screen.getByText('What does this line print?')).toBeInTheDocument()

    await next()
    expect(
      await stepHeading('Step 3 of 3 · Your next topic'),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Start Values and types' }),
    ).toHaveAttribute('href', '/topic/py.values-and-types')

    await userEvent.click(
      screen.getByRole('button', { name: 'Done for today' }),
    )
    expect(
      await screen.findByRole('heading', { name: "That's the session done" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/^Nothing was answered this time/),
    ).toBeInTheDocument()
  })

  it('grades and saves a review exactly as the Today page does, and counts it', async () => {
    setFakeRunner(fakeRunner({ check: allPassed('Prints the postcard') }))
    const { client } = renderSession([...learnedDaysAgo(10), missedYesterday()])

    const postcard = await screen.findByRole('region', {
      name: 'Review: A postcard',
    })
    await userEvent.type(
      within(postcard).getByLabelText('Python code'),
      'print()',
    )
    await userEvent.click(
      within(postcard).getByRole('button', { name: 'Check' }),
    )
    const quick = screen.getByRole('region', { name: 'Quick check' })
    await userEvent.click(
      within(quick).getByRole('radio', { name: 'Hi, Ada!' }),
    )
    await userEvent.click(
      within(quick).getByRole('button', { name: 'Fairly sure' }),
    )
    expect(
      await screen.findByText(/^Good: all right\. Next review/),
    ).toBeInTheDocument()
    await waitFor(() => {
      const sent = client.send.mock.calls.flatMap(([rows]) => rows)
      expect(sent.find((row) => row.type === 'review')).toMatchObject({
        topic_id: PRINT.id,
        context: 'review',
        data: { rating: 'good' },
      })
    })

    // The mistake coming back is answered too, in the review context.
    await next()
    await stepHeading('Step 2 of 3 · A mistake coming back')
    await userEvent.click(screen.getByRole('radio', { name: 'Hi, Ada!' }))
    await userEvent.click(screen.getByRole('button', { name: 'Fairly sure' }))
    await waitFor(() =>
      expect(client.send).toHaveBeenCalledWith([
        expect.objectContaining({
          item_id: 'review-mcq-commas',
          context: 'review',
        }),
      ]),
    )

    await next()
    await userEvent.click(
      screen.getByRole('button', { name: 'Done for today' }),
    )
    expect(
      await screen.findByText(
        'You finished 1 review and 1 mistake coming back. Each one is saved and counts in full.',
      ),
    ).toBeInTheDocument()
  })

  it('goes straight to the next topic when nothing is due', async () => {
    renderSession([])
    expect(
      await stepHeading('Step 1 of 1 · Your next topic'),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Start Programs and print' }),
    ).toHaveAttribute('href', '/topic/py.programs-and-print')
  })
})

describe('the five-minute session', () => {
  it('asks only the reviews closest to fading, not the mistakes or a new topic', async () => {
    renderSession(
      [...learnedDaysAgo(10), missedYesterday()],
      '/session?minutes=5',
    )
    expect(
      await screen.findByRole('heading', { name: 'Just 5 minutes', level: 1 }),
    ).toBeInTheDocument()
    expect(await stepHeading('Step 1 of 1 · Review')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Finish' }))
    expect(
      await screen.findByRole('heading', { name: "That's the session done" }),
    ).toBeInTheDocument()
  })

  it('says so when no review is due, and points to the full session', async () => {
    renderSession([missedYesterday()], '/session?minutes=5')
    expect(
      await screen.findByText(/^No reviews are due today/),
    ).toBeInTheDocument()
    const link = screen.getByRole('link', { name: "Today's session" })
    expect(link).toHaveAttribute('href', '/session')
    // Following it plans the full session afresh.
    await userEvent.click(link)
    expect(
      await stepHeading('Step 1 of 2 · A mistake coming back'),
    ).toBeInTheDocument()
  })
})

describe('how a session ends (ADR-0030)', () => {
  const VALUES = 'py.values-and-types'
  const endCard = () =>
    screen.findByRole(
      'region',
      { name: 'One question before you go' },
      { timeout: 5000 },
    )

  it("ends on a question about the next topic, and keeps the learner's guess", async () => {
    renderSession(learnedDaysAgo(10))
    await stepHeading('Step 1 of 2 · Review')
    await next()
    await userEvent.click(
      await screen.findByRole('button', { name: 'Done for today' }),
    )
    const card = await endCard()
    expect(card).toHaveTextContent('Your next topic is Values and types.')
    // Nothing is kept until a guess is typed.
    const keep = within(card).getByRole('button', {
      name: 'Keep my guess for next time',
    })
    expect(keep).toBeDisabled()

    await userEvent.type(
      within(card).getByRole('textbox', { name: 'Your guess' }),
      'Text and numbers differ',
    )
    await userEvent.click(keep)
    expect(card).toHaveTextContent('Your guess: Text and numbers differ')
    expect(card).toHaveTextContent('Kept on this device.')
    expect(
      within(card).getByRole('link', { name: 'Open Values and types' }),
    ).toHaveAttribute('href', `/topic/${VALUES}`)
    expect(
      JSON.parse(localStorage.getItem(`guess:${VALUES}`) ?? '{}'),
    ).toMatchObject({ guess: 'Text and numbers differ' })
  })

  it('ends the five-minute session on it too', async () => {
    renderSession(learnedDaysAgo(10), '/session?minutes=5')
    await stepHeading('Step 1 of 1 · Review')
    await userEvent.click(screen.getByRole('button', { name: 'Finish' }))
    expect(await endCard()).toHaveTextContent('Values and types')
  })

  it('shows the next unanswered question of a topic in progress, to sleep on', async () => {
    renderSession([
      ...learnedDaysAgo(10),
      // Values and types has been started.
      { ...answer('anything', false, daysAgo(1)), topic_id: VALUES },
    ])
    await stepHeading('Step 1 of 2 · Review')
    await next()
    await userEvent.click(
      await screen.findByRole('button', { name: 'Done for today' }),
    )
    const card = await screen.findByRole(
      'region',
      { name: 'One to sleep on' },
      { timeout: 5000 },
    )
    expect(card).toHaveTextContent('The next thing waiting in Values and types')
    // Nothing to answer here: answering belongs on the topic's page.
    expect(within(card).queryByRole('textbox')).not.toBeInTheDocument()
    expect(
      within(card).getByRole('link', { name: "It'll be here" }),
    ).toHaveAttribute('href', `/topic/${VALUES}`)
  })
})
