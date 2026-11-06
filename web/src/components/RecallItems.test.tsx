import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { MCQ, PREDICT } from '../test/fakeContent.tsx'
import { McqQuestion } from './McqQuestion.tsx'
import { PredictOutput } from './PredictOutput.tsx'

const check = () =>
  userEvent.click(screen.getByRole('button', { name: 'Check' }))

describe('McqQuestion', () => {
  it('waits for a choice before it can be checked', () => {
    render(<McqQuestion item={MCQ} />)
    expect(screen.getByRole('button', { name: 'Check' })).toBeDisabled()
  })

  it('says when the answer is right, and explains why', async () => {
    const onAnswer = vi.fn()
    render(<McqQuestion item={MCQ} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('radio', { name: 'Hi' }))
    await check()
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(screen.getByText(MCQ.explanation)).toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(true, 0)
  })

  it('shows the right answer after a wrong one, and locks the choice', async () => {
    const onAnswer = vi.fn()
    render(<McqQuestion item={MCQ} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('radio', { name: 'print' }))
    await check()
    expect(screen.getByText(/Not quite. The answer is/)).toBeInTheDocument()
    expect(screen.getByText(MCQ.explanation)).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: 'Hi' })).toBeDisabled()
    expect(onAnswer).toHaveBeenCalledWith(false, 2)
  })
})

describe('PredictOutput', () => {
  it('accepts a prediction that matches, ignoring spaces at line ends', async () => {
    const onAnswer = vi.fn()
    render(<PredictOutput item={PREDICT} onAnswer={onAnswer} />)
    await userEvent.type(
      screen.getByLabelText('What will it print?'),
      'a  {Enter}b',
    )
    await check()
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(true, 'a  \nb')
  })

  it('shows the real output after a wrong prediction', async () => {
    render(<PredictOutput item={PREDICT} />)
    await userEvent.type(screen.getByLabelText('What will it print?'), 'ab')
    await check()
    expect(screen.getByText(/Not quite. It prints:/)).toBeInTheDocument()
    expect(screen.getByLabelText('What will it print?')).toBeDisabled()
    expect(screen.getByText(PREDICT.explanation)).toBeInTheDocument()
  })
})
