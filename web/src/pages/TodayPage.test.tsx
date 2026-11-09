import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { getTopic } from '../content/content.ts'
import { EventsProvider } from '../events/EventsProvider.tsx'
import type { Attempt } from '../followups/followUps.ts'
import { fetchAttempts } from '../followups/history.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeEventsClient } from '../test/fakeEvents.ts'
import { allPassed, fakeRunner, oneFailed } from '../test/fakePython.ts'
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

/** A Check of a code exercise. */
function check(item: string, passed: boolean, when: string): Attempt {
  return { ...answer(item, passed, when), type: 'code_check' }
}

function renderToday(history: Attempt[] | Error, { signedIn = true } = {}) {
  if (history instanceof Error) {
    // The page reads the history twice (mistakes to revisit, then next up);
    // the first read fails.
    vi.mocked(fetchAttempts).mockResolvedValue([])
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

  it('says a skill is relearned after the third right day', async () => {
    // Missed 11 days ago; right 10 days ago (back 3 days later) and 7 days
    // ago (back 7 days later, today).
    renderToday([
      answer('predict-four-lines', false, daysAgo(11)),
      answer('review-mcq-commas', true, daysAgo(10)),
      answer('review-predict-commas', true, daysAgo(7)),
    ])
    const revisit = await revisitSection()
    await choose(revisit, 'Hi, Ada!')
    expect(
      await within(revisit).findByText(
        "Relearned: you've got this right on 3 different days.",
      ),
    ).toBeInTheDocument()
  })

  it('gives each skill its own question when one miss opens several', async () => {
    // The recipe card tests two skills, and it never passed that day.
    renderToday([check('write-recipe-card', false, daysAgo(1))])
    const revisit = await revisitSection()
    const headings = within(revisit)
      .getAllByRole('heading', { level: 3 })
      .map((heading) => heading.textContent)
    expect(headings).toEqual([
      'Fill in the gaps: A shopping list',
      'Quick check',
    ])
    expect(revisit).toHaveTextContent('Print an empty line with print()')
    expect(revisit).toHaveTextContent('Show text with print, in quotes')
  })

  it("doesn't count failing Checks on code that passed the same day", async () => {
    renderToday([
      check('write-recipe-card', false, daysAgo(1)),
      check('write-recipe-card', true, daysAgo(1)),
    ])
    expect(await revisitSection()).toHaveTextContent(
      'Nothing to revisit today.',
    )
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

describe('reviews on the Today page', () => {
  beforeEach(() => {
    setFakeRunner()
    vi.mocked(fetchAttempts).mockReset()
  })

  const PRINT = getTopic('py.programs-and-print')!

  /** The three proof checks of Programs and print, passed `days` ago. */
  function learnedDaysAgo(days: number): Attempt[] {
    return [
      check(PRINT.prove.build ?? '', true, daysAgo(days)),
      check(PRINT.prove.debug ?? '', true, daysAgo(days)),
      { ...answer('explain', true, daysAgo(days)), type: 'explain_submit' },
    ]
  }

  const reviewsSection = () => screen.findByRole('region', { name: 'Reviews' })

  /** Answers the session's two items: the postcard exercise and the quick check. */
  async function answerBoth(choice: string) {
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
    await userEvent.click(within(quick).getByRole('radio', { name: choice }))
    await userEvent.click(within(quick).getByRole('button', { name: 'Check' }))
  }

  it('says when nothing is due', async () => {
    renderToday([])
    expect(await screen.findByText('No reviews due today.')).toBeInTheDocument()
  })

  it('reviews a Learned topic once its review is due, with two items from its pool', async () => {
    renderToday(learnedDaysAgo(10))
    // The section shows once the due topics' content has loaded.
    expect(
      await screen.findByText(/One topic is due for a review/),
    ).toBeInTheDocument()
    const reviews = await reviewsSection()
    expect(
      within(reviews).getByRole('link', { name: 'Programs and print' }),
    ).toHaveAttribute('href', '/topic/py.programs-and-print')
    expect(
      await screen.findByRole('region', { name: 'Review: A postcard' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('region', { name: 'Quick check' }),
    ).toBeInTheDocument()
    expect(within(reviews).getAllByText(/Review \d of 2/)).toHaveLength(2)
  })

  it("isn't due the day after Learned", async () => {
    renderToday(learnedDaysAgo(1))
    expect(await screen.findByText('No reviews due today.')).toBeInTheDocument()
  })

  it('rates the session Good when both are right, and schedules the next one', async () => {
    setFakeRunner(fakeRunner({ check: allPassed('Prints the postcard') }))
    const { client } = renderToday(learnedDaysAgo(10))
    await answerBoth('Hi, Ada!')
    expect(
      await screen.findByText(/^Good: all right\. Next review/),
    ).toBeInTheDocument()
    await vi.waitFor(() => {
      const sent = client.send.mock.calls.flatMap(([rows]) => rows)
      const review = sent.find((row) => row.type === 'review')
      expect(review).toMatchObject({
        topic_id: 'py.programs-and-print',
        item_id: 'review',
        context: 'review',
        correct: true,
        data: { rating: 'good' },
      })
    })
  })

  it('rates it Hard when one is right, and Again when neither is', async () => {
    setFakeRunner(fakeRunner({ check: oneFailed('Prints the postcard') }))
    const { client } = renderToday(learnedDaysAgo(10))
    await answerBoth('Hi, Ada!')
    expect(await screen.findByText(/^Hard: some right/)).toBeInTheDocument()
    await vi.waitFor(() => {
      const sent = client.send.mock.calls.flatMap(([rows]) => rows)
      expect(sent.find((row) => row.type === 'review')).toMatchObject({
        correct: false,
        data: { rating: 'hard' },
      })
    })
  })

  it('rates it Again when nothing is right', async () => {
    setFakeRunner(fakeRunner({ check: oneFailed('Prints the postcard') }))
    renderToday(learnedDaysAgo(10))
    await answerBoth('Hi Ada!')
    expect(
      await screen.findByText(/^Again: none right this time/),
    ).toBeInTheDocument()
  })
})

describe('next up on the Today page', () => {
  beforeEach(() => {
    setFakeRunner()
    vi.mocked(fetchAttempts).mockReset()
  })

  const PRINT = getTopic('py.programs-and-print')!
  const nextUpSection = () => screen.findByRole('region', { name: 'Next up' })

  it('starts with the first topic when nothing has been started', async () => {
    renderToday([])
    const next = await nextUpSection()
    expect(next).toHaveTextContent('Start:')
    expect(
      within(next).getByRole('link', { name: 'Programs and print' }),
    ).toHaveAttribute('href', '/topic/py.programs-and-print')
    expect(next).toHaveTextContent(`about ${PRINT.estimated_minutes} minutes`)
  })

  it('continues the topic in progress', async () => {
    renderToday([answer('mcq-quotes', true, daysAgo(1))])
    const next = await nextUpSection()
    expect(next).toHaveTextContent('Continue:')
    expect(
      within(next).getByRole('link', { name: 'Programs and print' }),
    ).toBeInTheDocument()
  })

  it('moves on once a topic is learned', async () => {
    renderToday([
      check(PRINT.prove.build ?? '', true, daysAgo(1)),
      check(PRINT.prove.debug ?? '', true, daysAgo(1)),
      { ...answer('explain', true, daysAgo(1)), type: 'explain_submit' },
    ])
    const next = await nextUpSection()
    expect(next).toHaveTextContent('Start:')
    expect(
      within(next).getByRole('link', { name: 'Values and types' }),
    ).toBeInTheDocument()
  })

  it('is absent for signed-out visitors', () => {
    renderToday([], { signedIn: false })
    expect(screen.queryByRole('region', { name: 'Next up' })).toBeNull()
  })
})
