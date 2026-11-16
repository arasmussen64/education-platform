import { act, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { BackToTop } from './BackToTop.tsx'

// jsdom has no layout and no scrolling, so the page's scroll position is set
// by hand and scrollTo is a spy.
function scrollPageTo(y: number) {
  act(() => {
    Object.defineProperty(window, 'scrollY', { value: y, configurable: true })
    window.dispatchEvent(new Event('scroll'))
  })
}

const BUTTON = { name: 'Back to top' }

describe('the back-to-top button', () => {
  let scrollTo: ReturnType<typeof vi.fn>

  beforeEach(() => {
    Object.defineProperty(window, 'innerHeight', {
      value: 800,
      configurable: true,
    })
    Object.defineProperty(window, 'scrollY', { value: 0, configurable: true })
    scrollTo = vi.fn()
    window.scrollTo = scrollTo as unknown as typeof window.scrollTo
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('stays hidden until the page is scrolled more than one screen', () => {
    render(<BackToTop focusTarget={() => null} />)
    expect(screen.queryByRole('button', BUTTON)).toBeNull()

    scrollPageTo(800)
    expect(screen.queryByRole('button', BUTTON)).toBeNull()

    scrollPageTo(801)
    expect(screen.getByRole('button', BUTTON)).toBeVisible()

    scrollPageTo(10)
    expect(screen.queryByRole('button', BUTTON)).toBeNull()
  })

  it('scrolls to the top and moves focus there', () => {
    const top = document.createElement('header')
    top.tabIndex = -1
    document.body.append(top)
    render(<BackToTop focusTarget={() => top} />)

    scrollPageTo(2000)
    fireEvent.click(screen.getByRole('button', BUTTON))

    expect(scrollTo).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' })
    expect(top).toHaveFocus()
    top.remove()
  })

  it('jumps without animating when the system asks for less motion', () => {
    vi.stubGlobal('matchMedia', (query: string) => ({
      matches: query === '(prefers-reduced-motion: reduce)',
    }))
    render(<BackToTop focusTarget={() => null} />)

    scrollPageTo(2000)
    fireEvent.click(screen.getByRole('button', BUTTON))

    expect(scrollTo).toHaveBeenCalledWith({ top: 0, behavior: 'auto' })
  })
})
