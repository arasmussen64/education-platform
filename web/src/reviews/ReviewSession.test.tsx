import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { StrictMode } from 'react'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { EventLogContext } from '../events/eventLogContext.ts'
import type { NewEvent } from '../events/types.ts'
import type { Attempt } from '../followups/followUps.ts'
import { progressOf } from '../progress/progress.ts'
import { fakeAuth } from '../test/fakeAuth.ts'
import { fakeContent, fakeTopic } from '../test/fakeContent.tsx'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { ReviewSession } from './ReviewSession.tsx'

// Predictions can be stepped through, which needs the Python runner: use
// the fake one.
vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)

// A topic with a two-item review pool: a quick check and a prediction.
const content = fakeContent(
  fakeTopic({ prerequisites: [], review_pool: ['mcq-print', 'predict-print'] }),
)
const LEARNED = '2026-11-01T12:00:00.000Z'
/** A week after Learned: the first review (due after 4 days) is due. */
const VISIT = '2026-11-08T12:00:00.000Z'

/** The three proofs, passed on 1 November. */
const learnedEvents: Attempt[] = [
  ['code_check', 'build-hello'] as const,
  ['code_check', 'debug-hello'] as const,
  ['explain_submit', 'explain'] as const,
].map(([type, item]) => ({
  id: `proof-${item}`,
  type,
  topic_id: content.topic.id,
  item_id: item,
  correct: true,
  occurred_at: LEARNED,
  context: 'prove',
}))

/** What the server would send back for an event the session recorded. */
function asAttempt(event: NewEvent, when: string, index: number): Attempt {
  return {
    id: `recorded-${index}`,
    type: event.type as Attempt['type'],
    topic_id: event.topic_id ?? '',
    item_id: event.item_id ?? '',
    correct: event.correct ?? false,
    occurred_at: when,
    context: event.context,
  }
}

/** One page load: the Today page's session for the topic. */
function openReview(history: Attempt[], { strict = false } = {}) {
  const { log, events } = recordingEventLog()
  const progress = progressOf([content.topic], history).get(content.topic.id)!
  const session = (
    <AuthProvider auth={fakeAuth(null)}>
      <EventLogContext value={log}>
        <MemoryRouter>
          <ReviewSession
            content={content}
            progress={progress}
            attempts={history}
            now={new Date().toISOString()}
          />
        </MemoryRouter>
      </EventLogContext>
    </AuthProvider>
  )
  const view = render(strict ? <StrictMode>{session}</StrictMode> : session)
  return { ...view, events }
}

async function answerQuickCheck(choice: string) {
  const quick = screen.getByRole('region', { name: 'Quick check' })
  await userEvent.click(within(quick).getByRole('radio', { name: choice }))
  await userEvent.click(within(quick).getByRole('button', { name: 'Check' }))
}

async function answerPrediction(text: string) {
  const predict = screen.getByRole('region', { name: 'Predict the output' })
  await userEvent.type(
    within(predict).getByLabelText('What will it print?'),
    text,
  )
  await userEvent.click(within(predict).getByRole('button', { name: 'Check' }))
}

const reviewsIn = (events: NewEvent[]) =>
  events.filter((event) => event.type === 'review')

describe('a review session', () => {
  beforeEach(() => {
    // Only the clock: the page's own timers run as usual.
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date(VISIT))
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('is rated from both first answers, and saved once', async () => {
    const { events } = openReview(learnedEvents)
    await answerPrediction('a{Enter}b')
    expect(reviewsIn(events)).toHaveLength(0)
    await answerQuickCheck('Hi')
    expect(reviewsIn(events)).toEqual([
      expect.objectContaining({
        topic_id: content.topic.id,
        correct: true,
        data: {
          rating: 'good',
          items: [
            { id: 'predict-print', correct: true },
            { id: 'mcq-print', correct: true },
          ],
        },
      }),
    ])
    expect(screen.getByText(/^Good: all right\./)).toBeInTheDocument()
  })

  it('left half-way still counts: the next page load keeps the wrong answer and asks the rest', async () => {
    // First visit: the quick check, wrong; then the learner leaves.
    const first = openReview(learnedEvents)
    await answerQuickCheck('"Hi"')
    expect(reviewsIn(first.events)).toHaveLength(0)
    const answered = first.events.map((event, index) =>
      asAttempt(event, VISIT, index),
    )
    first.unmount()

    // An hour later, a new page load.
    vi.setSystemTime(new Date(Date.parse(VISIT) + 60 * 60 * 1000))
    const second = openReview([...learnedEvents, ...answered])
    expect(
      screen.queryByRole('region', { name: 'Quick check' }),
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(
        /answered this one on an earlier visit, and didn't get it right/,
      ),
    ).toBeInTheDocument()
    await answerPrediction('a{Enter}b')
    expect(reviewsIn(second.events)).toEqual([
      expect.objectContaining({
        correct: false,
        data: {
          rating: 'hard',
          items: [
            { id: 'mcq-print', correct: false },
            { id: 'predict-print', correct: true },
          ],
        },
      }),
    ])
    expect(
      screen.getByText(/^Hard: some right, some not\./),
    ).toBeInTheDocument()
  })

  it('answered in full on earlier visits is saved as soon as it shows, once', async () => {
    const earlier: Attempt[] = [
      ['mcq-print', true] as const,
      ['predict-print', false] as const,
    ].map(([item, correct], index) => ({
      id: `earlier-${index}`,
      type: 'answer',
      topic_id: content.topic.id,
      item_id: item,
      correct,
      occurred_at: VISIT,
      context: 'review',
    }))
    vi.setSystemTime(new Date(Date.parse(VISIT) + 60 * 60 * 1000))
    // Strict mode runs effects twice in development: still one review.
    const { events } = openReview([...learnedEvents, ...earlier], {
      strict: true,
    })
    expect(await screen.findByText(/^Hard: some right/)).toBeInTheDocument()
    expect(reviewsIn(events)).toEqual([
      expect.objectContaining({
        data: expect.objectContaining({ rating: 'hard' }),
      }),
    ])
  })

  it('starts fresh from old answers saved without a context', async () => {
    const old: Attempt = {
      id: 'old',
      type: 'answer',
      topic_id: content.topic.id,
      item_id: 'mcq-print',
      correct: false,
      occurred_at: VISIT,
    }
    vi.setSystemTime(new Date(Date.parse(VISIT) + 60 * 60 * 1000))
    const { events } = openReview([...learnedEvents, old])
    expect(screen.getAllByText(/^Review \d of 2$/)).toHaveLength(2)
    expect(
      screen.queryByText(/answered this one on an earlier visit/),
    ).not.toBeInTheDocument()
    expect(reviewsIn(events)).toHaveLength(0)
  })
})
