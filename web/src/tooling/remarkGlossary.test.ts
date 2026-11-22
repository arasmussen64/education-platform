import { evaluate } from '@mdx-js/mdx'
import { createElement, type ReactNode } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import * as runtime from 'react/jsx-runtime'
import { describe, expect, it } from 'vitest'
import {
  type GlossaryTerm,
  remarkGlossary,
  topicOfLesson,
} from './remarkGlossary.ts'

const TERMS: GlossaryTerm[] = [
  {
    term: 'NAT',
    aliases: ['network address translation'],
    definition: 'Rewriting addresses as packets pass a gateway.',
    topicId: 'csa.net.nat',
    topicTitle: 'NAT',
  },
  {
    term: 'source NAT',
    aliases: ['SNAT'],
    definition: "NAT that rewrites a packet's source.",
    topicId: 'csa.net.nat',
    topicTitle: 'NAT',
  },
  {
    term: 'page cache',
    aliases: [],
    definition: 'Copies of recently read files, kept in memory.',
    topicId: 'csa.linux.memory',
    topicTitle: 'Memory',
  },
]

/** Stand-ins for the lesson's components that show what they were given. */
const components = {
  Term: ({ term, children }: { term: string; children?: ReactNode }) =>
    createElement('mark', { 'data-term': term }, children),
  Intro: ({ children }: { children?: ReactNode }) =>
    createElement('div', null, children),
  Recap: ({ children }: { children?: ReactNode }) =>
    createElement('div', null, children),
  Story: ({ children }: { children?: ReactNode }) =>
    createElement('aside', null, children),
  Puzzle: ({ children }: { children?: ReactNode }) =>
    createElement('section', null, children),
}

/** Compiles a lesson of the given topic as the build does, and renders it. */
async function render(source: string, topicId = 'csa.net.transport') {
  const { default: Lesson } = await evaluate(
    { value: source, path: `/repo/content/topics/${topicId}/lesson.mdx` },
    {
      ...runtime,
      remarkPlugins: [[remarkGlossary, { load: async () => TERMS }]],
    },
  )
  return renderToStaticMarkup(createElement(Lesson, { components }))
}

/** The words that were marked, with their terms. */
function marked(html: string): string[] {
  return [...html.matchAll(/<mark data-term="([^"]+)">([^<]+)<\/mark>/g)].map(
    ([, term, text]) => `${term}: ${text}`,
  )
}

describe('glossary terms in a lesson (ADR-0026)', () => {
  it('marks the first use of each term, and only the first', async () => {
    const html = await render(
      'A NAT gateway. Another NAT. The page cache helps; the page cache fills.',
    )
    expect(marked(html)).toEqual(['NAT: NAT', 'page cache: page cache'])
  })

  it('carries the definition and the teaching topic', async () => {
    const { default: Lesson } = await evaluate(
      {
        value: 'Use NAT here.',
        path: '/repo/content/topics/csa.net.transport/lesson.mdx',
      },
      {
        ...runtime,
        remarkPlugins: [[remarkGlossary, { load: async () => TERMS }]],
      },
    )
    const props: Record<string, unknown>[] = []
    renderToStaticMarkup(
      createElement(Lesson, {
        components: {
          Term: (given: Record<string, unknown>) => {
            props.push(given)
            return null
          },
        },
      }),
    )
    expect(props).toEqual([
      {
        term: 'NAT',
        definition: 'Rewriting addresses as packets pass a gateway.',
        topicId: 'csa.net.nat',
        topicTitle: 'NAT',
        children: 'NAT',
      },
    ])
  })

  it('takes the longest term, an alias, a plural and a capital first letter', async () => {
    expect(marked(await render('Two SNATs, then source NAT.'))).toEqual([
      'source NAT: SNATs',
    ])
    expect(marked(await render('Page cache first.'))).toEqual([
      'page cache: Page cache',
    ])
    expect(
      marked(await render('With network address translation, NAT.')),
    ).toEqual(['NAT: network address translation'])
  })

  it('matches whole words, and the rest of a term exactly', async () => {
    expect(
      marked(await render('NATIVE code, a nat, and a pre-NAT step.')),
    ).toEqual([])
  })

  it('leaves headings, links, code and puzzles alone', async () => {
    const html = await render(
      [
        '# NAT in a heading',
        '',
        '[NAT in a link](https://example.com)',
        '',
        'Code: `NAT` and',
        '',
        '```text',
        'NAT in a block',
        '```',
        '',
        '<Puzzle question="Why?">',
        '',
        'NAT in a puzzle.',
        '',
        '</Puzzle>',
        '',
        'Finally, NAT in prose.',
      ].join('\n'),
    )
    expect(marked(html)).toEqual(['NAT: NAT'])
    expect(html).toContain('Finally, <mark data-term="NAT">NAT</mark>')
  })

  it('reads the intro, the recap, a story and bold text', async () => {
    const html = await render(
      [
        '<Intro>',
        '',
        'The **page cache** matters.',
        '',
        '</Intro>',
        '',
        '<Story title="t" source="https://example.com" sourceTitle="s" license="l">',
        '',
        'A NAT ran out of ports.',
        '',
        '</Story>',
      ].join('\n'),
    )
    expect(marked(html)).toEqual(['page cache: page cache', 'NAT: NAT'])
  })

  it("doesn't mark a topic's own terms on its own page", async () => {
    // On NAT's page, "source NAT" is its own term: not marked, and its
    // "NAT" isn't marked either. Another topic's term still is.
    const html = await render(
      'First source NAT, then NAT, then the page cache.',
      'csa.net.nat',
    )
    expect(marked(html)).toEqual(['page cache: page cache'])
  })

  it("doesn't mark another track's terms: the same word means other things there", async () => {
    // "page cache" is a cloud-track term; in an ML lesson it stays plain.
    const html = await render(
      'The page cache holds files, and NAT rewrites addresses.',
      'ml.dsa.graphs',
    )
    expect(marked(html)).toEqual([])
  })

  it('finds the topic from the lesson file, on Windows too', () => {
    expect(topicOfLesson('/a/content/topics/csa.net.nat/lesson.mdx')).toBe(
      'csa.net.nat',
    )
    expect(topicOfLesson('C:\\a\\content\\topics\\py.x\\lesson.mdx')).toBe(
      'py.x',
    )
    expect(topicOfLesson('/a/elsewhere.mdx')).toBeNull()
  })
})
