import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import type { Topic, TopicContent } from '../content/types.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeContent, fakeTopic } from '../test/fakeContent.tsx'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { allPassed, fakeRunner } from '../test/fakePython.ts'
import { setFakeRunner } from '../test/mockPython.ts'
import { TopicView } from './TopicPage.tsx'

vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock(
  '../components/CodeEditor.tsx',
  () => import('../test/FakeCodeEditor.tsx'),
)

/** Renders a topic for a signed-in learner (unless `signedIn` is false). */
function renderTopic(
  topic: Topic = fakeTopic(),
  content: TopicContent | null = fakeContent(topic),
  { signedIn = true } = {},
) {
  const { log, events } = recordingEventLog()
  render(
    <AuthProvider auth={fakeAuth(signedIn ? fakeUser() : null)}>
      <EventLogContext value={log}>
        <MemoryRouter>
          <TopicView topic={topic} content={content} />
        </MemoryRouter>
      </EventLogContext>
    </AuthProvider>,
  )
  return { events }
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
    expect(screen.getByText(/About 30 minutes/)).toBeInTheDocument()
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
    expect(learn).toHaveTextContent('License: CC BY 4.0')
    expect(
      within(learn).getByRole('link', { name: 'The Python tutorial: numbers' }),
    ).toHaveAttribute(
      'href',
      'https://docs.python.org/3/tutorial/introduction.html',
    )
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
    expect(screen.getByRole('link', { name: 'Sign in' })).toHaveAttribute(
      'href',
      '/sign-in',
    )
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
