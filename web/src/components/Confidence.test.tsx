import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { MCQ, PARSONS, PREDICT } from '../test/fakeContent.tsx'
import { McqQuestion } from './McqQuestion.tsx'
import { ParsonsProblem } from './ParsonsProblem.tsx'
import { PredictOutput } from './PredictOutput.tsx'

vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)

const CERTAIN_NOTE = /You were certain, and it's wrong/
const GUESS_NOTE = /Right, though you were guessing/

describe('saying how sure you are before checking (ADR-0028)', () => {
  it('replaces Check with three buttons, in a group named by its question', () => {
    render(<McqQuestion item={MCQ} />)
    expect(
      screen.queryByRole('button', { name: 'Check' }),
    ).not.toBeInTheDocument()
    const group = screen.getByRole('group', {
      name: 'How sure are you? Pick one to check.',
    })
    expect(group).toHaveTextContent('GuessingFairly sureCertain')
  })

  it('reaches each button with Tab and presses it with Enter', async () => {
    const onAnswer = vi.fn()
    render(<McqQuestion item={MCQ} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('radio', { name: 'Hi' }))
    await userEvent.tab()
    expect(screen.getByRole('button', { name: 'Guessing' })).toHaveFocus()
    await userEvent.tab()
    await userEvent.tab()
    expect(screen.getByRole('button', { name: 'Certain' })).toHaveFocus()
    await userEvent.keyboard('{Enter}')
    expect(onAnswer).toHaveBeenCalledWith(true, 0, 'sure')
  })

  it('points out a mistake made with certainty, the kind that sticks once corrected', async () => {
    render(<McqQuestion item={MCQ} />)
    await userEvent.click(screen.getByRole('radio', { name: 'print' }))
    await userEvent.click(screen.getByRole('button', { name: 'Certain' }))
    expect(screen.getByText(CERTAIN_NOTE)).toBeVisible()
    expect(screen.getByText(MCQ.explanation)).toBeVisible()
  })

  it('says a right guess is still worth reading', async () => {
    render(<PredictOutput item={PREDICT} />)
    await userEvent.type(screen.getByLabelText('What will it print?'), 'a\nb')
    await userEvent.click(screen.getByRole('button', { name: 'Guessing' }))
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(screen.getByText(GUESS_NOTE)).toBeVisible()
  })

  it('adds nothing when the confidence fitted the answer', async () => {
    render(<ParsonsProblem item={PARSONS} />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Add: count = 3' }),
    )
    // Wrong, but only fairly sure: no note.
    await userEvent.click(screen.getByRole('button', { name: 'Fairly sure' }))
    expect(screen.getByText(/Not quite/)).toBeInTheDocument()
    expect(screen.queryByText(CERTAIN_NOTE)).not.toBeInTheDocument()
    expect(screen.queryByText(GUESS_NOTE)).not.toBeInTheDocument()
  })

  it('keeps the single Check in the placement test, which asks nothing more', () => {
    render(<McqQuestion item={MCQ} quiet />)
    expect(screen.getByRole('button', { name: 'Check' })).toBeInTheDocument()
    expect(screen.queryByRole('group')).not.toBeInTheDocument()
  })
})
