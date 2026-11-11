import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { fetchStepsOpened } from '../checkpoints/stepsOpened.ts'
import { getTopic } from '../content/content.ts'
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
// When the learner opened a checkpoint's steps comes from the server too:
// never, unless a test says otherwise.
vi.mock('../checkpoints/stepsOpened.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../checkpoints/stepsOpened.ts')>()),
  fetchStepsOpened: vi.fn(),
}))
beforeEach(() => {
  vi.mocked(fetchStepsOpened).mockResolvedValue([])
})

/** Noon on November 6, wherever the test runs. */
const NOV_6 = new Date(2026, 10, 6, 12)

/** A passing Check, as the server would send it back. */
function passedCheck(item: string, topicId = 'py.values-and-types'): Attempt {
  return {
    id: `check-${topicId}-${item}`,
    type: 'code_check',
    topic_id: topicId,
    item_id: item,
    correct: true,
    occurred_at: NOV_6.toISOString(),
  }
}

/** A graded explanation that passed. */
function explainPassed(topicId = 'py.values-and-types'): Attempt {
  return {
    id: `explain-${topicId}`,
    type: 'explain_submit',
    topic_id: topicId,
    item_id: 'explain',
    correct: true,
    occurred_at: NOV_6.toISOString(),
  }
}

/**
 * Passing proof checks for everything a topic builds on, so the topic isn't
 * Locked (F8). The prerequisites are real topics, with real proof checks.
 */
function unlocked(topic: Topic): Attempt[] {
  return topic.prerequisites.flatMap((id) => {
    const prerequisite = getTopic(id)
    if (!prerequisite) return []
    return [
      passedCheck(prerequisite.prove.build ?? '', id),
      passedCheck(prerequisite.prove.debug ?? '', id),
      explainPassed(id),
    ]
  })
}

/**
 * Renders a topic for a signed-in learner (unless `signedIn` is false), with
 * what it builds on already learned, so the whole page shows.
 */
function renderTopic(
  topic: Topic = fakeTopic(),
  content: TopicContent | null = fakeContent(topic),
  {
    signedIn = true,
    loadAttempts = vi.fn((_topicId: string) =>
      Promise.resolve<Attempt[]>(unlocked(topic)),
    ),
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
    // With more than one track, the header names the track too.
    expect(
      screen.getByText('Python Foundations · Module 1: First programs'),
    ).toBeInTheDocument()
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

  it("mixes in a question from an earlier topic, after this topic's own (F5)", async () => {
    const earlier = fakeTopic({
      id: 'py.programs-and-print',
      title: 'Programs and print',
      prerequisites: [],
    })
    const { log, events } = recordingEventLog()
    render(
      <AuthProvider auth={fakeAuth(fakeUser())}>
        <EventLogContext value={log}>
          <MemoryRouter>
            <TopicView
              topic={fakeTopic()}
              content={fakeContent()}
              interleaved={{
                content: fakeContent(earlier),
                itemId: 'mcq-print',
              }}
              loadAttempts={vi.fn((_topicId: string) =>
                Promise.resolve(unlocked(fakeTopic())),
              )}
            />
          </MemoryRouter>
        </EventLogContext>
      </AuthProvider>,
    )
    const practice = screen.getByRole('region', { name: 'Practice' })
    expect(itemHeadings(practice)).toEqual([
      'Worked example: Say hello',
      'Quick check',
      'Predict the output',
      'Quick check',
      'Fill in the gaps: Say hello',
      'Write it: Say hello',
    ])
    expect(
      within(practice).getByText('Practice 4 of 6 · from Programs and print'),
    ).toBeInTheDocument()
    expect(practice).toHaveTextContent('One question is from an earlier topic')

    // Its answer is saved under the earlier topic, where it counts.
    const borrowed = screen.getAllByRole('region', { name: 'Quick check' })[1]!
    await userEvent.click(within(borrowed).getByRole('radio', { name: 'Hi' }))
    await userEvent.click(
      within(borrowed).getByRole('button', { name: 'Check' }),
    )
    expect(events.at(-1)).toMatchObject({
      type: 'answer',
      topic_id: 'py.programs-and-print',
      item_id: 'mcq-print',
      context: 'practice',
      correct: true,
    })
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

  /**
   * Renders the fake checkpoint, with its module's topics learned; `history`
   * is what else the server says was tried.
   */
  function renderCheckpoint({
    signedIn = true,
    history = [] as Attempt[],
  } = {}) {
    const content = fakeCheckpointContent()
    const loadAttempts = vi.fn((_topicId: string) =>
      Promise.resolve([...unlocked(content.topic), ...history]),
    )
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

  /**
   * Renders the fake checkpoint with a real event log, so a Check passed
   * on the page counts toward its progress straight away.
   */
  function renderSavingCheckpoint() {
    const content = fakeCheckpointContent()
    render(
      <AuthProvider auth={fakeAuth(fakeUser())}>
        <EventsProvider client={fakeEventsClient()}>
          <MemoryRouter>
            <TopicView
              topic={content.topic}
              content={content}
              loadAttempts={vi.fn((_topicId: string) =>
                Promise.resolve(unlocked(content.topic)),
              )}
            />
          </MemoryRouter>
        </EventsProvider>
      </AuthProvider>,
    )
  }

  /** Waits until the learner's progress has loaded. */
  const progressLoaded = () =>
    screen.findByRole('list', { name: 'Your proof so far:' })

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

  // The explain prompt can walk through code much like the build's, so a
  // checkpoint keeps it out of sight until the build has passed (ADR-0012,
  // amended 2026-11-10).
  describe('its explain check', () => {
    const PROMPT = 'How does your receipt program work?'
    const CLOSED = 'Explain it back opens once your build passes.'

    const explainCard = () =>
      screen.getByRole('region', { name: 'Explain it back' })

    /** Nothing of the explain check but its heading and why it's closed. */
    function expectClosed() {
      expect(explainCard()).toHaveTextContent(CLOSED)
      expect(document.body).not.toHaveTextContent(PROMPT)
      expect(screen.queryByLabelText('Your explanation')).toBeNull()
    }

    function expectOpen() {
      expect(explainCard()).toHaveTextContent(PROMPT)
      expect(explainCard()).not.toHaveTextContent(CLOSED)
      expect(screen.getByLabelText('Your explanation')).toBeInTheDocument()
    }

    it('stays closed, prompt and all, until the build passes on the page', async () => {
      const runner = setFakeRunner(
        fakeRunner({ check: oneFailed('Adds it all up') }),
      )
      renderSavingCheckpoint()
      await progressLoaded()
      expectClosed()

      // A failing Check doesn't open it.
      await checkTheBuild()
      expectClosed()

      // A passing one does, with no reload.
      runner.check.mockResolvedValue(allPassed('Adds it all up'))
      await checkTheBuild()
      await vi.waitFor(expectOpen)
    })

    it('opens when a fresh version passes on the page, as that counts as the build', async () => {
      setFakeRunner(fakeRunner({ check: allPassed('Splits it') }))
      renderSavingCheckpoint()
      await progressLoaded()
      expectClosed()

      await openTheSteps()
      const version = await within(wayThrough()).findByRole('region', {
        name: 'Build: Split the bill',
      })
      await userEvent.click(
        within(version).getByRole('button', { name: 'Check' }),
      )
      await vi.waitFor(expectOpen)
    })

    it.each([
      ['the build', 'build-receipt'],
      ['a fresh version', 'build-fuel'],
    ])(
      'is open from the start once %s passed on an earlier visit',
      async (_which, item) => {
        renderCheckpoint({ history: [passedCheck(item, 'py.m1.checkpoint')] })
        await progressLoaded()
        expectOpen()
      },
    )

    it("doesn't open for the debug or the steps, only the build", async () => {
      renderCheckpoint({
        history: [
          passedCheck('debug-tickets', 'py.m1.checkpoint'),
          passedCheck('step-print', 'py.m1.checkpoint'),
        ],
      })
      await progressLoaded()
      expectClosed()
    })

    it("keeps what's typed once it's open, and can then be passed", async () => {
      vi.mocked(gradeExplanation).mockResolvedValue({
        status: 'graded',
        grading: {
          verdict: 'pass',
          rubric: [{ id: 'parts', met: true }],
          questions: [],
        },
        ai_call_id: 'call-1',
        model: 'claude-haiku-5-5',
      })
      setFakeRunner(fakeRunner({ check: allPassed('Adds it all up') }))
      renderSavingCheckpoint()
      await progressLoaded()
      await checkTheBuild()
      await vi.waitFor(expectOpen)

      const typed = 'It reads the prices, adds them up, then prints.'
      await userEvent.type(screen.getByLabelText('Your explanation'), typed)

      // Another Check changes the progress again. The open check must stay
      // the same one, not start over with an empty box.
      const debug = screen.getByRole('region', {
        name: 'Debug: Cinema tickets',
      })
      await userEvent.click(
        within(debug).getByRole('button', { name: 'Check' }),
      )
      await vi.waitFor(async () =>
        expect(await progressLoaded()).toHaveTextContent(/Debug: passed on/),
      )
      expect(screen.getByLabelText('Your explanation')).toHaveValue(typed)

      await userEvent.click(
        screen.getByRole('button', { name: 'Check my explanation' }),
      )
      await vi.waitFor(async () =>
        expect(await progressLoaded()).toHaveTextContent(/Explain: passed on/),
      )
      // All three have passed, so the checkpoint has.
      expect(screen.getByTestId('topic-state')).toHaveTextContent('Passed')
      expectOpen()
    })

    it('stays closed while the progress is loading, and says so', () => {
      const content = fakeCheckpointContent()
      renderTopic(content.topic, content, {
        // Never answers.
        loadAttempts: vi.fn(
          (_topicId: string) => new Promise<Attempt[]>(() => {}),
        ),
      })
      expectClosed()
      expect(explainCard()).toHaveTextContent('Checking whether it has…')
    })

    it("stays closed when the progress can't load, and opens after a retry", async () => {
      const content = fakeCheckpointContent()
      // Every read fails until the connection is "back". (More than the
      // progress reads the history, so failing only the first read wouldn't
      // do.)
      let offline = true
      const loadAttempts = vi.fn((_topicId: string) =>
        offline
          ? Promise.reject<Attempt[]>(new Error('Failed to fetch'))
          : Promise.resolve([
              ...unlocked(content.topic),
              passedCheck('build-receipt', 'py.m1.checkpoint'),
            ]),
      )
      renderTopic(content.topic, content, { loadAttempts })

      await vi.waitFor(() =>
        expect(explainCard()).toHaveTextContent(
          "Your progress here couldn't load, so the page can't tell whether it has.",
        ),
      )
      expectClosed()

      offline = false
      await userEvent.click(
        within(explainCard()).getByRole('button', { name: 'Try again' }),
      )
      await vi.waitFor(expectOpen)
    })

    it('stays closed for a signed-out visitor, whose build is never saved', async () => {
      setFakeRunner(fakeRunner({ check: allPassed('Adds it all up') }))
      renderCheckpoint({ signedIn: false })
      expectClosed()
      expect(
        within(explainCard()).getByRole('link', { name: 'Sign in' }),
      ).toHaveAttribute('href', '/sign-in')

      await checkTheBuild()
      expectClosed()
    })

    it('leaves a regular topic alone: its prompt shows from the start', async () => {
      renderTopic()
      const prompt = 'Why is "5" different from 5?'
      // While the progress is still loading...
      expect(explainCard()).toHaveTextContent(prompt)
      // ...and once it's known that nothing has passed yet.
      expect(await progressLoaded()).toHaveTextContent('Build: not passed yet')
      expect(explainCard()).toHaveTextContent(prompt)
      expect(document.body).not.toHaveTextContent(CLOSED)
      expect(screen.getByLabelText('Your explanation')).toBeInTheDocument()
    })
  })

  // The steps hand over most of the build's own program, so once they've
  // been opened, a pass of that build no longer proves it; a fresh version
  // does (ADR-0012, amended 2026-11-11).
  describe('once the steps are opened', () => {
    const CHECKPOINT = 'py.m1.checkpoint'
    const NOTICE = /passing the build below no longer counts as your proof/
    const PROMPT = 'How does your receipt program work?'
    const FRESH_VERSION_NEEDED =
      "Since you've opened the steps, that means a fresh version"

    const notice = () => screen.queryByText(NOTICE)
    const explainCard = () =>
      screen.getByRole('region', { name: 'Explain it back' })

    /** Opened on an earlier visit, at this time. */
    function openedBefore(occurred_at: string) {
      vi.mocked(fetchStepsOpened).mockResolvedValue([
        { topic_id: CHECKPOINT, occurred_at },
      ])
    }

    // Only Date is faked: the timers that waitFor and userEvent rely on stay
    // real.
    beforeEach(() => {
      vi.useFakeTimers({ toFake: ['Date'] })
      vi.setSystemTime(new Date('2026-11-11T12:00:00.000Z'))
      return () => vi.useRealTimers()
    })

    it('says so where the steps are offered, before they open', () => {
      renderCheckpoint()
      expect(wayThrough()).toHaveTextContent(
        'So once you open them, passing the build above no longer counts as your proof: a fresh version does.',
      )
      expect(notice()).not.toBeInTheDocument()
    })

    it("saves the first opening on each visit, as a hint on the checkpoint's build", async () => {
      const { events } = renderCheckpoint()
      await openTheSteps()
      await userEvent.click(
        within(wayThrough()).getByRole('button', { name: 'Hide the steps' }),
      )
      await openTheSteps()
      const hints = events.filter((event) => event.type === 'hint')
      expect(hints).toHaveLength(1)
      expect(hints[0]).toMatchObject({
        topic_id: CHECKPOINT,
        item_id: 'build-receipt',
        context: 'prove',
        data: { source: 'steps' },
      })
    })

    it('says by the build that a fresh version proves it now, and goes there', async () => {
      renderCheckpoint()
      await openTheSteps()
      await userEvent.click(
        within(wayThrough()).getByRole('button', { name: 'Hide the steps' }),
      )
      // Above the build, where the learner would come back to finish it.
      const proveIt = screen.getByRole('region', { name: 'Prove it' })
      expect(within(proveIt).getByText(NOTICE)).toBeInTheDocument()

      const scroll = vi.spyOn(Element.prototype, 'scrollIntoView')
      await userEvent.click(
        screen.getByRole('button', { name: 'Prove it on a fresh version' }),
      )
      const heading = screen.getByRole('heading', {
        name: 'Stuck? Try it in steps',
      })
      expect(heading).toHaveFocus()
      expect(scroll.mock.contexts).toContain(heading)
      expect(
        within(wayThrough()).getByRole('button', { name: 'Hide the steps' }),
      ).toHaveAttribute('aria-expanded', 'true')
    })

    it("doesn't count a pass of the build after them, but does a fresh version's", async () => {
      setFakeRunner(fakeRunner({ check: allPassed('Adds it all up') }))
      renderSavingCheckpoint()
      await progressLoaded()
      await openTheSteps()

      // Five minutes later, the learner goes back up and passes the build.
      vi.setSystemTime(new Date('2026-11-11T12:05:00.000Z'))
      await checkTheBuild()
      expect(await progressLoaded()).toHaveTextContent('Build: not passed yet')
      expect(notice()).toBeInTheDocument()
      expect(explainCard()).toHaveTextContent(FRESH_VERSION_NEEDED)
      expect(document.body).not.toHaveTextContent(PROMPT)

      const version = await within(wayThrough()).findByRole('region', {
        name: 'Build: Split the bill',
      })
      await userEvent.click(
        within(version).getByRole('button', { name: 'Check' }),
      )
      await vi.waitFor(async () =>
        expect(await progressLoaded()).toHaveTextContent(/Build: passed on/),
      )
      expect(notice()).not.toBeInTheDocument()
      expect(explainCard()).toHaveTextContent(PROMPT)
    })

    it('remembers the steps were opened on an earlier visit', async () => {
      setFakeRunner(fakeRunner({ check: oneFailed('Adds it all up') }))
      openedBefore('2026-11-05T12:00:00.000Z')
      // The build passed after that, on Nov 6.
      renderCheckpoint({ history: [passedCheck('build-receipt', CHECKPOINT)] })
      expect(await progressLoaded()).toHaveTextContent('Build: not passed yet')
      expect(notice()).toBeInTheDocument()
      expect(explainCard()).toHaveTextContent(FRESH_VERSION_NEEDED)
      expect(document.body).not.toHaveTextContent(PROMPT)

      // The notice already points at the steps, so the suggestion to try
      // them doesn't come as well.
      await checkTheBuild()
      await checkTheBuild()
      expect(
        screen.queryByRole('button', { name: 'Try it in steps' }),
      ).not.toBeInTheDocument()
    })

    it('still counts a build passed before they were opened', async () => {
      openedBefore('2026-11-07T12:00:00.000Z')
      // Passed on Nov 6, the day before.
      renderCheckpoint({ history: [passedCheck('build-receipt', CHECKPOINT)] })
      expect(await progressLoaded()).toHaveTextContent(/Build: passed on/)
      expect(notice()).not.toBeInTheDocument()
      expect(explainCard()).toHaveTextContent(PROMPT)
    })

    it('counts the build in history with no record of the steps, as before', async () => {
      // Openings were first saved on 2026-11-11: older history has none.
      renderCheckpoint({ history: [passedCheck('build-receipt', CHECKPOINT)] })
      expect(await progressLoaded()).toHaveTextContent(/Build: passed on/)
      expect(notice()).not.toBeInTheDocument()
    })
  })
})

describe('your progress on a topic page', () => {
  beforeEach(() => {
    setFakeRunner()
  })

  /** "Nov 6", as the page writes a date. */
  const shortDate = (date: Date) =>
    date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })

  const proofList = () =>
    screen.findByRole('list', { name: 'Your proof so far:' })

  it('lists which proof checks have passed, and when', async () => {
    renderTopic(fakeTopic(), fakeContent(), {
      loadAttempts: vi.fn((_topicId: string) =>
        Promise.resolve([...unlocked(fakeTopic()), passedCheck('build-hello')]),
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
                Promise.resolve(unlocked(topic)),
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
                Promise.resolve(unlocked(topic)),
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
        Promise.resolve([
          ...unlocked(content.topic),
          passedCheck('build-fuel', 'py.m1.checkpoint'),
        ]),
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
      Promise.resolve(unlocked(fakeTopic())),
    )
    loadAttempts.mockRejectedValueOnce(new Error('Failed to fetch'))
    renderTopic(fakeTopic(), fakeContent(), { loadAttempts })

    await userEvent.click(
      await screen.findByRole('button', { name: 'Try again' }),
    )
    expect(await proofList()).toBeInTheDocument()
  })
})

describe('topic states and gating', () => {
  beforeEach(() => {
    setFakeRunner()
  })

  const stateLine = () => screen.findByTestId('topic-state')
  const lockedNotice = () =>
    screen.findByRole('complementary', { name: 'Locked' })

  it('locks a topic until what it builds on is learned: lesson only', async () => {
    // Nothing learned yet, so the prerequisite isn't either.
    renderTopic(fakeTopic(), fakeContent(), {
      loadAttempts: vi.fn((_topicId: string) => Promise.resolve<Attempt[]>([])),
    })
    const notice = await lockedNotice()
    expect(notice).toHaveTextContent(/opens once you've learned/)
    expect(
      within(notice).getByRole('link', { name: 'Programs and print' }),
    ).toHaveAttribute('href', '/topic/py.programs-and-print')
    expect(await stateLine()).toHaveTextContent('Locked')

    expect(screen.getByRole('region', { name: 'Learn' })).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Practice' })).toBeNull()
    expect(screen.queryByRole('region', { name: 'Prove it' })).toBeNull()
    expect(screen.queryByRole('button', { name: 'Prove it now' })).toBeNull()
  })

  it('is Available once what it builds on is learned, and offers Prove it now', async () => {
    renderTopic()
    expect(await stateLine()).toHaveTextContent('Available')
    expect(screen.getByRole('region', { name: 'Practice' })).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Prove it now' }))
    expect(screen.queryByRole('region', { name: 'Learn' })).toBeNull()
    expect(screen.queryByRole('region', { name: 'Practice' })).toBeNull()
    expect(screen.getByRole('region', { name: 'Prove it' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Prove it' })).toHaveFocus()
    expect(screen.queryByRole('button', { name: 'Prove it now' })).toBeNull()

    await userEvent.click(
      screen.getByRole('button', { name: 'Show them anyway' }),
    )
    expect(screen.getByRole('region', { name: 'Learn' })).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Practice' })).toBeInTheDocument()
  })

  it('is In progress once started, with no shortcut offered', async () => {
    const topic = fakeTopic()
    renderTopic(topic, fakeContent(topic), {
      loadAttempts: vi.fn((_topicId: string) =>
        Promise.resolve([...unlocked(topic), passedCheck('build-hello')]),
      ),
    })
    expect(await stateLine()).toHaveTextContent('In progress')
    expect(screen.queryByRole('button', { name: 'Prove it now' })).toBeNull()
  })

  it('says when, once all three checks have passed', async () => {
    const topic = fakeTopic()
    renderTopic(topic, fakeContent(topic), {
      loadAttempts: vi.fn((_topicId: string) =>
        Promise.resolve([
          ...unlocked(topic),
          passedCheck('build-hello'),
          passedCheck('debug-hello'),
          explainPassed(),
        ]),
      ),
    })
    expect(await stateLine()).toHaveTextContent('Learned on Nov 6')
  })

  it('locks a checkpoint the same way', async () => {
    const content = fakeCheckpointContent()
    renderTopic(content.topic, content, {
      loadAttempts: vi.fn((_topicId: string) => Promise.resolve<Attempt[]>([])),
    })
    const notice = await lockedNotice()
    expect(notice).toHaveTextContent(/This checkpoint opens once/)
    expect(
      within(notice).getByRole('link', { name: 'Arithmetic' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('region', { name: 'About this checkpoint' }),
    ).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Prove it' })).toBeNull()
    expect(
      screen.queryByRole('region', { name: 'Stuck? Try it in steps' }),
    ).toBeNull()
  })

  it("doesn't gate a signed-out visitor, whose progress it can't know", () => {
    renderTopic(fakeTopic(), fakeContent(), { signedIn: false })
    expect(screen.queryByTestId('topic-state')).toBeNull()
    expect(screen.getByRole('region', { name: 'Practice' })).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Prove it' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Prove it now' })).toBeNull()
  })
})

describe('your place on a long topic', () => {
  beforeEach(() => {
    setFakeRunner()
  })

  /** An answer to a recall question, as the server would send it back. */
  function answered(
    item: string,
    correct: boolean,
    topicId = 'py.values-and-types',
  ): Attempt {
    return {
      id: `answer-${topicId}-${item}-${correct}`,
      type: 'answer',
      topic_id: topicId,
      item_id: item,
      correct,
      occurred_at: NOV_6.toISOString(),
    }
  }

  const outline = () =>
    screen.getByRole('navigation', { name: 'Your place in this topic' })

  it('lists the lesson, every practice item with its state, and the proof checks', async () => {
    renderTopic(fakeTopic(), fakeContent(), {
      loadAttempts: vi.fn((_topicId: string) =>
        Promise.resolve([
          ...unlocked(fakeTopic()),
          passedCheck('example-hello'),
          answered('mcq-print', true),
          answered('predict-print', false),
        ]),
      ),
    })
    const nav = outline()
    expect(await within(nav).findByText(/2 of 5 done/)).toBeInTheDocument()
    // Each item is a link to its card, named with its state (F9: words,
    // not only a color).
    expect(
      within(nav).getByRole('link', { name: 'Practice 1: Done ✓' }),
    ).toHaveAttribute('href', '#place-item-py.values-and-types-example-hello')
    expect(
      within(nav).getByRole('link', {
        name: 'Practice 3: Tried, not right yet',
      }),
    ).toBeInTheDocument()
    expect(
      within(nav).getByRole('link', { name: 'Practice 4: not done yet' }),
    ).toBeInTheDocument()
    expect(
      within(nav).getByRole('link', { name: 'Next not done: Practice 3' }),
    ).toHaveAttribute('href', '#place-item-py.values-and-types-predict-print')
    // The lesson's parts and the proof checks are places too.
    expect(
      within(nav).getByRole('link', { name: 'The lesson' }),
    ).toHaveAttribute('href', '#place-lesson-1')
    expect(document.getElementById('place-lesson-1')).toBeInTheDocument()
    expect(document.getElementById('place-recap')).toBeInTheDocument()
    expect(
      within(nav).getByRole('link', { name: 'Build: not passed yet' }),
    ).toHaveAttribute('href', '#place-prove-build')
    expect(document.getElementById('place-prove-build')).toBeInTheDocument()
  })

  it('shows the places without states to a signed-out visitor', () => {
    renderTopic(fakeTopic(), fakeContent(), { signedIn: false })
    const nav = outline()
    expect(within(nav).queryByText(/of 5 done/)).toBeNull()
    expect(
      within(nav).getByRole('link', { name: 'Practice 2: not done yet' }),
    ).toBeInTheDocument()
    expect(within(nav).queryByText(/Next not done/)).toBeNull()
  })

  it('folds away an item already got right, until asked, and marks it done', async () => {
    renderTopic(fakeTopic(), fakeContent(), {
      loadAttempts: vi.fn((_topicId: string) =>
        Promise.resolve([
          ...unlocked(fakeTopic()),
          answered('mcq-print', true),
        ]),
      ),
    })
    const quick = screen.getByRole('region', { name: 'Quick check' })
    expect(
      await within(quick).findByText('Practice 2 of 5 · Done ✓'),
    ).toBeInTheDocument()
    expect(within(quick).queryByRole('radio')).toBeNull()
    await userEvent.click(
      within(quick).getByRole('button', { name: 'Show it again' }),
    )
    expect(within(quick).getAllByRole('radio').length).toBeGreaterThan(0)
    // An item only tried stays open.
    const predict = screen.getByRole('region', { name: 'Predict the output' })
    expect(
      within(predict).getByRole('button', { name: 'Check' }),
    ).toBeInTheDocument()
  })

  it('marks an item done as soon as it is answered right, and keeps it open', async () => {
    const topic = fakeTopic()
    render(
      <AuthProvider auth={fakeAuth(fakeUser())}>
        <EventsProvider client={fakeEventsClient()}>
          <MemoryRouter>
            <TopicView
              topic={topic}
              content={fakeContent(topic)}
              loadAttempts={vi.fn((_topicId: string) =>
                Promise.resolve(unlocked(topic)),
              )}
            />
          </MemoryRouter>
        </EventsProvider>
      </AuthProvider>,
    )
    const nav = outline()
    expect(await within(nav).findByText(/0 of 5 done/)).toBeInTheDocument()
    const quick = screen.getByRole('region', { name: 'Quick check' })
    await userEvent.click(within(quick).getByRole('radio', { name: 'Hi' }))
    await userEvent.click(within(quick).getByRole('button', { name: 'Check' }))
    expect(
      await within(quick).findByText('Practice 2 of 5 · Done ✓'),
    ).toBeInTheDocument()
    expect(within(quick).getAllByRole('radio').length).toBeGreaterThan(0)
    expect(within(nav).getByText(/1 of 5 done/)).toBeInTheDocument()
    expect(
      within(nav).getByRole('link', { name: 'Next not done: Practice 1' }),
    ).toBeInTheDocument()
  })

  it('offers to continue where the last visit stopped', () => {
    localStorage.setItem(
      'place:py.values-and-types',
      'place-item-py.values-and-types-fill-hello',
    )
    renderTopic()
    expect(
      within(outline()).getByRole('link', {
        name: 'Continue where you left off: Practice 4',
      }),
    ).toHaveAttribute('href', '#place-item-py.values-and-types-fill-hello')
  })

  it('offers nothing to continue on a first visit', () => {
    renderTopic()
    expect(
      within(outline()).queryByText(/Continue where you left off/),
    ).toBeNull()
  })
})

// Every fixture here is dated Nov 6, 2026, and a topic proved that day has a
// review due a few days later. These tests aren't about reviews, so they run
// at the end of that day, whatever day it really is (as progress.test does).
// Only Date is faked: the timers that waitFor and userEvent rely on stay real.
beforeEach(() => {
  vi.useFakeTimers({ toFake: ['Date'] })
  vi.setSystemTime(new Date(2026, 10, 6, 23))
  return () => vi.useRealTimers()
})
