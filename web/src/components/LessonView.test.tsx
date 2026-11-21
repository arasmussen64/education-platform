import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { MDXComponents } from 'mdx/types'
import type { ComponentType, ReactNode } from 'react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import type { TopicContent } from '../content/types.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { fakeAuth } from '../test/fakeAuth.ts'
import { fakeContent, MCQ } from '../test/fakeContent.tsx'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { LessonView } from './LessonView.tsx'

type Tag = ComponentType<Record<string, unknown> & { children?: ReactNode }>

/**
 * Stands in for a compiled lesson.mdx that uses the building blocks of
 * ADR-0026, as content/README.md shows them.
 */
function BlocksLesson({ components = {} }: { components?: MDXComponents }) {
  const tag = (name: string) => components[name] as Tag
  const [Intro, Resource, Recap, Check, Puzzle, Story] = [
    'Intro',
    'Resource',
    'Recap',
    'Check',
    'Puzzle',
    'Story',
  ].map(tag)
  return (
    <>
      <Intro>
        <Puzzle question="Why does `print` start a new line?">
          <p>Because its end is a newline unless you say otherwise.</p>
        </Puzzle>
        <p>Watch how a program prints.</p>
        <Check item="mcq-print" />
      </Intro>
      <Resource index={0} />
      <Story
        title="The report that printed nothing"
        source="https://example.com/postmortem"
        sourceTitle="The printer postmortem"
        license="linked, not copied"
      >
        <p>A nightly report printed an empty page for a week.</p>
      </Story>
      <Recap>
        <p>print() shows text in the output.</p>
      </Recap>
    </>
  )
}

function renderLesson(content: TopicContent = fakeContent()) {
  const { log, events } = recordingEventLog()
  render(
    <AuthProvider auth={fakeAuth(null)}>
      <EventLogContext value={log}>
        <MemoryRouter>
          <LessonView Lesson={BlocksLesson} content={content} />
        </MemoryRouter>
      </EventLogContext>
    </AuthProvider>,
  )
  return { events }
}

describe('a question inside the lesson (<Check>)', () => {
  it('is graded and saved exactly as in practice', async () => {
    const { events } = renderLesson()
    const check = screen.getByRole('region', { name: 'Quick check' })
    await userEvent.click(within(check).getByRole('radio', { name: 'Hi' }))
    await userEvent.click(
      within(check).getByRole('button', { name: 'Fairly sure' }),
    )
    expect(within(check).getByText('Correct!')).toBeInTheDocument()
    expect(events).toEqual([
      expect.objectContaining({
        type: 'answer',
        item_id: MCQ.id,
        item_rev: 1,
        context: 'practice',
        correct: true,
      }),
    ])
  })

  it('is a place in the lesson the outline can point at', () => {
    renderLesson()
    const check = screen.getByRole('region', { name: 'Quick check' })
    // The intro's third part, after the puzzle and a paragraph.
    expect(check).toHaveAttribute('id', 'place-lesson-3')
    expect(check).toHaveAttribute('data-place', 'place-lesson-3')
  })
})

describe('an opening puzzle (<Puzzle>)', () => {
  it('shows the answer only after a guess is typed', async () => {
    renderLesson()
    const puzzle = screen.getByRole('region', { name: 'A puzzle to start' })
    expect(puzzle).toHaveTextContent('Why does print start a new line?')
    expect(puzzle).not.toHaveTextContent('Because its')

    const show = within(puzzle).getByRole('button', { name: 'Show the answer' })
    await userEvent.click(show)
    // No guess yet: the answer stays hidden, and the box asks for one.
    expect(puzzle).not.toHaveTextContent('Because its')
    const box = within(puzzle).getByRole('textbox', { name: 'Your guess' })
    expect(box).toHaveFocus()
    expect(box).toHaveAccessibleDescription(/Type a guess first/)

    await userEvent.type(box, 'print adds it')
    await userEvent.click(show)
    expect(puzzle).toHaveTextContent('Because its end is a newline')
    expect(puzzle).toHaveTextContent('Your guess: print adds it')
    expect(within(puzzle).queryByRole('textbox')).not.toBeInTheDocument()
  })

  it('saves nothing, guess or answer', async () => {
    const { events } = renderLesson()
    const puzzle = screen.getByRole('region', { name: 'A puzzle to start' })
    await userEvent.type(within(puzzle).getByRole('textbox'), 'a guess')
    await userEvent.click(
      within(puzzle).getByRole('button', { name: 'Show the answer' }),
    )
    expect(events).toEqual([])
  })
})

describe('a guess kept from the end of an earlier session', () => {
  const keep = (source: 'puzzle' | 'goal') =>
    localStorage.setItem(
      `guess:${fakeContent().topic.id}`,
      JSON.stringify({
        question: 'Why does `print` start a new line?',
        guess: 'It ends with one',
        at: '2026-11-20T18:00:00.000Z',
        source,
      }),
    )

  it("is waiting in the lesson's puzzle, and is forgotten once the answer shows", async () => {
    keep('puzzle')
    renderLesson()
    const puzzle = screen.getByRole('region', { name: 'A puzzle to start' })
    const box = within(puzzle).getByRole('textbox', { name: 'Your guess' })
    expect(box).toHaveValue('It ends with one')
    expect(box).toHaveAccessibleDescription(/the guess you made last time/)

    await userEvent.click(
      within(puzzle).getByRole('button', { name: 'Show the answer' }),
    )
    expect(puzzle).toHaveTextContent('Your guess: It ends with one')
    expect(puzzle).toHaveTextContent('Because its end is a newline')
    expect(localStorage.getItem(`guess:${fakeContent().topic.id}`)).toBeNull()
  })

  it("leaves the puzzle empty when the guess was about the topic's goal", () => {
    keep('goal')
    renderLesson()
    const puzzle = screen.getByRole('region', { name: 'A puzzle to start' })
    expect(within(puzzle).getByRole('textbox')).toHaveValue('')
  })
})

describe('a real incident (<Story>)', () => {
  it('tells the story and links its source, with its licence', () => {
    renderLesson()
    const story = screen.getByRole('complementary', {
      name: 'The report that printed nothing',
    })
    expect(story).toHaveTextContent('A real incident')
    expect(story).toHaveTextContent('printed an empty page for a week')
    const link = within(story).getByRole('link', {
      name: 'The printer postmortem',
    })
    expect(link).toHaveAttribute('href', 'https://example.com/postmortem')
    expect(link).toHaveAttribute('target', '_blank')
    expect(story).toHaveTextContent(
      'Told in our own words, from The printer postmortem (linked, not copied).',
    )
  })
})
