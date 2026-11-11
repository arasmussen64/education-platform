import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeExercise } from '../test/fakeContent.tsx'
import { oneFailed } from '../test/fakePython.ts'
import type { AskTutor, HintOutcome } from './hint.ts'
import { MAX_ASKS, TutorBox } from './TutorBox.tsx'

const EXERCISE = fakeExercise({ id: 'write-hello', stage: 'write' })

const hinted = (
  text: string,
  level: 'nudge' | 'concept' | 'specific' | 'step' = 'nudge',
): HintOutcome => ({
  status: 'hinted',
  hint: { text, level, replaced: false },
  ai_call_id: 'call-1',
  model: 'claude-haiku-5-5',
})

function renderBox(ask: AskTutor, { signedIn = true, onHint = vi.fn() } = {}) {
  render(
    <AuthProvider auth={fakeAuth(signedIn ? fakeUser() : null)}>
      <MemoryRouter>
        <TutorBox
          topicId="py.values-and-types"
          itemId="write-hello"
          exercise={EXERCISE}
          code="print(Hello)"
          check={oneFailed('Prints Hello!')}
          onHint={onHint}
          ask={ask}
        />
      </MemoryRouter>
    </AuthProvider>,
  )
  return { onHint }
}

const askButton = () => screen.getByRole('button', { name: /Ask/ })

describe('TutorBox', () => {
  it('asks with the code, the Check and the question, and shows the hint with its rung', async () => {
    const ask = vi.fn<AskTutor>(() =>
      Promise.resolve(hinted('What is Hello without quotes?')),
    )
    const { onHint } = renderBox(ask)
    await userEvent.type(
      screen.getByLabelText('What are you stuck on? (optional)'),
      'why the error',
    )
    await userEvent.click(askButton())

    expect(ask).toHaveBeenCalledWith({
      topicId: 'py.values-and-types',
      itemId: 'write-hello',
      exercise: EXERCISE,
      code: 'print(Hello)',
      check: oneFailed('Prints Hello!'),
      question: 'why the error',
      earlier: [],
    })
    const hints = screen.getByRole('list', { name: 'Hints from the tutor' })
    expect(within(hints).getByText('You: why the error')).toBeInTheDocument()
    expect(within(hints).getByText('A nudge')).toBeInTheDocument()
    expect(
      within(hints).getByText('What is Hello without quotes?'),
    ).toBeInTheDocument()
    expect(onHint).toHaveBeenCalledWith({
      hint: {
        text: 'What is Hello without quotes?',
        level: 'nudge',
        replaced: false,
      },
      count: 1,
      question: 'why the error',
      aiCallId: 'call-1',
      model: 'claude-haiku-5-5',
    })
    // The question box is cleared for the next ask.
    expect(
      screen.getByLabelText('What are you stuck on? (optional)'),
    ).toHaveValue('')
    expect(
      screen.getByRole('button', { name: 'Ask again' }),
    ).toBeInTheDocument()
  })

  it('sends the earlier hints back, so the tutor climbs the ladder', async () => {
    const ask = vi
      .fn<AskTutor>()
      .mockResolvedValueOnce(hinted('First', 'nudge'))
      .mockResolvedValueOnce(hinted('Second', 'concept'))
    renderBox(ask)
    await userEvent.click(askButton())
    await userEvent.click(askButton())
    expect(ask.mock.calls[1]?.[0].earlier).toEqual(['First'])
    expect(screen.getByText('The idea')).toBeInTheDocument()
  })

  it('stops after six hints', async () => {
    const ask = vi.fn<AskTutor>(() => Promise.resolve(hinted('A hint')))
    renderBox(ask)
    for (let i = 0; i < MAX_ASKS; i++) {
      await userEvent.click(askButton())
    }
    expect(
      screen.queryByRole('button', { name: /Ask/ }),
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(/That's all the tutor can give here/),
    ).toBeInTheDocument()
    expect(screen.getAllByText('A hint')).toHaveLength(MAX_ASKS)
  })

  it('explains when there is no hint this time, and keeps the button', async () => {
    const outcomes: [HintOutcome['status'], RegExp][] = [
      ['paused', /paused until next month/],
      ['not_allowed', /isn't switched on for your account/],
      ['unavailable', /isn't available right now/],
      ['too_long', /too long for the tutor to read/],
      ['failed', /couldn't be reached/],
    ]
    for (const [status, message] of outcomes) {
      const ask = vi.fn<AskTutor>(() =>
        Promise.resolve({ status } as HintOutcome),
      )
      const { unmount } = render(
        <AuthProvider auth={fakeAuth(fakeUser())}>
          <MemoryRouter>
            <TutorBox
              topicId="t"
              itemId="i"
              exercise={EXERCISE}
              code=""
              check={null}
              ask={ask}
            />
          </MemoryRouter>
        </AuthProvider>,
      )
      await userEvent.click(askButton())
      expect(screen.getByText(message)).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Ask the tutor' }),
      ).toBeEnabled()
      unmount()
    }
  })

  it('is not there for signed-out visitors, who are asked to sign in once, at the top', () => {
    renderBox(vi.fn<AskTutor>(), { signedIn: false })
    expect(
      screen.queryByRole('region', { name: 'Tutor' }),
    ).not.toBeInTheDocument()
  })
})
