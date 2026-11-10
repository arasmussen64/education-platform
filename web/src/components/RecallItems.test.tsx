import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { MCQ, PARSONS, PREDICT, PREDICT_SHELL } from '../test/fakeContent.tsx'
import { McqQuestion } from './McqQuestion.tsx'
import { ParsonsProblem } from './ParsonsProblem.tsx'
import { PredictOutput } from './PredictOutput.tsx'

vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
import { scramble } from './scramble.ts'

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

describe('"I don\'t know this" in the placement test (ADR-0021)', () => {
  const dontKnow = "I don't know this"

  it('is a last choice on a multiple-choice question, taken as a wrong answer', async () => {
    const onAnswer = vi.fn()
    render(<McqQuestion item={MCQ} quiet onAnswer={onAnswer} />)
    const radios = screen.getAllByRole('radio')
    expect(radios.at(-1)).toHaveAccessibleName(dontKnow)
    await userEvent.click(screen.getByRole('radio', { name: dontKnow }))
    await check()
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(false, null)
  })

  it('is a button beside Check for a prediction, with nothing typed', async () => {
    const onAnswer = vi.fn()
    render(<PredictOutput item={PREDICT} quiet onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('button', { name: dontKnow }))
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(screen.getByLabelText('What will it print?')).toBeDisabled()
    expect(onAnswer).toHaveBeenCalledWith(false, null)
  })

  it('is a button beside Check for a Parsons problem, even with no lines placed', async () => {
    const onAnswer = vi.fn()
    render(<ParsonsProblem item={PARSONS} quiet onAnswer={onAnswer} />)
    expect(screen.getByRole('button', { name: 'Check' })).toBeDisabled()
    await userEvent.click(screen.getByRole('button', { name: dontKnow }))
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(false, null)
  })

  it('is not offered in practice, where a wrong answer is followed by the explanation', () => {
    render(<McqQuestion item={MCQ} />)
    render(<PredictOutput item={PREDICT} />)
    render(<ParsonsProblem item={PARSONS} />)
    expect(
      screen.queryByRole('radio', { name: dontKnow }),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: dontKnow }),
    ).not.toBeInTheDocument()
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

describe('PredictOutput, stepped through afterwards (ADR-0022)', () => {
  it('offers to step through the code once the prediction is checked', async () => {
    const { setFakeRunner } = await import('../test/mockPython.ts')
    const { fakeRunner } = await import('../test/fakePython.ts')
    const runner = setFakeRunner(fakeRunner())
    const onStepThrough = vi.fn()
    render(<PredictOutput item={PREDICT} onStepThrough={onStepThrough} />)
    expect(
      screen.queryByRole('button', { name: 'Step through it' }),
    ).not.toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('What will it print?'), 'a')
    await userEvent.click(screen.getByRole('button', { name: 'Check' }))
    await userEvent.click(
      screen.getByRole('button', { name: 'Step through it' }),
    )
    expect(await screen.findByText('Step 1 of 4')).toBeInTheDocument()
    expect(runner.trace).toHaveBeenCalledWith(PREDICT.code, {
      timeLimitMs: 5000,
    })
    expect(onStepThrough).toHaveBeenCalledTimes(1)
  })

  it('offers nothing in the placement test, which shows no answers', async () => {
    render(<PredictOutput item={PREDICT} quiet />)
    await userEvent.type(screen.getByLabelText('What will it print?'), 'a')
    await userEvent.click(screen.getByRole('button', { name: 'Check' }))
    expect(screen.getByText('Answer recorded.')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Step through it' }),
    ).not.toBeInTheDocument()
  })
})

describe('PredictOutput for a shell command', () => {
  const pre = (text: string) =>
    screen.getByText(
      (_, node) => node?.tagName === 'PRE' && node.textContent === text,
    )

  it('shows the files the command sees, then the command at a prompt', () => {
    render(<PredictOutput item={PREDICT_SHELL} />)
    expect(screen.getByText('The folder holds one file:')).toBeInTheDocument()
    expect(screen.getByText('names.txt')).toBeInTheDocument()
    expect(pre('ada\ngrace\nada\n')).toBeInTheDocument()
    expect(pre('$ grep -c ada names.txt')).toBeInTheDocument()
  })

  it('grades the prediction like any other output', async () => {
    const onAnswer = vi.fn()
    render(<PredictOutput item={PREDICT_SHELL} onAnswer={onAnswer} />)
    await userEvent.type(screen.getByLabelText('What will it print?'), '2')
    await check()
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(screen.getByText(/counts the matching lines/)).toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(true, '2')
  })
})

describe('ParsonsProblem', () => {
  const add = (line: string) =>
    userEvent.click(screen.getByRole('button', { name: `Add: ${line}` }))
  const programList = () =>
    within(screen.getByRole('region', { name: 'Your program' })).queryAllByRole(
      'listitem',
    )

  it('scrambles the lines and the decoy the same way every time, never solved', () => {
    const once = scramble(PARSONS)
    expect(scramble(PARSONS)).toEqual(once)
    expect(once).toHaveLength(5)
    expect([...once].sort()).toEqual(
      [...PARSONS.lines, ...PARSONS.distractors].sort(),
    )
    expect(once.slice(0, 4)).not.toEqual(PARSONS.lines)
  })

  it('starts empty, says a decoy is in the mix, and waits for a line before checking', () => {
    render(<ParsonsProblem item={PARSONS} />)
    expect(programList()).toHaveLength(0)
    expect(
      screen.getByText("One line is a decoy that doesn't belong."),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Check' })).toBeDisabled()
    expect(screen.getAllByRole('button', { name: /^Add: / })).toHaveLength(5)
  })

  it('is right when the lines are in order without the decoy', async () => {
    const onAnswer = vi.fn()
    render(<ParsonsProblem item={PARSONS} onAnswer={onAnswer} />)
    // Added out of order, then fixed with Up and Down.
    await add('while count > 0:')
    await add('count = 3')
    await add('count = count - 1')
    await add('print(count)')
    await userEvent.click(
      screen.getByRole('button', { name: 'Move up: count = 3' }),
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Move down: count = count - 1' }),
    )
    expect(programList().map((item) => item.textContent)).toEqual([
      'count = 3UpDownRemove',
      'while count > 0:UpDownRemove',
      '    print(count)UpDownRemove',
      '    count = count - 1UpDownRemove',
    ])
    await check()
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(screen.getByText(PARSONS.explanation)).toBeInTheDocument()
    expect(onAnswer).toHaveBeenCalledWith(true, PARSONS.lines)
  })

  it('is wrong with the decoy in, shows the program, and locks the lines', async () => {
    const onAnswer = vi.fn()
    render(<ParsonsProblem item={PARSONS} onAnswer={onAnswer} />)
    await add('count = 3')
    await add('while count < 0:')
    await add('print(count)')
    await add('count = count - 1')
    // Removing puts a line back in the tray.
    await userEvent.click(
      screen.getByRole('button', { name: 'Remove: count = count - 1' }),
    )
    expect(
      screen.getByRole('button', { name: 'Add: count = count - 1' }),
    ).toBeInTheDocument()
    await add('count = count - 1')
    await check()
    expect(screen.getByText(/Not quite. The program is:/)).toBeInTheDocument()
    // The right program, with its line breaks and indentation kept.
    const shown = screen.getByText((_, node) => node?.tagName === 'PRE')
    expect(shown.textContent).toBe(PARSONS.lines.join('\n'))
    expect(
      screen.getByRole('button', { name: 'Add: while count > 0:' }),
    ).toBeDisabled()
    expect(
      screen.getByRole('button', { name: 'Remove: count = 3' }),
    ).toBeDisabled()
    expect(onAnswer).toHaveBeenCalledWith(false, [
      'count = 3',
      'while count < 0:',
      '    print(count)',
      '    count = count - 1',
    ])
  })
})
