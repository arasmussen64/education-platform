import { render, screen, within } from '@testing-library/react'
import type { MDXComponents } from 'mdx/types'
import { createElement, type ReactNode } from 'react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'
import { loadTopicContent } from '../content/content.ts'
import { listedTerms } from '../content/glossary.ts'
import { GlossaryPage } from './GlossaryPage.tsx'

describe('the glossary page (ADR-0026)', () => {
  it('lists every term, sorted, with the topic that teaches it', () => {
    render(
      <MemoryRouter>
        <GlossaryPage />
      </MemoryRouter>,
    )
    expect(
      screen.getByRole('heading', { level: 1, name: 'Glossary' }),
    ).toBeInTheDocument()
    const nat = screen.getByText('NAT', { selector: 'dt' })
    const entry = nat.parentElement as HTMLElement
    expect(entry).toHaveTextContent('also network address translation')
    expect(within(entry).getByRole('link', { name: 'NAT' })).toHaveAttribute(
      'href',
      '/topic/csa.net.nat',
    )
  })

  it('leaves out terms of topics a learner cannot open, and sorts by term', () => {
    const terms = listedTerms({
      '../../../content/topics/csa.net.nat/glossary.yaml': [
        { term: 'source NAT', definition: 'b' },
        { term: 'masquerade', definition: 'a' },
      ],
      // A topic that's only an outline: its page can't be opened.
      '../../../content/topics/csa.capstone-1/glossary.yaml': [
        { term: 'capstone', definition: 'c' },
      ],
    })
    expect(terms.map((entry) => entry.term)).toEqual([
      'masquerade',
      'source NAT',
    ])
    expect(terms[0]).toMatchObject({
      topicId: 'csa.net.nat',
      topicTitle: 'NAT',
    })
  })
})

describe('a real lesson, as the build compiles it', () => {
  it("marks the first use of another topic's term", async () => {
    // The transport lesson uses NAT, which csa.net.nat's glossary defines.
    const content = await loadTopicContent('csa.net.transport')
    const Lesson = content?.Lesson
    expect(Lesson).toBeTypeOf('function')
    if (!Lesson) return
    const marks: string[] = []
    const pass = ({ children }: { children?: ReactNode }) =>
      createElement('div', null, children)
    const components: MDXComponents = {
      Intro: pass,
      Recap: pass,
      Resource: () => null,
      Check: () => null,
      Puzzle: () => null,
      Story: pass,
      Term: ({ term }: { term: string }) => {
        marks.push(term)
        return null
      },
    }
    render(<Lesson components={components} />)
    expect(marks.filter((term) => term === 'NAT')).toHaveLength(1)
  })
})
