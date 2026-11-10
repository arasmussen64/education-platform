import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import type { TraceResult } from '../python/protocol.ts'
import { SIMPLE_CODE, SIMPLE_STEPS, traced } from '../test/fakePython.ts'
import { StepThrough } from './StepThrough.tsx'
import { describeStep } from './stepText.ts'

function simple(overrides: Partial<TraceResult> = {}): TraceResult {
  const outcome = traced(overrides)
  if (outcome.kind !== 'done') throw new Error('a finished trace')
  return outcome.trace
}

const currentLine = () =>
  screen.getByLabelText('Code').querySelector('[aria-current="step"]')

describe('StepThrough', () => {
  it('starts at the first step, with the line marked and no variables yet', () => {
    render(<StepThrough code={SIMPLE_CODE} trace={simple()} />)
    expect(screen.getByText('Step 1 of 4')).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent(
      'Line 1 is about to run.',
    )
    expect(currentLine()).toHaveTextContent('1 x = 1')
    expect(
      within(
        screen.getByRole('table', { name: 'Variables: The program' }),
      ).getByText('No variables yet'),
    ).toBeInTheDocument()
    expect(screen.getByText('Nothing printed yet')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Back' })).toBeDisabled()
  })

  it('moves through the steps, showing the variables and output so far', async () => {
    render(<StepThrough code={SIMPLE_CODE} trace={simple()} />)
    await userEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(screen.getByText('Step 2 of 4')).toBeInTheDocument()
    expect(currentLine()).toHaveTextContent('2 y = x + 1')
    const table = screen.getByRole('table', { name: 'Variables: The program' })
    expect(within(table).getByRole('row', { name: /x 1/ })).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Last' }))
    expect(screen.getByText('Step 4 of 4')).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('The program ends.')
    expect(screen.getByText('1 2')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Next' })).toBeDisabled()

    await userEvent.click(screen.getByRole('button', { name: 'First' }))
    expect(screen.getByText('Step 1 of 4')).toBeInTheDocument()
  })

  it('shows each running call, innermost first, and what it returns', () => {
    const trace = simple({
      steps: [
        {
          line: 2,
          event: 'return',
          frames: [
            {
              name: 'program',
              line: 4,
              vars: [['double', 'function double']],
              returns: null,
            },
            { name: 'double', line: 2, vars: [['n', '4']], returns: '8' },
          ],
          out_len: 0,
        },
      ],
    })
    render(
      <StepThrough
        code={'def double(n):\n    return n * 2\n\nresult = double(4)\n'}
        trace={trace}
      />,
    )
    expect(screen.getByRole('status')).toHaveTextContent('double() returns 8.')
    const tables = screen.getAllByRole('table')
    expect(tables[0]).toHaveAccessibleName('Variables: double()')
    expect(tables[0]).toHaveTextContent('returns 8')
    expect(tables[1]).toHaveAccessibleName('Variables: The program')
  })

  it('shows the error at the last step', async () => {
    const trace = simple({
      steps: [
        SIMPLE_STEPS[0]!,
        {
          line: 2,
          event: 'exception',
          frames: [SIMPLE_STEPS[1]!.frames[0]!],
          out_len: 0,
        },
      ],
      error:
        'Traceback (most recent call last):\n  File "solution.py", line 2, in <module>\nZeroDivisionError: division by zero\n',
    })
    render(<StepThrough code={'x = 1\ny = x / 0\n'} trace={trace} />)
    expect(screen.queryByText(/ZeroDivisionError/)).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Last' }))
    expect(screen.getByRole('status')).toHaveTextContent(
      'Error at line 2: ZeroDivisionError: division by zero',
    )
    expect(screen.getByText(/Traceback/)).toBeInTheDocument()
  })

  it('says when the recording stopped early or the program wanted input', async () => {
    const { unmount } = render(
      <StepThrough code={SIMPLE_CODE} trace={simple({ truncated: true })} />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'Last' }))
    expect(
      screen.getByText(/Recording stopped after 4 steps/),
    ).toBeInTheDocument()
    unmount()
    render(
      <StepThrough
        code={SIMPLE_CODE}
        trace={simple({ steps: [SIMPLE_STEPS[0]!], waiting_for_input: true })}
      />,
    )
    expect(screen.getByText(/asked for more input/)).toBeInTheDocument()
  })

  it('has something to say when the program never started', () => {
    render(
      <StepThrough
        code="print("
        trace={simple({ steps: [], error: 'SyntaxError: ...' })}
      />,
    )
    expect(screen.getByText(/didn't get to its first line/)).toBeInTheDocument()
    expect(screen.getByText('SyntaxError: ...')).toBeInTheDocument()
  })

  it('describes a call with its arguments', () => {
    expect(
      describeStep(
        {
          line: 1,
          event: 'call',
          frames: [
            { name: 'program', line: 4, vars: [], returns: null },
            {
              name: 'greet',
              line: 1,
              vars: [
                ['name', "'Ada'"],
                ['times', '2'],
              ],
              returns: null,
            },
          ],
          out_len: 0,
        },
        simple(),
      ),
    ).toBe("Calling greet(name = 'Ada', times = 2).")
  })
})
