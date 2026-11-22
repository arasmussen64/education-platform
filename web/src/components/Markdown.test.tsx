import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Markdown } from './Markdown.tsx'

describe('Markdown', () => {
  it('draws a table as a table, not as a line of | characters', () => {
    render(
      <Markdown>
        {'| line | pages |\n| --- | --- |\n| 1 | 40 |\n| 2 | 25 |'}
      </Markdown>,
    )
    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(
      screen.getAllByRole('columnheader').map((cell) => cell.textContent),
    ).toEqual(['line', 'pages'])
    expect(screen.getAllByRole('row')).toHaveLength(3)
    expect(screen.getByRole('cell', { name: '40' })).toBeInTheDocument()
  })

  it('adds tables only: a tilde and a bare address stay as written', () => {
    render(<Markdown>{'About ~5~ at https://example.com today.'}</Markdown>)
    expect(
      screen.getByText('About ~5~ at https://example.com today.'),
    ).toBeInTheDocument()
    expect(screen.queryByRole('link')).not.toBeInTheDocument()
  })
})
