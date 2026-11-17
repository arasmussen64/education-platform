import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'
import { GlossaryTerm } from './GlossaryTerm.tsx'

function renderTerm() {
  render(
    <MemoryRouter>
      <p>
        A{' '}
        <GlossaryTerm
          term="source NAT"
          definition="NAT that rewrites a packet's `source`."
          topicId="csa.net.nat"
          topicTitle="NAT"
        >
          SNAT
        </GlossaryTerm>{' '}
        gateway. <button type="button">Elsewhere</button>
      </p>
    </MemoryRouter>,
  )
  // Screen readers hear what the button does, not only the word.
  return screen.getByRole('button', { name: /^SNAT ?\(show its definition\)$/ })
}

describe('a glossary term in a lesson (ADR-0026)', () => {
  it('shows its definition and where it is taught when pressed', async () => {
    const term = renderTerm()
    expect(term).toHaveAttribute('aria-expanded', 'false')
    expect(screen.queryByText('Taught in:')).not.toBeInTheDocument()

    await userEvent.click(term)
    expect(term).toHaveAttribute('aria-expanded', 'true')
    const definition = document.getElementById(
      term.getAttribute('aria-controls') ?? '',
    )
    expect(definition).toHaveTextContent(
      "source NATNAT that rewrites a packet's source.Taught in: NAT · All terms",
    )
    expect(screen.getByRole('link', { name: 'NAT' })).toHaveAttribute(
      'href',
      '/topic/csa.net.nat',
    )
    expect(screen.getByRole('link', { name: 'All terms' })).toHaveAttribute(
      'href',
      '/glossary',
    )

    // Pressed again, it goes away.
    await userEvent.click(term)
    expect(term).toHaveAttribute('aria-expanded', 'false')
  })

  it('opens from the keyboard, and Escape closes it', async () => {
    const term = renderTerm()
    term.focus()
    await userEvent.keyboard('{Enter}')
    expect(term).toHaveAttribute('aria-expanded', 'true')
    await userEvent.tab()
    expect(screen.getByRole('link', { name: 'NAT' })).toHaveFocus()
    await userEvent.keyboard('{Escape}')
    expect(term).toHaveAttribute('aria-expanded', 'false')
    expect(term).toHaveFocus()
  })

  it('closes when the learner presses anywhere else', async () => {
    const term = renderTerm()
    await userEvent.click(term)
    await userEvent.click(screen.getByRole('button', { name: 'Elsewhere' }))
    expect(term).toHaveAttribute('aria-expanded', 'false')
  })

  it('shows while a mouse hovers, and not for a touch', () => {
    const term = renderTerm()
    const wrapper = term.parentElement as HTMLElement
    fireEvent.pointerEnter(wrapper, { pointerType: 'touch' })
    expect(term).toHaveAttribute('aria-expanded', 'false')
    fireEvent.pointerEnter(wrapper, { pointerType: 'mouse' })
    expect(term).toHaveAttribute('aria-expanded', 'true')
    fireEvent.pointerLeave(wrapper, { pointerType: 'mouse' })
    expect(term).toHaveAttribute('aria-expanded', 'false')
  })
})
