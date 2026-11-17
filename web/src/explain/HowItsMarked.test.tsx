import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import type { Explain } from '../content/types.ts'
import { HowItsMarked } from './HowItsMarked.tsx'
import { pointsSentence } from './marking.ts'

const EXPLAIN: Explain = {
  prompt: 'Why does `names` become `None`?',
  rubric: [
    {
      id: 'append-in-place',
      required: true,
      description: 'append changes the list; it returns None.',
    },
    {
      id: 'none',
      required: true,
      description: 'Assigning the result replaced the list with None.',
    },
    {
      id: 'index',
      required: false,
      description: 'The last item is names[-1].',
    },
  ],
  model_answer: 'SECRET MODEL ANSWER',
}

describe('how an explanation is marked', () => {
  it('says how many points there are and what a pass needs, behind a fold', async () => {
    render(<HowItsMarked explain={EXPLAIN} />)
    const summary = screen.getByText("How it's marked")
    expect(summary.closest('details')).not.toHaveAttribute('open')
    await userEvent.click(summary)
    expect(summary.closest('details')).toHaveAttribute('open')
    expect(
      screen.getByText(
        "Your explanation is checked against three points, drawn from the question above: two needed to pass, and one extra that isn't needed.",
      ),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/The ideas count, not the wording/),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/up to three questions about it/),
    ).toBeInTheDocument()
  })

  it("never shows the points' wording, which is the answer, or the model answer", () => {
    render(<HowItsMarked explain={EXPLAIN} />)
    for (const point of EXPLAIN.rubric) {
      expect(document.body).not.toHaveTextContent(point.description)
    }
    expect(document.body).not.toHaveTextContent('SECRET MODEL ANSWER')
  })

  it('counts in words that read well', () => {
    expect(pointsSentence(1, 1, 0)).toBe(
      'Your explanation is checked against one point, drawn from the question above, and a pass needs it.',
    )
    expect(pointsSentence(4, 4, 0)).toMatch(
      /four points, drawn from the question above, and a pass needs every one\.$/,
    )
    expect(pointsSentence(6, 4, 2)).toMatch(
      /six points, .*: four needed to pass, and two extra that aren't needed\.$/,
    )
    expect(pointsSentence(12, 12, 0)).toMatch(/against 12 points/)
  })

  it('shows nothing for a rubric with no points', () => {
    const { container } = render(
      <HowItsMarked explain={{ ...EXPLAIN, rubric: [] }} />,
    )
    expect(container).toBeEmptyDOMElement()
  })
})
