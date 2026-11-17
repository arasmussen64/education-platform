import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TYPED_COMMAND, TYPED_TERM } from '../test/fakeContent.tsx'
import { TypedQuestion } from './TypedQuestion.tsx'

const check = () =>
  userEvent.click(screen.getByRole('button', { name: 'Check' }))

describe('TypedQuestion', () => {
  it('asks for a command in a labelled box, and waits for something typed', () => {
    render(<TypedQuestion item={TYPED_COMMAND} />)
    expect(screen.getByText(/lists only the containers/)).toBeVisible()
    const box = screen.getByRole('textbox', { name: 'Your command' })
    // No phone keyboard capitalising or "correcting" what's recalled.
    expect(box).toHaveAttribute('autocapitalize', 'none')
    expect(box).toHaveAttribute('spellcheck', 'false')
    expect(screen.getByRole('button', { name: 'Check' })).toBeDisabled()
  })

  it('takes Enter as Check, says it was right, and explains', async () => {
    const onAnswer = vi.fn()
    render(<TypedQuestion item={TYPED_COMMAND} onAnswer={onAnswer} />)
    await userEvent.type(
      screen.getByRole('textbox', { name: 'Your command' }),
      '$ docker ps{Enter}',
    )
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(screen.getByText(/Also right:/)).toHaveTextContent(
      'Also right: docker container ls',
    )
    expect(screen.getByText(/lists the running containers/)).toBeVisible()
    expect(screen.getByRole('textbox')).toBeDisabled()
    expect(onAnswer).toHaveBeenCalledWith(true, {
      typed: '$ docker ps',
      mistake: null,
      slip: false,
    })
  })

  it('shows the answer and the known slip after a wrong one', async () => {
    const onAnswer = vi.fn()
    render(<TypedQuestion item={TYPED_COMMAND} onAnswer={onAnswer} />)
    await userEvent.type(screen.getByRole('textbox'), 'docker ps -a')
    await check()
    expect(screen.getByText(/Not quite. The answer is/)).toHaveTextContent(
      'Not quite. The answer is docker ps.',
    )
    expect(screen.getByText('A common slip')).toBeVisible()
    expect(screen.getByText(/stopped ones too/)).toBeVisible()
    expect(screen.getByText(/Also accepted:/)).toHaveTextContent(
      'Also accepted: docker container ls',
    )
    expect(onAnswer).toHaveBeenCalledWith(false, {
      typed: 'docker ps -a',
      mistake: 'every-container',
      slip: false,
    })
  })

  it('forgives a term a slip of the fingers, and shows the spelling', async () => {
    const onAnswer = vi.fn()
    render(<TypedQuestion item={TYPED_TERM} onAnswer={onAnswer} />)
    await userEvent.type(
      screen.getByRole('textbox', { name: 'Your answer' }),
      'kubernets{Enter}',
    )
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(screen.getByText(/Watch the spelling/)).toHaveTextContent(
      "Watch the spelling: it's Kubernetes.",
    )
    expect(onAnswer).toHaveBeenCalledWith(true, {
      typed: 'kubernets',
      mistake: null,
      slip: true,
    })
  })

  it('offers "I don\'t know this" in the placement test, and shows no answer', async () => {
    const onAnswer = vi.fn()
    render(<TypedQuestion item={TYPED_TERM} quiet onAnswer={onAnswer} />)
    await userEvent.click(
      screen.getByRole('button', { name: "I don't know this" }),
    )
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(screen.queryByText(/Kubernetes runs/)).not.toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(false, null)
  })

  it('takes an answer in the placement test without saying if it was right', async () => {
    render(<TypedQuestion item={TYPED_TERM} quiet />)
    await userEvent.type(screen.getByRole('textbox'), 'Docker{Enter}')
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(screen.queryByText(/Not quite/)).not.toBeInTheDocument()
  })
})
