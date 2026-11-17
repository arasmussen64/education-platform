import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { getTopic, loadTopicContent } from '../content/content.ts'
import { dayOf } from '../days.ts'
import { EventsProvider } from '../events/EventsProvider.tsx'
import type { Topic } from '../content/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import { fetchAttempts } from '../followups/history.ts'
import { fetchPlacements, type PlacementRecord } from '../placement/history.ts'
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
// No checkpoint's steps were ever opened.
vi.mock('../checkpoints/stepsOpened.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../checkpoints/stepsOpened.ts')>()),
  fetchStepsOpened: vi.fn(async () => []),
}))
vi.mock('../placement/history.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../placement/history.ts')>()),
  fetchPlacements: vi.fn(),
}))
vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock(
  '../components/CodeEditor.tsx',
  () => import('../test/FakeCodeEditor.tsx'),
)
// The real content loads as usual; tests can see which topics did, or make
// a download fail.
vi.mock('../content/content.ts', async (importOriginal) => {
  const content = await importOriginal<typeof import('../content/content.ts')>()
  return { ...content, loadTopicContent: vi.fn(content.loadTopicContent) }
})

// The page reads the clock; every test here sees the same afternoon. Only
// Date is pinned, so the page's timers still run.
beforeEach(() => {
  vi.useFakeTimers({ toFake: ['Date'] })
  vi.setSystemTime(new Date(2026, 10, 11, 15, 0))
  vi.mocked(loadTopicContent).mockClear()
})
afterEach(() => {
  vi.useRealTimers()
})

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

function renderToday(
  history: Attempt[] | Error,
  {
    signedIn = true,
    placements = [] as PlacementRecord[],
  }: { signedIn?: boolean; placements?: PlacementRecord[] } = {},
) {
  vi.mocked(fetchPlacements).mockResolvedValue(placements)
  if (history instanceof Error) {
    // The page reads the history once, for everything on it; that read
    // fails, and the next one works.
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

  it('adds up practice time, capped per attempt, with a milestone per track', async () => {
    renderToday([
      // Python: ninety seconds, ninety seconds, and three hours with the page
      // left open, which counts as the 30-minute cap. Cloud: five minutes.
      { ...answer('mcq-print', true, daysAgo(1)), duration_ms: 90_000 },
      { ...check('fill-greeting', true, daysAgo(2)), duration_ms: 90_000 },
      {
        ...answer('predict-four-lines', true, daysAgo(10)),
        duration_ms: 3 * 60 * 60_000,
      },
      answer('review-mcq-commas', true, daysAgo(3)),
      {
        ...answer('mcq-shell', true, daysAgo(1)),
        topic_id: 'csa.linux.shell',
        duration_ms: 5 * 60_000,
      },
    ])
    const hours = await screen.findByRole('region', { name: 'Practice hours' })
    // The total, in one sentence.
    expect(hours).toHaveTextContent(
      '38 minutes of deliberate practice so far, 8 minutes of it in the last 7 days.',
    )
    // Then each track on its own ladder (ADR-0019).
    const python = within(hours).getByRole('heading', {
      name: /^Python Foundations/,
    })
    expect(python).toHaveTextContent(
      'Python Foundations33 minutes so far, 3 minutes in the last 7 days',
    )
    expect(
      within(hours).getByRole('progressbar', {
        name: 'Python Foundations: progress toward 1 hour',
      }),
    ).toHaveAttribute('value', '33')
    expect(
      within(hours).getByRole('progressbar', {
        name: 'Cloud Solutions Architect: progress toward 1 hour',
      }),
    ).toHaveAttribute('value', '5')
    expect(hours).toHaveTextContent(
      'Next milestone: 1 hour (27 minutes to go).',
    )
    expect(hours).toHaveTextContent(
      'Next milestone: 1 hour (55 minutes to go).',
    )
    // Nothing is on a topic outside the tracks, so no "Other" ladder.
    expect(
      within(hours).queryByRole('heading', { name: /^Other/ }),
    ).not.toBeInTheDocument()
  })

  it('shows a track with no practice yet, at zero, beside the one with some', async () => {
    renderToday([
      { ...answer('mcq-print', true, daysAgo(1)), duration_ms: 90_000 },
    ])
    const hours = await screen.findByRole('region', { name: 'Practice hours' })
    expect(
      within(hours).getByRole('heading', {
        name: /^Cloud Solutions Architect/,
      }),
    ).toHaveTextContent('nothing counted yet')
    expect(
      within(hours).getByRole('progressbar', {
        name: 'Cloud Solutions Architect: progress toward 1 hour',
      }),
    ).toHaveAttribute('value', '0')
  })

  it('says when no practice time has been counted yet', async () => {
    renderToday([])
    const hours = await screen.findByRole('region', { name: 'Practice hours' })
    expect(hours).toHaveTextContent('Nothing counted yet.')
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
    expect(
      await screen.findByText(
        "Your progress couldn't load. Check your connection, then try again.",
      ),
    ).toBeInTheDocument()
    // Nothing else shows meanwhile: every part of the plan needs it.
    expect(screen.queryByRole('region', { name: 'Reviews' })).toBeNull()
    expect(screen.queryByRole('region', { name: 'Next up' })).toBeNull()
    await userEvent.click(screen.getByRole('button', { name: 'Try again' }))
    expect(await revisitSection()).toHaveTextContent(
      'Nothing to revisit today.',
    )
    expect(screen.getByRole('region', { name: 'Next up' })).toBeInTheDocument()
  })

  it('reads the history once for the whole page', async () => {
    renderToday([answer('predict-four-lines', false, daysAgo(1))])
    await revisitSection()
    await screen.findByRole('region', { name: 'Next up' })
    await screen.findByText('No reviews due today.')
    expect(fetchAttempts).toHaveBeenCalledTimes(1)
  })

  it("downloads only the topics of today's questions in full", async () => {
    renderToday([
      // Due today: its topic is needed for the question.
      answer('predict-four-lines', false, daysAgo(1)),
      // Missed today, so back tomorrow: listed from the topic's outline.
      {
        ...answer('mcq-which-type', false, daysAgo(0)),
        topic_id: 'py.values-and-types',
      },
    ])
    expect(await revisitSection()).toHaveTextContent(COMMAS)
    expect(
      screen.getByRole('region', { name: 'Coming back later' }),
    ).toHaveTextContent(
      'Tell str, int and float apart, and check with type() (Values and types): tomorrow',
    )
    expect(
      vi.mocked(loadTopicContent).mock.calls.map(([topicId]) => topicId),
    ).toEqual(['py.programs-and-print'])
  })

  it("offers to try again when today's questions fail to download", async () => {
    vi.mocked(loadTopicContent).mockRejectedValueOnce(new Error('offline'))
    renderToday([answer('predict-four-lines', false, daysAgo(1))])
    const revisit = await revisitSection()
    expect(
      await within(revisit).findByText(
        "Today's questions to revisit couldn't load. Check your connection, then try again.",
      ),
    ).toBeInTheDocument()
    await userEvent.click(
      within(revisit).getByRole('button', { name: 'Try again' }),
    )
    expect(await revisitSection()).toHaveTextContent(
      'What does this line print?',
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

  it("waits for tomorrow once the day's reviews are done", async () => {
    // Twenty review sessions already finished today, on other topics.
    const doneToday = Array.from({ length: 20 }, (_, i) => ({
      ...answer('review', true, daysAgo(0)),
      type: 'review' as const,
      topic_id: `py.elsewhere-${i}`,
      rating: 'good' as const,
      context: 'review' as const,
    }))
    renderToday([...learnedDaysAgo(10), ...doneToday])
    expect(
      await screen.findByText(/^That's today's reviews done\./),
    ).toBeInTheDocument()
    expect(screen.queryByText(/is due for a review/)).not.toBeInTheDocument()
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

  it('offers to try again when a review fails to download', async () => {
    // Offline, or the site was updated while the tab was open.
    vi.mocked(loadTopicContent).mockRejectedValueOnce(new Error('offline'))
    renderToday(learnedDaysAgo(10))
    const reviews = await reviewsSection()
    expect(
      await within(reviews).findByText(
        "Your reviews couldn't load. Check your connection, then try again.",
      ),
    ).toBeInTheDocument()
    await userEvent.click(
      within(reviews).getByRole('button', { name: 'Try again' }),
    )
    expect(
      await screen.findByText(/One topic is due for a review/),
    ).toBeInTheDocument()
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

describe("today's session on the Today page", () => {
  beforeEach(() => {
    setFakeRunner()
    vi.mocked(fetchAttempts).mockReset()
  })

  const PRINT = getTopic('py.programs-and-print')!
  const sessionSection = () =>
    screen.findByRole('region', { name: "Today's session" })

  it('says what the session holds, and starts it with one button', async () => {
    renderToday([
      check(PRINT.prove.build ?? '', true, daysAgo(10)),
      check(PRINT.prove.debug ?? '', true, daysAgo(10)),
      { ...answer('explain', true, daysAgo(10)), type: 'explain_submit' },
      answer('predict-four-lines', false, daysAgo(1)),
    ])
    const session = await sessionSection()
    expect(session).toHaveTextContent(
      '1 review and 1 mistake coming back, then your next topic, Values and types.',
    )
    expect(
      within(session).getByRole('link', { name: "Start today's session" }),
    ).toHaveAttribute('href', '/session')
    expect(
      within(session).getByRole('link', { name: 'Just 5 minutes' }),
    ).toHaveAttribute('href', '/session?minutes=5')
    expect(session).toHaveTextContent(
      'Just 5 minutes: the one review closest to fading, counted in full.',
    )
    // Where the next topic sits in its module.
    expect(session).toHaveTextContent(
      /1 of (\d+) topics proven in Module 1, First programs: \d+ to go\./,
    )
  })

  it('goes straight to the next topic when nothing is due, with no short version', async () => {
    renderToday([])
    const session = await sessionSection()
    expect(session).toHaveTextContent(
      'Nothing to review today, so straight to your next topic, Programs and print.',
    )
    expect(
      within(session).queryByRole('link', { name: 'Just 5 minutes' }),
    ).not.toBeInTheDocument()
    // Nothing proven in the module yet: a fresh start.
    expect(session).toHaveTextContent(
      /A fresh start: Module 1, First programs, begins here, with \d+ topics\./,
    )
  })
})

describe('weeks with practice on the Today page', () => {
  beforeEach(() => {
    setFakeRunner()
    vi.mocked(fetchAttempts).mockReset()
  })

  const hours = () => screen.findByRole('region', { name: 'Practice hours' })

  it('counts the weeks with practice, not a streak of days', async () => {
    // This week, last week, and four weeks back.
    renderToday([
      answer('mcq-print', true, daysAgo(0)),
      answer('mcq-print', true, daysAgo(8)),
      answer('mcq-print', true, daysAgo(30)),
    ])
    const section = await hours()
    expect(section).toHaveTextContent('You practised in 3 of the last 5 weeks.')
    expect(section).not.toHaveTextContent(/streak/i)
    expect(section).not.toHaveTextContent('A session today counts')
    const marks = within(section).getByTestId('week-marks').children
    // Oldest first.
    expect(
      [...marks].map((mark) => mark.getAttribute('data-practised')),
    ).toEqual(['true', 'false', 'false', 'true', 'true'])
  })

  it('says gently that today counts when this week has nothing yet', async () => {
    renderToday([
      answer('mcq-print', true, daysAgo(9)),
      answer('mcq-print', true, daysAgo(20)),
    ])
    const section = await hours()
    expect(section).toHaveTextContent('You practised in 2 of the last 3 weeks.')
    expect(section).toHaveTextContent('A session today counts for this week.')
  })

  it('says nothing about weeks before any practice', async () => {
    renderToday([])
    expect(await hours()).not.toHaveTextContent('You practised')
  })
})

describe('next up on the Today page', () => {
  beforeEach(() => {
    setFakeRunner()
    vi.mocked(fetchAttempts).mockReset()
  })

  const PRINT = getTopic('py.programs-and-print')!
  const nextUpSection = () => screen.findByRole('region', { name: 'Next up' })

  /** The entry for one track, by the heading that names it (ADR-0019). */
  function trackEntry(section: HTMLElement, title: RegExp) {
    const heading = within(section).getByRole('heading', { name: title })
    const entry = heading.parentElement
    if (!entry) throw new Error('a track entry wraps its heading')
    return entry
  }

  it('offers the placement test until one has been taken', async () => {
    renderToday([])
    const next = await nextUpSection()
    expect(
      await within(next).findByRole('link', {
        name: 'Take the placement test',
      }),
    ).toHaveAttribute('href', '/placement')
  })

  it('says where the placement test said to start', async () => {
    const at = daysAgo(1)
    renderToday([], {
      placements: [
        {
          id: 'p1',
          run: 'r1',
          subject: 'python-foundations',
          kind: 'track',
          at,
          known: ['py.programs-and-print'],
          next: 'py.values-and-types',
          asked: 4,
          correct: 3,
        },
      ],
    })
    const next = await nextUpSection()
    expect(
      await within(next).findByText(
        `Python Foundations. Placement on ${dayOf(at)}: start at Values and types, with 1 topic to prove first.`,
      ),
    ).toBeInTheDocument()
    expect(
      within(next).getByRole('link', { name: 'Placement test' }),
    ).toHaveAttribute('href', '/placement')
  })

  it('starts each track with its first topic when nothing has been started', async () => {
    renderToday([])
    const next = await nextUpSection()
    const python = trackEntry(next, /^Python Foundations/)
    expect(python).toHaveTextContent('0 of')
    expect(python).toHaveTextContent('Start:')
    expect(
      within(python).getByRole('link', { name: 'Programs and print' }),
    ).toHaveAttribute('href', '/topic/py.programs-and-print')
    expect(python).toHaveTextContent(`about ${PRINT.estimated_minutes} minutes`)
    const cloud = trackEntry(next, /^Cloud Solutions Architect/)
    expect(cloud).toHaveTextContent('0 of')
    expect(cloud).toHaveTextContent('Start:')
    expect(
      within(cloud).getByRole('link', { name: 'Shell essentials' }),
    ).toHaveAttribute('href', '/topic/csa.linux.shell')
  })

  it('says what unlocks a track whose topics are all locked', async () => {
    renderToday([])
    const next = await nextUpSection()
    const ml = trackEntry(next, /^Machine Learning Foundations/)
    expect(ml).toHaveTextContent(
      "Next: Fractions, decimals and percentages, once you've learned Strings and input (Python Foundations).",
    )
    expect(
      within(ml).getByRole('link', {
        name: 'Fractions, decimals and percentages',
      }),
    ).toHaveAttribute('href', '/topic/ml.math.arithmetic')
  })

  it('continues the topic in progress, in its own track only', async () => {
    renderToday([answer('mcq-quotes', true, daysAgo(1))])
    const next = await nextUpSection()
    const python = trackEntry(next, /^Python Foundations/)
    expect(python).toHaveTextContent('Continue:')
    expect(
      within(python).getByRole('link', { name: 'Programs and print' }),
    ).toBeInTheDocument()
    const cloud = trackEntry(next, /^Cloud Solutions Architect/)
    expect(cloud).toHaveTextContent('Start:')
    expect(
      within(cloud).getByRole('link', { name: 'Shell essentials' }),
    ).toBeInTheDocument()
  })

  it('moves a track on once one of its topics is learned, and counts it', async () => {
    renderToday([
      check(PRINT.prove.build ?? '', true, daysAgo(1)),
      check(PRINT.prove.debug ?? '', true, daysAgo(1)),
      { ...answer('explain', true, daysAgo(1)), type: 'explain_submit' },
    ])
    const next = await nextUpSection()
    const python = trackEntry(next, /^Python Foundations/)
    expect(python).toHaveTextContent('1 of')
    expect(python).toHaveTextContent('Start:')
    expect(
      within(python).getByRole('link', { name: 'Values and types' }),
    ).toBeInTheDocument()
    // The other track is untouched by it.
    expect(trackEntry(next, /^Cloud Solutions Architect/)).toHaveTextContent(
      '0 of',
    )
  })

  it('is absent for signed-out visitors', () => {
    renderToday([], { signedIn: false })
    expect(screen.queryByRole('region', { name: 'Next up' })).toBeNull()
  })
})

describe('honest times on the Today page', () => {
  beforeEach(() => {
    setFakeRunner()
    vi.mocked(fetchAttempts).mockReset()
  })

  const FIRST_THREE = [
    getTopic('py.programs-and-print')!,
    getTopic('py.values-and-types')!,
    getTopic('py.variables')!,
  ]
  const ARITHMETIC = getTopic('py.arithmetic')!

  /**
   * A topic worked through in one sitting `days` ago, from noon, for twice
   * its estimate: an answer every 10 minutes, its proof checks at the end.
   */
  function provenInTwiceItsEstimate(topic: Topic, days: number): Attempt[] {
    const start = Date.parse(daysAgo(days))
    const minutes = 2 * topic.estimated_minutes
    const at = (minute: number) =>
      new Date(start + minute * 60_000).toISOString()
    const steps: Attempt[] = []
    for (let minute = 0; minute < minutes; minute += 10) {
      steps.push({
        ...answer('mcq-print', true, at(minute)),
        topic_id: topic.id,
      })
    }
    const end = at(minutes)
    return [
      ...steps,
      { ...check(topic.prove.build ?? '', true, end), topic_id: topic.id },
      { ...check(topic.prove.debug ?? '', true, end), topic_id: topic.id },
      {
        ...answer('explain', true, end),
        type: 'explain_submit',
        topic_id: topic.id,
      },
    ]
  }

  it("stretches the topics' times to the learner's pace, and says why", async () => {
    renderToday(
      FIRST_THREE.flatMap((topic, index) =>
        provenInTwiceItsEstimate(topic, 30 - 10 * index),
      ),
    )
    const next = await screen.findByRole('region', { name: 'Next up' })
    expect(next).toHaveTextContent(
      `about ${2 * ARITHMETIC.estimated_minutes} minutes at your pace`,
    )
    expect(next).toHaveTextContent(
      "Topics you've proven took you about 2.0× their estimate, so the times on this page are stretched to match.",
    )
    expect(next).toHaveTextContent(/reading before it isn't included/)
    const session = await screen.findByRole('region', {
      name: "Today's session",
    })
    // Three reviews at the default minute a question, then the new topic.
    expect(session).toHaveTextContent(
      `About 6 minutes for those, then about ${2 * ARITHMETIC.estimated_minutes} for the new topic at your pace.`,
    )
  })

  it("keeps the authors' estimates until three topics are proven", async () => {
    renderToday(provenInTwiceItsEstimate(FIRST_THREE[0], 10))
    const next = await screen.findByRole('region', { name: 'Next up' })
    expect(next).toHaveTextContent(
      `about ${FIRST_THREE[1].estimated_minutes} minutes`,
    )
    expect(next).not.toHaveTextContent('at your pace')
    expect(next).not.toHaveTextContent('their estimate')
  })
})

describe('coming back on the Today page', () => {
  beforeEach(() => {
    setFakeRunner()
    vi.mocked(fetchAttempts).mockReset()
  })

  const PRINT = getTopic('py.programs-and-print')!
  const proved = (days: number): Attempt[] => [
    check(PRINT.prove.build ?? '', true, daysAgo(days)),
    check(PRINT.prove.debug ?? '', true, daysAgo(days)),
    { ...answer('explain', true, daysAgo(days)), type: 'explain_submit' },
  ]

  it('welcomes the learner back after a break, with a calm plan', async () => {
    renderToday(proved(10))
    const welcome = await screen.findByRole('region', { name: 'Welcome back' })
    expect(welcome).toHaveTextContent(
      "It's been 10 days since you last practised, and that's all right: what you learned is still there, some of it faded.",
    )
    expect(welcome).toHaveTextContent('Today: 1 review, about 2 minutes')
    expect(welcome).toHaveTextContent('Programs and print (memory about')
    // Nothing that reads as a debt.
    expect(welcome).not.toHaveTextContent(/missed|behind|overdue|streak/i)
  })

  it('says nothing after a short gap', async () => {
    renderToday([answer('mcq-quotes', true, daysAgo(2))])
    await screen.findByRole('region', { name: 'Next up' })
    expect(
      screen.queryByRole('region', { name: 'Welcome back' }),
    ).not.toBeInTheDocument()
  })
})

describe('late in the evening on the Today page', () => {
  beforeEach(() => {
    setFakeRunner()
    vi.mocked(fetchAttempts).mockReset()
  })

  const EVENING = /^It's late in your day: a good time for reviews\./

  it('suggests reviews tonight and new topics earlier tomorrow, and blocks nothing', async () => {
    vi.setSystemTime(new Date(2026, 10, 11, 22, 0))
    renderToday([])
    expect(await screen.findByText(EVENING)).toBeInTheDocument()
    // The session, and its new topic, can still start.
    expect(
      await screen.findByRole('link', { name: "Start today's session" }),
    ).toHaveAttribute('href', '/session')
  })

  it('says nothing in the afternoon', async () => {
    renderToday([])
    await screen.findByRole('region', { name: 'Next up' })
    expect(screen.queryByText(EVENING)).not.toBeInTheDocument()
  })
})
