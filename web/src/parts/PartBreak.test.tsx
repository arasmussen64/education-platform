import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { BREAK_MS, PartBreak } from './PartBreak.tsx'

describe('a short break between parts', () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ['Date', 'setInterval', 'clearInterval'] })
    vi.setSystemTime(new Date(2026, 10, 16, 10))
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('suggests resting, and can be skipped', async () => {
    const onDismiss = vi.fn()
    render(<PartBreak finished="Learn" onDismiss={onDismiss} />)
    const card = screen.getByRole('complementary', { name: 'A short break' })
    expect(card).toHaveTextContent('Learn: done.')
    expect(card).toHaveTextContent('five-minute break')
    expect(screen.queryByRole('timer')).toBeNull()
    await userEvent.click(
      screen.getByRole('button', { name: 'Skip the break' }),
    )
    expect(onDismiss).toHaveBeenCalledOnce()
  })

  it('counts five minutes down on the page, and says when the break is over', async () => {
    render(<PartBreak finished="Practice" onDismiss={() => {}} />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Start a 5-minute timer' }),
    )
    expect(screen.getByRole('timer')).toHaveTextContent('5:00')
    act(() => vi.advanceTimersByTime(55_000))
    expect(screen.getByRole('timer')).toHaveTextContent('4:05')
    expect(
      screen.getByRole('button', { name: 'End the break' }),
    ).toBeInTheDocument()

    act(() => vi.advanceTimersByTime(BREAK_MS))
    expect(screen.getByRole('timer')).toHaveTextContent('0:00')
    expect(screen.getByRole('status')).toHaveTextContent("Break's over.")
    expect(screen.getByRole('button', { name: 'Close' })).toBeInTheDocument()
  })

  it('shows the right time after the tab was in the background', async () => {
    render(<PartBreak finished="Practice" onDismiss={() => {}} />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Start a 5-minute timer' }),
    )
    // The clock moved on two minutes while the page's timer was held back.
    vi.setSystemTime(Date.now() + 120_000)
    act(() => vi.advanceTimersByTime(1000))
    expect(screen.getByRole('timer')).toHaveTextContent('2:59')
  })
})
