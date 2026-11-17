import { render, screen, within } from '@testing-library/react'
import type { MDXComponents } from 'mdx/types'
import type { ComponentType, ReactNode } from 'react'
import { MemoryRouter } from 'react-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { EventLogContext } from '../events/eventLogContext.ts'
import { fakeAuth } from '../test/fakeAuth.ts'
import { fakeContent } from '../test/fakeContent.tsx'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { TopicView } from './TopicPage.tsx'

vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock(
  '../components/CodeEditor.tsx',
  () => import('../test/FakeCodeEditor.tsx'),
)

type Tag = ComponentType<{ children?: ReactNode; item?: string }>

/** A lesson that asks the topic's multiple-choice question itself. */
function LessonWithCheck({ components = {} }: { components?: MDXComponents }) {
  const Intro = components.Intro as Tag
  const Check = components.Check as Tag
  return (
    <Intro>
      <p>Watch how a program prints.</p>
      <Check item="mcq-print" />
    </Intro>
  )
}

/** Renders the topic page, opened at a place as a link would (ADR-0025). */
function renderAt(anchor: string) {
  window.history.replaceState(null, '', `#${anchor}`)
  const content = {
    ...fakeContent(),
    Lesson: LessonWithCheck,
    lessonChecks: ['mcq-print'],
  }
  const { log } = recordingEventLog()
  render(
    <AuthProvider auth={fakeAuth(null)}>
      <EventLogContext value={log}>
        <MemoryRouter>
          <TopicView topic={content.topic} content={content} />
        </MemoryRouter>
      </EventLogContext>
    </AuthProvider>,
  )
}

afterEach(() => {
  window.history.replaceState(null, '', window.location.pathname)
})

describe('a question the lesson asks (ADR-0026)', () => {
  it('shows in the lesson', () => {
    renderAt('learn')
    const learn = screen.getByRole('region', { name: 'Learn' })
    expect(
      within(learn).getByRole('heading', { name: 'Quick check' }),
    ).toBeInTheDocument()
  })

  it('is left out of the practice ladder', () => {
    renderAt('practice')
    const practice = screen.getByRole('region', { name: 'Practice' })
    expect(
      within(practice).queryByRole('heading', { name: 'Quick check' }),
    ).not.toBeInTheDocument()
    // The ladder counts what it shows: four of the topic's five items.
    expect(within(practice).getByText('Practice 1 of 4')).toBeInTheDocument()
  })
})
