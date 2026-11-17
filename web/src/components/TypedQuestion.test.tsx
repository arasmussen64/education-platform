import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TYPED_COMMAND, TYPED_TERM } from '../test/fakeContent.tsx'
import { TypedQuestion } from './TypedQuestion.tsx'

/** Checks the answer, saying how sure (ADR-0028). */
const checkAs = (name: 'Guessing' | 'Fairly sure' | 'Certain') =>
  userEvent.click(screen.getByRole('button', { name }))

describe('TypedQuestion', () => {
  it('asks for a command in a labelled box, and waits for something typed', () => {
    render(<TypedQuestion item={TYPED_COMMAND} />)
    expect(screen.getByText(/lists only the containers/)).toBeVisible()
    const box = screen.getByRole('textbox', { name: 'Your command' })
    // No phone keyboard capitalising or "correcting" what's recalled.
    expect(box).toHaveAttribute('autocapitalize', 'none')
    expect(box).toHaveAttribute('spellcheck', 'false')
    expect(screen.getByRole('button', { name: 'Fairly sure' })).toBeDisabled()
  })

  it('moves to the confidence buttons on Enter, then says it was right', async () => {
    const onAnswer = vi.fn()
    render(<TypedQuestion item={TYPED_COMMAND} onAnswer={onAnswer} />)
    await userEvent.type(
      screen.getByRole('textbox', { name: 'Your command' }),
      '$ docker ps{Enter}',
    )
    expect(screen.getByRole('button', { name: 'Guessing' })).toHaveFocus()
    expect(onAnswer).not.toHaveBeenCalled()
    await userEvent.keyboard('{Tab}{Enter}')
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(screen.getByText(/Also right:/)).toHaveTextContent(
      'Also right: docker container ls',
    )
    expect(screen.getByText(/lists the running containers/)).toBeVisible()
    expect(screen.getByRole('textbox')).toBeDisabled()
    expect(onAnswer).toHaveBeenCalledWith(
      true,
      { typed: '$ docker ps', mistake: null, slip: false },
      'fair',
    )
  })

  it('shows the answer and the known slip after a wrong one', async () => {
    const onAnswer = vi.fn()
    render(<TypedQuestion item={TYPED_COMMAND} onAnswer={onAnswer} />)
    await userEvent.type(screen.getByRole('textbox'), 'docker ps -a')
    await checkAs('Fairly sure')
    expect(screen.getByText(/Not quite. The answer is/)).toHaveTextContent(
      'Not quite. The answer is docker ps.',
    )
    expect(screen.getByText('A common slip')).toBeVisible()
    expect(screen.getByText(/stopped ones too/)).toBeVisible()
    expect(screen.getByText(/Also accepted:/)).toHaveTextContent(
      'Also accepted: docker container ls',
    )
    expect(onAnswer).toHaveBeenCalledWith(
      false,
      { typed: 'docker ps -a', mistake: 'every-container', slip: false },
      'fair',
    )
  })

  it('forgives a term a slip of the fingers, and shows the spelling', async () => {
    const onAnswer = vi.fn()
    render(<TypedQuestion item={TYPED_TERM} onAnswer={onAnswer} />)
    await userEvent.type(
      screen.getByRole('textbox', { name: 'Your answer' }),
      'kubernets',
    )
    await checkAs('Certain')
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(screen.getByText(/Watch the spelling/)).toHaveTextContent(
      "Watch the spelling: it's Kubernetes.",
    )
    expect(onAnswer).toHaveBeenCalledWith(
      true,
      { typed: 'kubernets', mistake: null, slip: true },
      'sure',
    )
  })

  it('offers "I don\'t know this" in the placement test, and shows no answer', async () => {
    const onAnswer = vi.fn()
    render(<TypedQuestion item={TYPED_TERM} quiet onAnswer={onAnswer} />)
    await userEvent.click(
      screen.getByRole('button', { name: "I don't know this" }),
    )
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(screen.queryByText(/Kubernetes runs/)).not.toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(false, null, null)
  })

  it('takes Enter as Check in the placement test, asking nothing more', async () => {
    const onAnswer = vi.fn()
    render(<TypedQuestion item={TYPED_TERM} quiet onAnswer={onAnswer} />)
    expect(
      screen.queryByRole('button', { name: 'Fairly sure' }),
    ).not.toBeInTheDocument()
    await userEvent.type(screen.getByRole('textbox'), 'Docker{Enter}')
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(screen.queryByText(/Not quite/)).not.toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(
      false,
      { typed: 'Docker', mistake: null, slip: false },
      null,
    )
  })
})
