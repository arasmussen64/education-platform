import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import type { Topic, TopicContent } from '../content/types.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { EventsProvider } from '../events/EventsProvider.tsx'
import { gradeExplanation } from '../explain/grade.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import type { Attempt } from '../followups/followUps.ts'
import {
  fakeCheckpointContent,
  fakeContent,
  fakeTopic,
} from '../test/fakeContent.tsx'
import { fakeEventsClient, recordingEventLog } from '../test/fakeEvents.ts'
import { allPassed, fakeRunner, oneFailed } from '../test/fakePython.ts'
import { setFakeRunner } from '../test/mockPython.ts'
import { TopicView } from './TopicPage.tsx'

vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock(
  '../components/CodeEditor.tsx',
  () => import('../test/FakeCodeEditor.tsx'),
)
// Explanations are graded by the AI proxy; tests say what it answers.
vi.mock('../explain/grade.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../explain/grade.ts')>()),
  gradeExplanation: vi.fn(),
}))

/** Renders a topic for a signed-in learner (unless `signedIn` is false). */
function renderTopic(
  topic: Topic = fakeTopic(),
  content: TopicContent | null = fakeContent(topic),
  {
    signedIn = true,
    loadAttempts = vi.fn((_topicId: string) => Promise.resolve<Attempt[]>([])),
  } = {},
) {
  const { log, events } = recordingEventLog()
  render(
    <AuthProvider auth={fakeAuth(signedIn ? fakeUser() : null)}>
      <EventLogContext value={log}>
        <MemoryRouter>
          <TopicView
            topic={topic}
            content={content}
            loadAttempts={loadAttempts}
          />
        </MemoryRouter>
      </EventLogContext>
    </AuthProvider>,
  )
  return { events, loadAttempts }
}

/** The text of each item heading in a section, in order. */
function itemHeadings(section: HTMLElement) {
  return within(section)
    .getAllByRole('heading', { level: 3 })
    .map((heading) => heading.textContent)
}

describe('the topic page', () => {
  beforeEach(() => {
    setFakeRunner()
  })

  it('shows where the topic fits and what it builds on', () => {
    renderTopic()
    expect(
      screen.getByRole('heading', { level: 1, name: 'Values and types' }),
    ).toBeInTheDocument()
    expect(screen.getByText('Module 1: First programs')).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Programs and print' }),
    ).toHaveAttribute('href', '/topic/py.programs-and-print')
    expect(
      screen.getByText(/About 30 minutes for the whole topic/),
    ).toBeInTheDocument()
  })

  it('teaches with an intro, the main resource, a recap and more resources', () => {
    renderTopic()
    const learn = screen.getByRole('region', { name: 'Learn' })
    expect(learn).toHaveTextContent('Use type() to check a value.')
    expect(within(learn).getByText('What to watch for')).toBeInTheDocument()
    expect(within(learn).getByText('Recap')).toBeInTheDocument()
    expect(
      within(learn).getByTitle('Python values, explained'),
    ).toHaveAttribute(
      'src',
      'https://www.youtube-nocookie.com/embed/abc123?start=65&end=190&rel=0',
    )
    expect(learn).toHaveTextContent('(1:05–3:10)')
    // The player shows the whole video's length, so the page says how long
    // the clip is, and that it stops by itself.
    expect(learn).toHaveTextContent(
      'This clip: 1:05 to 3:10 (about 2 minutes).',
    )
    expect(learn).toHaveTextContent('it stops by itself at 3:10')
    expect(learn).toHaveTextContent('License: CC BY 4.0')
    expect(
      within(learn).getByRole('link', { name: 'The Python tutorial: numbers' }),
    ).toHaveAttribute(
      'href',
      'https://docs.python.org/3/tutorial/introduction.html',
    )
  })

  it('shows a reading as a link, credited with its license once', () => {
    renderTopic(
      fakeTopic({
        resources: [
          {
            title: 'A good chapter',
            url: 'https://example.com/chapter',
            type: 'reading',
            use: 'link',
            license: 'CC BY 4.0',
          },
        ],
      }),
    )
    const learn = screen.getByRole('region', { name: 'Learn' })
    expect(
      within(learn).getByRole('link', { name: /A good chapter/ }),
    ).toHaveAttribute('href', 'https://example.com/chapter')
    expect(learn).toHaveTextContent('License: CC BY 4.0.')
    expect(within(learn).getAllByText(/A good chapter/)).toHaveLength(1)
  })

  it('lists the practice ladder in order', () => {
    renderTopic()
    const practice = screen.getByRole('region', { name: 'Practice' })
    expect(itemHeadings(practice)).toEqual([
      'Worked example: Say hello',
      'Quick check',
      'Predict the output',
      'Fill in the gaps: Say hello',
      'Write it: Say hello',
    ])
    expect(within(practice).getByText('Practice 1 of 5')).toBeInTheDocument()
  })

  it('has the three proof checks, without revealing the model answer', () => {
    renderTopic()
    const prove = screen.getByRole('region', { name: 'Prove it' })
    expect(itemHeadings(prove)).toEqual([
      'Build: Greet',
      'Debug: Fix the greeting',
      'Explain it back',
    ])
    expect(prove).toHaveTextContent('Why is "5" different from 5?')
    expect(document.body).not.toHaveTextContent('SECRET MODEL ANSWER')
  })

  it('says when a topic is still being written', () => {
    renderTopic(fakeTopic({ status: 'planned' }), null)
    expect(screen.getByText(/still being written/)).toBeInTheDocument()
    expect(
      screen.queryByRole('region', { name: 'Practice' }),
    ).not.toBeInTheDocument()
  })

  it('marks drafts', () => {
    renderTopic(fakeTopic({ status: 'draft' }))
    expect(screen.getByText(/Draft: only shown/)).toBeInTheDocument()
  })

  it('asks signed-out learners to sign in to save their answers', () => {
    renderTopic(fakeTopic(), fakeContent(), { signedIn: false })
    expect(screen.getByText(/won't be saved/)).toBeInTheDocument()
    // At the top, and in the explain check, which needs a signed-in learner.
    const links = screen.getAllByRole('link', { name: 'Sign in' })
    expect(links).toHaveLength(2)
    for (const link of links) expect(link).toHaveAttribute('href', '/sign-in')
    expect(
      screen.getByText(/to have your explanation checked/),
    ).toBeInTheDocument()
  })
})

describe('what the topic page saves', () => {
  it('saves one lesson view when the page opens', () => {
    const { events } = renderTopic()
    expect(events).toEqual([
      {
        type: 'lesson_view',
        topic_id: 'py.values-and-types',
        context: 'learn',
        data: { resource: 'https://www.youtube.com/watch?v=abc123' },
      },
    ])
  })

  it('saves nothing for a topic that is still being written', () => {
    const { events } = renderTopic(fakeTopic({ status: 'planned' }), null)
    expect(events).toEqual([])
  })

  it('saves each answer with the item, its revision and the time it took', async () => {
    const { events } = renderTopic()
    await userEvent.click(screen.getByRole('radio', { name: 'Hi' }))
    await userEvent.click(
      within(screen.getByRole('region', { name: 'Quick check' })).getByRole(
        'button',
        { name: 'Check' },
      ),
    )
    expect(events.at(-1)).toEqual({
      type: 'answer',
      topic_id: 'py.values-and-types',
      item_id: 'mcq-print',
      item_rev: 1,
      context: 'practice',
      correct: true,
      duration_ms: expect.any(Number),
      data: { choice: 0, choice_text: 'Hi' },
    })
  })

  it('saves proof checks as proof, with the code that was checked', async () => {
    setFakeRunner(fakeRunner({ check: allPassed('Greets') }))
    const { events } = renderTopic()
    const build = screen.getByRole('region', { name: 'Build: Greet' })
    await userEvent.type(within(build).getByLabelText('Python code'), 'print()')
    await userEvent.click(within(build).getByRole('button', { name: 'Check' }))

    await vi.waitFor(() =>
      expect(events.at(-1)).toMatchObject({
        type: 'code_check',
        item_id: 'build-hello',
        context: 'prove',
        correct: true,
        hints_used: 0,
        data: {
          code: 'print()',
          outcome: 'done',
          passed: 1,
          total: 1,
          failing: [],
        },
      }),
    )
  })
})

describe('a checkpoint page', () => {
  beforeEach(() => {
    setFakeRunner()
  })

  /** Renders the fake checkpoint; `history` is what the server says was tried. */
  function renderCheckpoint({
    signedIn = true,
    history = [] as Attempt[],
  } = {}) {
    const content = fakeCheckpointContent()
    const loadAttempts = vi.fn((_topicId: string) => Promise.resolve(history))
    return renderTopic(content.topic, content, { signedIn, loadAttempts })
  }

  const wayThrough = () =>
    screen.getByRole('region', { name: 'Stuck? Try it in steps' })

  async function openTheSteps() {
    await userEvent.click(
      within(wayThrough()).getByRole('button', { name: 'Show the steps' }),
    )
  }

  /** Checks the build once, and waits until a result shows. */
  async function checkTheBuild() {
    const build = screen.getByRole('region', { name: 'Build: Receipt' })
    await userEvent.click(within(build).getByRole('button', { name: 'Check' }))
    await vi.waitFor(() =>
      expect(within(build).queryAllByRole('listitem').length).toBeGreaterThan(
        0,
      ),
    )
  }

  it('says what it brings together, in place of a lesson', () => {
    renderCheckpoint()
    expect(
      screen.getByText(/About 60 minutes for the whole checkpoint/),
    ).toBeInTheDocument()
    const about = screen.getByRole('region', { name: 'About this checkpoint' })
    expect(about).toHaveTextContent('Print a formatted receipt.')
    expect(
      within(about).getByRole('link', { name: 'Strings and input' }),
    ).toHaveAttribute('href', '/topic/py.strings-and-input')
    expect(
      screen.queryByRole('region', { name: 'Learn' }),
    ).not.toBeInTheDocument()
  })

  it('has the three proof checks, and keeps the steps closed until asked', async () => {
    renderCheckpoint()
    expect(
      itemHeadings(screen.getByRole('region', { name: 'Prove it' })),
    ).toEqual(['Build: Receipt', 'Debug: Cinema tickets', 'Explain it back'])
    expect(document.body).not.toHaveTextContent('SECRET MODEL ANSWER')
    const toggle = within(wayThrough()).getByRole('button', {
      name: 'Show the steps',
    })
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
    expect(
      within(wayThrough()).queryAllByRole('heading', { level: 3 }),
    ).toEqual([])

    await openTheSteps()
    expect(toggle).toHaveAttribute('aria-expanded', 'true')
    await within(wayThrough()).findByRole('heading', {
      name: 'Build: Split the bill',
    })
    expect(itemHeadings(wayThrough())).toEqual([
      'Worked example: A shop receipt',
      'Fill in the gaps: Read the inputs',
      'Fill in the gaps: Work out the totals',
      'Fill in the gaps: Print the receipt',
      'Build: Split the bill',
    ])
    expect(
      within(wayThrough()).getByText('2. Build it in steps: step 1 of 3'),
    ).toBeInTheDocument()
    expect(
      within(wayThrough()).getByText('3. Prove it on a fresh version'),
    ).toBeInTheDocument()
  })

  it('suggests the steps after two failing Checks on the build', async () => {
    setFakeRunner(fakeRunner({ check: oneFailed('Adds it all up') }))
    renderCheckpoint()
    const suggestion = () =>
      screen.queryByRole('button', { name: 'Try it in steps' })

    await checkTheBuild()
    expect(suggestion()).not.toBeInTheDocument()
    await checkTheBuild()
    await vi.waitFor(() => expect(suggestion()).toBeInTheDocument())
    expect(
      screen.getByText('Stuck on the build? You can try it in steps.'),
    ).toBeInTheDocument()

    // It opens the steps and moves there, and then it's done its job.
    const scroll = vi.spyOn(Element.prototype, 'scrollIntoView')
    await userEvent.click(suggestion()!)
    const heading = screen.getByRole('heading', {
      name: 'Stuck? Try it in steps',
    })
    expect(heading).toHaveFocus()
    expect(scroll.mock.contexts).toContain(heading)
    expect(
      within(wayThrough()).getByRole('button', { name: 'Hide the steps' }),
    ).toHaveAttribute('aria-expanded', 'true')
    expect(suggestion()).not.toBeInTheDocument()
  })

  it('stops suggesting the steps once the build passes', async () => {
    const runner = setFakeRunner(
      fakeRunner({ check: oneFailed('Adds it all up') }),
    )
    renderCheckpoint()
    await checkTheBuild()
    await checkTheBuild()
    await screen.findByRole('button', { name: 'Try it in steps' })

    runner.check.mockResolvedValue(allPassed('Adds it all up'))
    await checkTheBuild()
    await vi.waitFor(() =>
      expect(
        screen.queryByRole('button', { name: 'Try it in steps' }),
      ).not.toBeInTheDocument(),
    )
  })

  it("offers a fresh version the learner hasn't tried", async () => {
    const tried: Attempt = {
      id: 'tried',
      type: 'code_check',
      topic_id: 'py.m1.checkpoint',
      item_id: 'build-split',
      correct: false,
      occurred_at: '2026-11-05T10:00:00.000Z',
    }
    const { loadAttempts } = renderCheckpoint({ history: [tried] })
    await openTheSteps()
    expect(
      await within(wayThrough()).findByRole('heading', {
        name: 'Build: Fuel for a trip',
      }),
    ).toBeInTheDocument()
    expect(loadAttempts).toHaveBeenCalledWith('py.m1.checkpoint')
  })

  it('offers the first version when signed out, without reading history', async () => {
    const { loadAttempts } = renderCheckpoint({ signedIn: false })
    await openTheSteps()
    expect(
      within(wayThrough()).getByRole('heading', {
        name: 'Build: Split the bill',
      }),
    ).toBeInTheDocument()
    expect(loadAttempts).not.toHaveBeenCalled()
  })

  it('saves the fresh version as proof, and the steps as practice', async () => {
    setFakeRunner(fakeRunner({ check: allPassed('Splits it') }))
    const { events } = renderCheckpoint()
    await openTheSteps()
    const version = await within(wayThrough()).findByRole('region', {
      name: 'Build: Split the bill',
    })
    await userEvent.click(
      within(version).getByRole('button', { name: 'Check' }),
    )
    await vi.waitFor(() =>
      expect(events.at(-1)).toMatchObject({
        type: 'code_check',
        topic_id: 'py.m1.checkpoint',
        item_id: 'build-split',
        context: 'prove',
      }),
    )

    const step = within(wayThrough()).getByRole('region', {
      name: 'Fill in the gaps: Read the inputs',
    })
    await userEvent.click(within(step).getByRole('button', { name: 'Check' }))
    await vi.waitFor(() =>
      expect(events.at(-1)).toMatchObject({
        item_id: 'step-read',
        context: 'practice',
      }),
    )
  })
})

describe('your progress on a topic page', () => {
  beforeEach(() => {
    setFakeRunner()
  })

  /** "Nov 6", as the page writes a date. */
  const shortDate = (date: Date) =>
    date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  /** Noon on November 6, wherever the test runs. */
  const NOV_6 = new Date(2026, 10, 6, 12)

  /** A passing Check, as the server would send it back. */
  function passedCheck(item: string, topicId = 'py.values-and-types') {
    return {
      id: `check-${item}`,
      type: 'code_check',
      topic_id: topicId,
      item_id: item,
      correct: true,
      occurred_at: NOV_6.toISOString(),
    } satisfies Attempt
  }

  const proofList = () =>
    screen.findByRole('list', { name: 'Your proof so far:' })

  it('lists which proof checks have passed, and when', async () => {
    renderTopic(fakeTopic(), fakeContent(), {
      loadAttempts: vi.fn((_topicId: string) =>
        Promise.resolve([passedCheck('build-hello')]),
      ),
    })
    const items = within(await proofList()).getAllByRole('listitem')
    expect(items.map((item) => item.textContent)).toEqual([
      `✓ Build: passed on ${shortDate(NOV_6)}`,
      '○ Debug: not passed yet',
      '○ Explain: not passed yet',
    ])
  })

  it('counts a check passed on this page straight away', async () => {
    setFakeRunner(fakeRunner({ check: allPassed('Greets') }))
    const topic = fakeTopic()
    render(
      <AuthProvider auth={fakeAuth(fakeUser())}>
        <EventsProvider client={fakeEventsClient()}>
          <MemoryRouter>
            <TopicView
              topic={topic}
              content={fakeContent(topic)}
              loadAttempts={vi.fn((_topicId: string) =>
                Promise.resolve<Attempt[]>([]),
              )}
            />
          </MemoryRouter>
        </EventsProvider>
      </AuthProvider>,
    )
    expect(await proofList()).toHaveTextContent('Debug: not passed yet')

    const debug = screen.getByRole('region', {
      name: 'Debug: Fix the greeting',
    })
    await userEvent.click(within(debug).getByRole('button', { name: 'Check' }))
    await vi.waitFor(async () =>
      expect(await proofList()).toHaveTextContent(
        `Debug: passed on ${shortDate(new Date())}`,
      ),
    )
  })

  it('counts an explanation that passes straight away', async () => {
    vi.mocked(gradeExplanation).mockResolvedValue({
      status: 'graded',
      grading: {
        verdict: 'pass',
        rubric: [{ id: 'types', met: true }],
        questions: [],
      },
      ai_call_id: 'call-1',
      model: 'claude-haiku-5-5',
    })
    const topic = fakeTopic()
    render(
      <AuthProvider auth={fakeAuth(fakeUser())}>
        <EventsProvider client={fakeEventsClient()}>
          <MemoryRouter>
            <TopicView
              topic={topic}
              content={fakeContent(topic)}
              loadAttempts={vi.fn((_topicId: string) =>
                Promise.resolve<Attempt[]>([]),
              )}
            />
          </MemoryRouter>
        </EventsProvider>
      </AuthProvider>,
    )
    expect(await proofList()).toHaveTextContent('Explain: not passed yet')

    await userEvent.type(
      screen.getByLabelText('Your explanation'),
      '"5" is text; 5 is a number.',
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Check my explanation' }),
    )
    await vi.waitFor(async () =>
      expect(await proofList()).toHaveTextContent(
        `Explain: passed on ${shortDate(new Date())}`,
      ),
    )
  })

  it("counts a fresh version as the checkpoint's build", async () => {
    const content = fakeCheckpointContent()
    renderTopic(content.topic, content, {
      loadAttempts: vi.fn((_topicId: string) =>
        Promise.resolve([passedCheck('build-fuel', 'py.m1.checkpoint')]),
      ),
    })
    expect(await proofList()).toHaveTextContent(
      `Build: passed on ${shortDate(NOV_6)}`,
    )
  })

  it('shows no progress to a signed-out visitor', () => {
    const { loadAttempts } = renderTopic(fakeTopic(), fakeContent(), {
      signedIn: false,
    })
    expect(screen.queryByText('Your proof so far:')).not.toBeInTheDocument()
    expect(loadAttempts).not.toHaveBeenCalled()
  })

  it("says so when the progress can't load, and can try again", async () => {
    const loadAttempts = vi.fn((_topicId: string) =>
      Promise.resolve<Attempt[]>([]),
    )
    loadAttempts.mockRejectedValueOnce(new Error('Failed to fetch'))
    renderTopic(fakeTopic(), fakeContent(), { loadAttempts })

    await userEvent.click(
      await screen.findByRole('button', { name: 'Try again' }),
    )
    expect(await proofList()).toBeInTheDocument()
  })
})
