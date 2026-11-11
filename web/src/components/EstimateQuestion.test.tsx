import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { EstimateItem } from '../content/types.ts'
import { ESTIMATE } from '../test/fakeContent.tsx'
import { EstimateQuestion } from './EstimateQuestion.tsx'

const box = () => screen.getByRole('textbox', { name: 'Your answer' })
const check = () =>
  userEvent.click(screen.getByRole('button', { name: 'Check' }))

/** Types into the number box and presses Check. */
async function answer(typed: string) {
  await userEvent.type(box(), typed)
  await check()
}

/** An exact count, with no prices. */
const LICENCES: EstimateItem = {
  id: 'count-licences',
  type: 'estimate',
  rev: 1,
  prompt: 'Three VMs have 2, 8 and 12 vCPUs. How many core licences? Exact.',
  unit: 'core licences',
  answer: 28,
  tolerance: { absolute: 0 },
  given: { a: 2, b: 8, c: 12 },
  working: 'max(8, a) + max(8, b) + max(8, c)',
  mistakes: [
    {
      id: 'no-floor',
      value: 22,
      working: 'a + b + c',
      why: 'That counts vCPUs; each VM needs at least 8.',
    },
  ],
  explanation: '8 + 8 + 12 = 28.',
  skills: ['print-text'],
}

describe('EstimateQuestion', () => {
  it('asks for a number in a labelled box with the unit beside it', () => {
    render(<EstimateQuestion item={ESTIMATE} />)
    expect(screen.getByText(/What do the two cost in a month/)).toBeVisible()
    expect(box()).toHaveAccessibleDescription('dollars a month')
    expect(screen.getByRole('button', { name: 'Check' })).toBeDisabled()
    // A phone's decimal keypad may offer only a comma, which isn't read.
    expect(box()).toHaveAttribute('inputmode', 'text')
  })

  it("says when the prices were read, and where today's are", () => {
    render(<EstimateQuestion item={ESTIMATE} />)
    expect(
      screen.getByText(/These prices were read on November 10, 2026/),
    ).toBeVisible()
    expect(
      screen.getByRole('link', { name: "the provider's price page" }),
    ).toHaveAttribute('href', 'https://example.com/prices')
    render(<EstimateQuestion item={LICENCES} />)
    expect(screen.getAllByText(/These prices were read/)).toHaveLength(1)
  })

  it('reads only the day of a date that has a time after it', () => {
    render(
      <EstimateQuestion
        item={{ ...ESTIMATE, prices_as_of: '2026-11-10T09:30:00' }}
      />,
    )
    expect(
      screen.getByText(/These prices were read on November 10, 2026/),
    ).toBeVisible()
  })

  it('is right within the tolerance, and says how close it was', async () => {
    const onAnswer = vi.fn()
    render(<EstimateQuestion item={ESTIMATE} onAnswer={onAnswer} />)
    await answer('$85')
    const result = screen.getByRole('status')
    expect(result).toHaveTextContent(
      'Correct! The answer is 87.6 dollars a month.',
    )
    expect(result).toHaveTextContent('Yours, 85, is 3% low: close enough.')
    expect(result).toHaveTextContent('(vm + disk) * hours')
    expect(result).toHaveTextContent('with vm = 0.1, disk = 0.02, hours = 730')
    expect(result).toHaveTextContent(ESTIMATE.explanation)
    expect(box()).toBeDisabled()
    expect(onAnswer).toHaveBeenCalledWith(true, {
      typed: '$85',
      number: 85,
      relativeError: expect.closeTo(-0.0297, 4),
      mistake: null,
    })
  })

  it('names the slip when a wrong answer matches a known mistake', async () => {
    const onAnswer = vi.fn()
    render(<EstimateQuestion item={ESTIMATE} onAnswer={onAnswer} />)
    await answer('73')
    const result = screen.getByRole('status')
    expect(result).toHaveTextContent('Not quite. The answer is 87.6')
    expect(result).toHaveTextContent(
      'Yours, 73, is 17% low; anything from 78.84 to 96.36 counts.',
    )
    expect(result).toHaveTextContent(
      "A common slipThat's the VM alone; its disk is billed too.",
    )
    expect(onAnswer).toHaveBeenCalledWith(
      false,
      expect.objectContaining({ number: 73, mistake: 'vm-only' }),
    )
  })

  it('names no slip for a wrong answer that matches none', async () => {
    const onAnswer = vi.fn()
    render(<EstimateQuestion item={ESTIMATE} onAnswer={onAnswer} />)
    await answer('120')
    expect(screen.getByRole('status')).toHaveTextContent(
      'Yours, 120, is 37% high;',
    )
    expect(screen.queryByText('A common slip')).not.toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(
      false,
      expect.objectContaining({ mistake: null }),
    )
  })

  it('counts the difference in units when the answer must be exact', async () => {
    render(<EstimateQuestion item={LICENCES} />)
    await answer('22')
    const result = screen.getByRole('status')
    expect(result).toHaveTextContent('The answer is 28 core licences.')
    expect(result).toHaveTextContent(
      'Yours, 22, is 6 low, and this one must be exact.',
    )
    expect(result).toHaveTextContent('each VM needs at least 8')
  })

  it("says how to type a number it can't read, and counts nothing", async () => {
    const onAnswer = vi.fn()
    render(<EstimateQuestion item={ESTIMATE} onAnswer={onAnswer} />)
    await answer('about 90')
    expect(screen.getByText(/Type a number, like 1168/)).toBeVisible()
    expect(box()).toHaveAttribute('aria-invalid', 'true')
    expect(box()).toHaveAccessibleDescription(/dollars a month Type a number/)
    expect(box()).toBeEnabled()
    expect(onAnswer).not.toHaveBeenCalled()
    // Typing again clears the note; Enter checks, like the button.
    await userEvent.clear(box())
    expect(screen.queryByText(/Type a number, like/)).not.toBeInTheDocument()
    await userEvent.type(box(), '87.6{Enter}')
    expect(onAnswer).toHaveBeenCalledWith(
      true,
      expect.objectContaining({ typed: '87.6', number: 87.6 }),
    )
  })

  it('takes a % only when the answer is a percentage', async () => {
    const onAnswer = vi.fn()
    render(<EstimateQuestion item={ESTIMATE} onAnswer={onAnswer} />)
    await answer('88%')
    expect(
      screen.getByText('Leave out the %: the answer is in dollars a month.'),
    ).toBeVisible()
    expect(onAnswer).not.toHaveBeenCalled()
  })
})

describe('EstimateQuestion in the placement test (ADR-0021)', () => {
  it('records the answer without saying whether it was right', async () => {
    const onAnswer = vi.fn()
    render(<EstimateQuestion item={ESTIMATE} quiet onAnswer={onAnswer} />)
    await answer('73')
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(screen.queryByText(/Not quite/)).not.toBeInTheDocument()
    expect(screen.queryByText(ESTIMATE.explanation)).not.toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(
      false,
      expect.objectContaining({ number: 73 }),
    )
  })

  it('offers "I don\'t know this", taken as a wrong answer', async () => {
    const onAnswer = vi.fn()
    render(<EstimateQuestion item={ESTIMATE} quiet onAnswer={onAnswer} />)
    await userEvent.click(
      screen.getByRole('button', { name: "I don't know this" }),
    )
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(box()).toBeDisabled()
    expect(onAnswer).toHaveBeenCalledWith(false, null)
  })

  it('is not offered in practice', () => {
    render(<EstimateQuestion item={ESTIMATE} />)
    expect(
      screen.queryByRole('button', { name: "I don't know this" }),
    ).not.toBeInTheDocument()
  })
})
