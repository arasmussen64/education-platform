import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { EventLogContext } from '../events/eventLogContext.ts'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeTopic } from '../test/fakeContent.tsx'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { ExplainCheck } from './ExplainCheck.tsx'
import type { GradeExplanation, GradeOutcome } from './grade.ts'

const TOPIC = fakeTopic()
const EXPLAIN = TOPIC.prove.explain!

const graded = (
  verdict: 'pass' | 'needs_work',
  questions: string[] = [],
): GradeOutcome => ({
  status: 'graded',
  grading: {
    verdict,
    rubric: [{ id: 'types', met: verdict === 'pass' }],
    questions,
  },
  ai_call_id: 'call-1',
  model: 'claude-haiku-5-5',
})

/** Renders the check with a fake grader; `signedIn` is true unless said. */
function renderCheck(
  outcome: GradeOutcome | Promise<GradeOutcome>,
  { signedIn = true, topic = TOPIC } = {},
) {
  const grade = vi.fn<GradeExplanation>(() => Promise.resolve(outcome))
  const { log, events } = recordingEventLog()
  const { unmount } = render(
    <AuthProvider auth={fakeAuth(signedIn ? fakeUser() : null)}>
      <EventLogContext value={log}>
        <MemoryRouter>
          <ExplainCheck topic={topic} explain={EXPLAIN} grade={grade} />
        </MemoryRouter>
      </EventLogContext>
    </AuthProvider>,
  )
  return { grade, events, unmount }
}

const box = () => screen.getByLabelText('Your explanation')
const checkButton = () =>
  screen.getByRole('button', { name: 'Check my explanation' })

async function explain(text: string) {
  await userEvent.type(box(), text)
  await userEvent.click(checkButton())
}

describe('the explain-it-back check', () => {
  it('grades an explanation, and saves it as a passed proof check', async () => {
    const { grade, events } = renderCheck(graded('pass'))
    await explain('  "5" is text and 5 is a number.  ')

    expect(
      await screen.findByText(/Passed. Your explanation shows every idea/),
    ).toBeInTheDocument()
    expect(grade).toHaveBeenCalledWith(
      TOPIC.id,
      EXPLAIN,
      '"5" is text and 5 is a number.',
    )
    expect(events).toEqual([
      expect.objectContaining({
        type: 'explain_submit',
        topic_id: TOPIC.id,
        item_id: 'explain',
        item_rev: 1,
        context: 'prove',
        correct: true,
        data: {
          text: '"5" is text and 5 is a number.',
          status: 'graded',
          verdict: 'pass',
          rubric: [{ id: 'types', met: true }],
          questions: [],
          ai_call_id: 'call-1',
          model: 'claude-haiku-5-5',
        },
      }),
    ])
  })

  it('shows guiding questions when it needs work, never the model answer', async () => {
    const { events } = renderCheck(
      graded('needs_work', ['What does each kind of value let you do?']),
    )
    await explain('They look the same.')

    expect(await screen.findByText(/Needs work/)).toBeInTheDocument()
    expect(
      screen.getByText('What does each kind of value let you do?'),
    ).toBeInTheDocument()
    expect(document.body).not.toHaveTextContent('SECRET MODEL ANSWER')
    expect(events[0]).toMatchObject({ correct: false })
  })

  it.each([
    ['paused', /paused until next month/],
    ['unavailable', /isn't available right now/],
    ['not_allowed', /isn't switched on for your account/],
    ['failed', /couldn't be checked, but it's saved/],
  ] as const)(
    'saves an explanation it could not grade (%s), ungraded, and says why',
    async (status, message) => {
      const { events } = renderCheck({ status })
      await explain('Because of types.')

      expect(await screen.findByText(message)).toBeInTheDocument()
      expect(events[0]).toMatchObject({
        type: 'explain_submit',
        correct: undefined,
        data: { text: 'Because of types.', status },
      })
    },
  )

  it("can't be sent empty, or twice while it's being checked", async () => {
    const { grade } = renderCheck(new Promise<GradeOutcome>(() => {}))
    expect(checkButton()).toBeDisabled()
    await userEvent.type(box(), '   ')
    expect(checkButton()).toBeDisabled()

    await userEvent.type(box(), 'Types differ.')
    await userEvent.click(checkButton())
    expect(screen.getByText('Checking your explanation…')).toBeInTheDocument()
    expect(checkButton()).toBeDisabled()
    expect(grade).toHaveBeenCalledTimes(1)
  })

  describe('drafts', () => {
    beforeEach(() => {
      // Drafts note when they were saved; pinned, so no test reads the clock.
      vi.useFakeTimers({ toFake: ['Date'] })
      vi.setSystemTime(new Date('2026-11-11T12:00:00.000Z'))
    })
    afterEach(() => {
      vi.useRealTimers()
      vi.restoreAllMocks()
    })
    const restoredNote = () =>
      screen.queryByText(/your explanation from last time/)

    it('keeps what was written when the page comes back', async () => {
      const first = renderCheck(graded('pass'))
      await userEvent.type(box(), 'Text and numbers')
      first.unmount()

      renderCheck(graded('pass'))
      expect(box()).toHaveValue('Text and numbers')
      expect(restoredNote()).toBeInTheDocument()
    })

    it('keeps it after "needs work", to improve on', async () => {
      const first = renderCheck(graded('needs_work', ['Why?']))
      await explain('They look the same.')
      await screen.findByText(/Needs work/)
      first.unmount()

      renderCheck(graded('pass'))
      expect(box()).toHaveValue('They look the same.')
    })

    it('starts empty next time, once it passes', async () => {
      const first = renderCheck(graded('pass'))
      await explain('"5" is text and 5 is a number.')
      await screen.findByText(/Passed/)
      first.unmount()

      renderCheck(graded('pass'))
      expect(box()).toHaveValue('')
      expect(restoredNote()).not.toBeInTheDocument()
    })

    it("doesn't bring back an explanation written for an older version of the topic", async () => {
      const first = renderCheck(graded('pass'))
      await userEvent.type(box(), 'Written for version 1')
      first.unmount()

      renderCheck(graded('pass'), { topic: { ...TOPIC, rev: 2 } })
      expect(box()).toHaveValue('')
    })

    it('works without drafts when the browser blocks storage', async () => {
      const blocked = () => {
        throw new DOMException('The operation is insecure.', 'SecurityError')
      }
      vi.spyOn(Storage.prototype, 'getItem').mockImplementation(blocked)
      vi.spyOn(Storage.prototype, 'setItem').mockImplementation(blocked)
      const first = renderCheck(graded('pass'))
      await explain('Types differ.')
      expect(await screen.findByText(/Passed/)).toBeInTheDocument()
      first.unmount()

      renderCheck(graded('pass'))
      expect(box()).toHaveValue('')
    })
  })

  it('asks a signed-out visitor to sign in instead', () => {
    const { grade } = renderCheck(graded('pass'), { signedIn: false })
    expect(screen.queryByLabelText('Your explanation')).not.toBeInTheDocument()
    expect(
      screen.getByText(/to have your explanation checked/),
    ).toBeInTheDocument()
    expect(grade).not.toHaveBeenCalled()
  })
})
