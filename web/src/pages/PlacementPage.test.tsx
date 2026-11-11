import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  getDiagnostic,
  getTopic,
  mainTrack,
  topicIdsOf,
} from '../content/content.ts'
import type { Topic } from '../content/types.ts'
import type { EventRow } from '../events/types.ts'
import { fetchAttempts } from '../followups/history.ts'
import { fetchPlacements, type PlacementRecord } from '../placement/history.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeEventsClient } from '../test/fakeEvents.ts'
import { renderApp } from '../test/renderApp.tsx'

// The history and the finished placements normally come from the server.
vi.mock('../followups/history.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../followups/history.ts')>()),
  fetchAttempts: vi.fn(),
}))
vi.mock('../placement/history.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../placement/history.ts')>()),
  fetchPlacements: vi.fn(),
}))
// No checkpoint's steps were ever opened.
vi.mock('../checkpoints/stepsOpened.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../checkpoints/stepsOpened.ts')>()),
  fetchStepsOpened: vi.fn(async () => []),
}))
// How many questions each topic's review pool has: three, unless a test says
// otherwise (some real topics have only two).
const pool = vi.hoisted(() => ({ size: 3 }))
// Every topic's questions are multiple-choice ones whose right answer is
// "right", so a test can pass or fail any probe on purpose.
vi.mock('../content/content.ts', async (importOriginal) => {
  const real = await importOriginal<typeof import('../content/content.ts')>()
  const { fakeContent } = await import('../test/fakeContent.tsx')
  return {
    ...real,
    loadTopicContent: vi.fn(async (id: string) => {
      const topic = real.getTopic(id)
      if (!topic) return null
      const QUESTIONS = ['q-1', 'q-2', 'q-3'].slice(0, pool.size)
      const content = fakeContent({ ...topic, review_pool: QUESTIONS })
      content.recall = Object.fromEntries(
        QUESTIONS.map((itemId) => [
          itemId,
          {
            id: itemId,
            type: 'mcq' as const,
            rev: 1,
            prompt: `Question ${itemId} about ${topic.title}`,
            choices: ['right', 'wrong'],
            answer: 0,
            explanation: 'Because.',
            skills: [],
          },
        ]),
      )
      return content
    }),
  }
})

/** The Python track's open topics, in order: what a placement walks. */
const ORDER: Topic[] = topicIdsOf(mainTrack())
  .map((id) => getTopic(id))
  .filter(
    (topic): topic is Topic =>
      topic !== undefined && topic.kind === 'topic' && topic.status === 'ready',
  )
const MATH = getDiagnostic('math')
if (!MATH) throw new Error('the math diagnostic is bundled')

function renderPlacement(placements: PlacementRecord[] = []) {
  vi.mocked(fetchAttempts).mockResolvedValue([])
  vi.mocked(fetchPlacements).mockResolvedValue(placements)
  const client = fakeEventsClient()
  renderApp('/placement', fakeAuth(fakeUser()), client)
  return { client }
}

/** Everything the page has sent to the (fake) server so far. */
function sentRows(client: ReturnType<typeof fakeEventsClient>): EventRow[] {
  return client.send.mock.calls.flatMap(([rows]) => rows)
}

const region = (name: string | RegExp) => screen.findByRole('region', { name })

/** Answers the question showing, then moves on. */
async function answer(choice: string) {
  await userEvent.click(await screen.findByRole('radio', { name: choice }))
  await userEvent.click(screen.getByRole('button', { name: 'Check' }))
  // Nothing about right or wrong: the test measures (ADR-0021).
  expect(screen.queryByText(/Correct!|Not quite/)).not.toBeInTheDocument()
  expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
  await userEvent.click(screen.getByRole('button', { name: 'Next question' }))
}

/** The topic the question showing is from. */
function topicShowing(): Topic {
  const text = screen.getByText(/^From the topic/).textContent ?? ''
  const title = text.replace('From the topic ', '')
  const topic = ORDER.find((each) => each.title === title)
  if (!topic) throw new Error(`no open topic called ${title}`)
  return topic
}

/** Walks a Python placement, answering right for the first `known` topics. */
async function walkPython(known: number) {
  for (let step = 0; step < 40; step++) {
    if (screen.queryByRole('heading', { name: /where to start/ })) return
    await screen.findByRole('radio', { name: 'right' })
    const index = ORDER.indexOf(topicShowing())
    await answer(index < known ? 'right' : 'wrong')
  }
  throw new Error('the placement never finished')
}

describe('the placement page', () => {
  beforeEach(() => {
    // Shuffles become repeatable: with random() = 0, shuffle() keeps rotating
    // the first item to the end, which is still a fixed order.
    vi.spyOn(Math, 'random').mockReturnValue(0)
  })
  afterEach(() => {
    vi.restoreAllMocks()
    pool.size = 3
  })

  it('asks visitors to sign in', async () => {
    renderApp('/placement')
    // The page loads lazily: give it the time a loaded machine may need.
    expect(
      await screen.findByRole(
        'heading',
        { name: 'Placement test' },
        { timeout: 10_000 },
      ),
    ).toBeInTheDocument()
    expect(screen.getByText(/to take the placement test/)).toBeInTheDocument()
  })

  it('offers each track and the math ladder, with how big each is', async () => {
    renderPlacement()
    const python = await region('Python Foundations')
    expect(python).toHaveTextContent(
      `${ORDER.length} topics written so far, 0 of them learned. About 5 topics' worth of questions.`,
    )
    expect(within(python).getByRole('button', { name: 'Start' })).toBeEnabled()
    const cloud = await region('Cloud Solutions Architect')
    expect(cloud).toHaveTextContent(/topics written so far/)
    const math = await region('Math for machine learning')
    expect(math).toHaveTextContent(
      `${MATH.levels.length} levels, about 3 levels' worth of questions.`,
    )
  })

  it('lists every topic to prove when everything is familiar', async () => {
    const { client } = renderPlacement()
    await userEvent.click(
      within(await region('Python Foundations')).getByRole('button', {
        name: 'Start',
      }),
    )
    await walkPython(ORDER.length)

    const result = await region('Python Foundations: where to start')
    expect(result).toHaveTextContent('You answered 8 of 8 right.')
    expect(result).toHaveTextContent(
      'You seem to know everything written here so far.',
    )
    expect(result).toHaveTextContent(
      `${ORDER.length} topics before it look familiar.`,
    )
    const links = within(result).getAllByRole('link')
    expect(links).toHaveLength(ORDER.length)
    expect(links[0]).toHaveTextContent('Programs and print')
    expect(links[0]).toHaveAttribute('href', '/topic/py.programs-and-print')

    // Every answer was saved as a placement answer of one run, and the run
    // ended in one placement event.
    await waitFor(() => {
      expect(
        sentRows(client).filter((row) => row.type === 'placement'),
      ).toHaveLength(1)
    })
    const rows = sentRows(client)
    const answers = rows.filter((row) => row.type === 'answer')
    expect(answers).toHaveLength(8)
    expect(new Set(answers.map((row) => row.context))).toEqual(
      new Set(['placement']),
    )
    const runs = new Set(
      answers.map((row) => (row.data as { run: string }).run),
    )
    expect(runs.size).toBe(1)
    const summary = rows.find((row) => row.type === 'placement')
    expect(summary?.topic_id).toBe('python-foundations')
    expect(summary?.context).toBe('placement')
    expect(summary?.data).toMatchObject({
      run: [...runs][0],
      kind: 'track',
      next: null,
      asked: 8,
      correct: 8,
    })
    const found = summary?.data as { known: string[] } | undefined
    expect(found?.known).toHaveLength(ORDER.length)
  })

  it('starts at the beginning when nothing is familiar', async () => {
    renderPlacement()
    await userEvent.click(
      within(await region('Python Foundations')).getByRole('button', {
        name: 'Start',
      }),
    )
    await walkPython(0)
    const result = await region('Python Foundations: where to start')
    expect(result).toHaveTextContent('You answered 0 of 10 right.')
    expect(result).toHaveTextContent(
      'Start at the beginning: Programs and print.',
    )
    expect(within(result).getAllByRole('link')).toHaveLength(1)
  })

  it('finds where the knowledge runs out in the middle', async () => {
    renderPlacement()
    await userEvent.click(
      within(await region('Python Foundations')).getByRole('button', {
        name: 'Start',
      }),
    )
    await walkPython(10)
    const result = await region('Python Foundations: where to start')
    const next = ORDER[10]
    expect(result).toHaveTextContent(
      `Your knowledge seems to run out at ${next?.title}. That's where to start learning.`,
    )
    expect(result).toHaveTextContent('10 topics before it look familiar.')
    const list = within(result).getByRole('list')
    expect(within(list).getAllByRole('listitem')).toHaveLength(10)
    expect(within(list).getAllByRole('link').at(-1)).toHaveTextContent(
      ORDER[9]?.title ?? '',
    )
  })

  // Eleven ready topics have only two recall questions to ask. ADR-0021
  // gives a tie the benefit of the doubt.
  describe('with two questions a topic', () => {
    beforeEach(() => {
      pool.size = 2
    })

    /** Walks a Python placement, answering each probe's questions in turn. */
    async function walkAnswering(answers: string[]) {
      const asked = new Map<Topic, number>()
      for (let step = 0; step < 40; step++) {
        if (screen.queryByRole('heading', { name: /where to start/ })) return
        await screen.findByRole('radio', { name: 'right' })
        const topic = topicShowing()
        const count = asked.get(topic) ?? 0
        asked.set(topic, count + 1)
        await answer(answers[count] ?? 'wrong')
      }
      throw new Error('the placement never finished')
    }

    async function start() {
      await userEvent.click(
        within(await region('Python Foundations')).getByRole('button', {
          name: 'Start',
        }),
      )
    }

    it('passes a topic on one right and one wrong', async () => {
      renderPlacement()
      await start()
      // Wrong first, so the probe has to ask both.
      await walkAnswering(['wrong', 'right'])
      const result = await region('Python Foundations: where to start')
      expect(result).toHaveTextContent('You answered 4 of 8 right.')
      expect(result).toHaveTextContent(
        'You seem to know everything written here so far.',
      )
    })

    it('fails a topic on two wrong', async () => {
      renderPlacement()
      await start()
      await walkAnswering(['wrong', 'wrong'])
      const result = await region('Python Foundations: where to start')
      expect(result).toHaveTextContent('You answered 0 of 10 right.')
      expect(result).toHaveTextContent(
        'Start at the beginning: Programs and print.',
      )
    })
  })

  it('walks the math ladder and says where to refresh', async () => {
    const { client } = renderPlacement()
    await userEvent.click(
      within(await region('Math for machine learning')).getByRole('button', {
        name: 'Start',
      }),
    )
    // Solid on the first three levels, shaky from the fourth.
    const KNOWN = 3
    for (let step = 0; step < 40; step++) {
      if (screen.queryByRole('heading', { name: /what it found/ })) break
      await screen.findByRole('heading', { name: 'Quick check' })
      const header = screen.getByText(/^Question \d+ · /).textContent ?? ''
      const index = MATH.levels.findIndex((level) =>
        header.endsWith(level.title),
      )
      const level = MATH.levels[index]
      if (!level) throw new Error(`unknown level in ${header}`)
      const item = level.items.find((each) => screen.queryByText(each.prompt))
      if (!item) throw new Error(`no question of ${level.id} is showing`)
      const right = item.choices[item.answer] ?? ''
      const wrong = item.choices[(item.answer + 1) % item.choices.length] ?? ''
      await answer(index < KNOWN ? right : wrong)
    }

    const result = await region('Math for machine learning: what it found')
    expect(result).toHaveTextContent('Solid through Functions and graphs.')
    expect(result).toHaveTextContent('From Exponents and logarithms on')
    const links = within(result).getAllByRole('link')
    expect(links).toHaveLength(MATH.levels.length - KNOWN)
    // The fourth level's topic is written, so the result links it rather
    // than the outside refresher.
    expect(links[0]).toHaveAttribute(
      'href',
      `/topic/${MATH.levels[KNOWN]?.topic ?? ''}`,
    )

    await waitFor(() => {
      expect(
        sentRows(client).filter((row) => row.type === 'placement'),
      ).toHaveLength(1)
    })
    const rows = sentRows(client)
    const answers = rows.filter((row) => row.type === 'answer')
    expect(answers.length).toBeGreaterThanOrEqual(6)
    expect(answers.every((row) => row.topic_id === 'diagnostic.math')).toBe(
      true,
    )
    expect(answers.every((row) => row.context === 'placement')).toBe(true)
    const summary = rows.find((row) => row.type === 'placement')
    expect(summary?.topic_id).toBe('diagnostic.math')
    expect(summary?.data).toMatchObject({
      kind: 'diagnostic',
      diagnostic: 'math',
      known: ['arithmetic', 'algebra', 'functions'],
      next: 'exponents-and-logs',
    })
  })

  it('offers "I don\'t know this" on every question and counts it as wrong', async () => {
    const { client } = renderPlacement()
    await userEvent.click(
      within(await region('Python Foundations')).getByRole('button', {
        name: 'Start',
      }),
    )
    for (let step = 0; step < 40; step++) {
      if (screen.queryByRole('heading', { name: /where to start/ })) break
      await screen.findByRole('radio', { name: 'right' })
      await answer("I don't know this")
    }
    const result = await region('Python Foundations: where to start')
    expect(result).toHaveTextContent('You answered 0 of 10 right.')
    expect(result).toHaveTextContent(
      'Start at the beginning: Programs and print.',
    )

    await waitFor(() => {
      expect(
        sentRows(client).filter((row) => row.type === 'placement'),
      ).toHaveLength(1)
    })
    const answers = sentRows(client).filter((row) => row.type === 'answer')
    expect(answers).toHaveLength(10)
    expect(answers.every((row) => row.correct === false)).toBe(true)
    // Saved as "didn't know", not as a wrong choice.
    for (const row of answers) {
      expect(row.data).toMatchObject({
        choice: null,
        choice_text: null,
        dont_know: true,
      })
    }
  })

  it('offers "I don\'t know this" on the math ladder too', async () => {
    const { client } = renderPlacement()
    await userEvent.click(
      within(await region('Math for machine learning')).getByRole('button', {
        name: 'Start',
      }),
    )
    await screen.findByRole('heading', { name: 'Quick check' })
    await answer("I don't know this")
    await waitFor(() => {
      expect(
        sentRows(client).filter((row) => row.type === 'answer'),
      ).toHaveLength(1)
    })
    const row = sentRows(client).find((each) => each.type === 'answer')
    expect(row?.correct).toBe(false)
    expect(row?.data).toMatchObject({ choice: null, dont_know: true })
    expect(row?.data).toHaveProperty('level')
  })

  it('shows the last result on a card, and offers to take it again', async () => {
    renderPlacement([
      {
        id: 'p1',
        run: 'r1',
        subject: 'python-foundations',
        kind: 'track',
        at: '2026-11-09T12:00:00.000Z',
        known: ['py.programs-and-print', 'py.values-and-types'],
        next: 'py.variables',
        asked: 6,
        correct: 4,
      },
    ])
    const python = await region('Python Foundations')
    expect(python).toHaveTextContent(
      /Placement on 2026-11-\d\d: start at Variables, with 2 topics to prove first\./,
    )
    expect(
      within(python).getByRole('button', { name: 'Take it again' }),
    ).toBeInTheDocument()
  })

  it('can be stopped, saving no result', async () => {
    const { client } = renderPlacement()
    await userEvent.click(
      within(await region('Python Foundations')).getByRole('button', {
        name: 'Start',
      }),
    )
    await screen.findByRole('radio', { name: 'right' })
    await userEvent.click(screen.getByRole('button', { name: 'Stop here' }))
    expect(await region('Python Foundations')).toHaveTextContent(
      'topics written so far',
    )
    expect(sentRows(client).some((row) => row.type === 'placement')).toBe(false)
  })
})
