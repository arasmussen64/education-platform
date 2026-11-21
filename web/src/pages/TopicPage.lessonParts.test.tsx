import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { MDXComponents } from 'mdx/types'
import type { ComponentType, ReactNode } from 'react'
import { MemoryRouter } from 'react-router'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { EventLogContext } from '../events/eventLogContext.ts'
import { READING_WORDS_A_MINUTE } from '../parts/estimates.ts'
import { fakeAuth } from '../test/fakeAuth.ts'
import { fakeContent, fakeTopic } from '../test/fakeContent.tsx'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { TopicView } from './TopicPage.tsx'

vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock(
  '../components/CodeEditor.tsx',
  () => import('../test/FakeCodeEditor.tsx'),
)

type Tag = ComponentType<{
  children?: ReactNode
  item?: string
  index?: number
}>

/** A lesson of two sections, each ending at a question, then the rest. */
function LongLesson({ components = {} }: { components?: MDXComponents }) {
  const Intro = components.Intro as Tag
  const Check = components.Check as Tag
  const Resource = components.Resource as Tag
  const Recap = components.Recap as Tag
  return (
    <>
      <Intro>
        <p>The first idea.</p>
        <Check item="mcq-print" />
        <p>The second idea.</p>
        <Check item="predict-two-prints" />
      </Intro>
      <Resource index={0} />
      <Recap>
        <p>Both ideas again.</p>
      </Recap>
    </>
  )
}

/** Half an hour of reading, then a question. */
const section = (check: string) => ({
  words: 30 * READING_WORDS_A_MINUTE,
  blocks: 2,
  check,
})

/** Renders the topic page, opened at a place as a link would (ADR-0025). */
function renderAt(anchor: string) {
  window.history.replaceState(null, '', `#${anchor}`)
  const content = {
    ...fakeContent(fakeTopic({ estimated_minutes: 200 })),
    Lesson: LongLesson,
    lessonChecks: ['mcq-print', 'predict-two-prints'],
    lessonShape: {
      sections: [section('mcq-print'), section('predict-two-prints')],
      recapWords: 0,
    },
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

describe('a long lesson, a part at a time (ADR-0025, amended 2026-11-21)', () => {
  it('opens at its first section, without the rest', () => {
    renderAt('learn')
    const learn = screen.getByRole('region', {
      name: 'Learn: section 1 of 2',
    })
    expect(within(learn).getByText('The first idea.')).toBeInTheDocument()
    expect(screen.queryByText('The second idea.')).not.toBeInTheDocument()
    expect(screen.queryByText('Both ideas again.')).not.toBeInTheDocument()
    expect(
      screen.getByText(/^Part 1 of \d · about 30 min$/),
    ).toBeInTheDocument()
  })

  it('keeps each place its number, whichever part shows it', () => {
    renderAt('place-lesson-3')
    // The third block of the lesson is the second section's first.
    expect(screen.getByText('The second idea.')).toHaveAttribute(
      'id',
      'place-lesson-3',
    )
    expect(screen.queryByText('The first idea.')).not.toBeInTheDocument()
  })

  it('ends with the resource and the recap, in a part of their own', () => {
    renderAt('place-recap')
    const last = screen.getByRole('region', {
      name: 'Learn: the video and the recap',
    })
    expect(within(last).getByText('Both ideas again.')).toBeInTheDocument()
    expect(screen.queryByText('The second idea.')).not.toBeInTheDocument()
  })

  it('moves on from one section to the next with the Next button', async () => {
    renderAt('learn')
    await userEvent.click(
      screen.getByRole('button', { name: /Next: Part 2, Learn: section 2/ }),
    )
    expect(screen.getByText('The second idea.')).toBeInTheDocument()
    expect(screen.queryByText('The first idea.')).not.toBeInTheDocument()
  })
})
