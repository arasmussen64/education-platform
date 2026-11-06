import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import type { Topic, TopicContent } from '../content/types.ts'
import { fakeContent, fakeTopic } from '../test/fakeContent.tsx'
import { setFakeRunner } from '../test/mockPython.ts'
import { TopicView } from './TopicPage.tsx'

vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock(
  '../components/CodeEditor.tsx',
  () => import('../test/FakeCodeEditor.tsx'),
)

function renderTopic(
  topic: Topic = fakeTopic(),
  content: TopicContent | null = fakeContent(topic),
) {
  setFakeRunner()
  render(
    <MemoryRouter>
      <TopicView topic={topic} content={content} />
    </MemoryRouter>,
  )
}

/** The text of each item heading in a section, in order. */
function itemHeadings(section: HTMLElement) {
  return within(section)
    .getAllByRole('heading', { level: 3 })
    .map((heading) => heading.textContent)
}

describe('the topic page', () => {
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
})
