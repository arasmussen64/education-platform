import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { CheckReport } from '../python/protocol.ts'
import type { CheckOutcome, RunOutcome } from '../python/runner.ts'
import { CodeRunner } from './CodeRunner.tsx'

// CodeMirror needs a real browser to lay itself out, so these tests swap the
// editor for a plain text box with the same name.
vi.mock('./CodeEditor.tsx', () => ({
  CodeEditor: (props: {
    initialCode: string
    onChange: (code: string) => void
    label: string
  }) => (
    <textarea
      aria-label={props.label}
      defaultValue={props.initialCode}
      onChange={(event) => props.onChange(event.target.value)}
    />
  ),
}))

const NOTHING_PRINTED: RunOutcome = {
  kind: 'done',
  result: { output: '', error: null },
}

function report(overrides: Partial<CheckReport>): CheckOutcome {
  return {
    kind: 'done',
    report: {
      status: 'ok',
      message: '',
      passed: 0,
      total: 0,
      results: [],
      ...overrides,
    },
  }
}

function fakeRunner(outcomes: { run?: RunOutcome; check?: CheckOutcome } = {}) {
  return {
    start: vi.fn((): Promise<void> => Promise.resolve()),
    run: vi.fn((): Promise<RunOutcome> =>
      Promise.resolve(outcomes.run ?? NOTHING_PRINTED),
    ),
    check: vi.fn((): Promise<CheckOutcome> =>
      Promise.resolve(outcomes.check ?? report({})),
    ),
  }
}

describe('CodeRunner', () => {
  it('runs the code and shows what it printed', async () => {
    const runner = fakeRunner({
      run: { kind: 'done', result: { output: 'Hello, Ada!\n', error: null } },
    })
    render(<CodeRunner initialCode="print('hi')" runner={runner} />)
    await userEvent.click(screen.getByRole('button', { name: 'Run' }))
    expect(await screen.findByText('Hello, Ada!')).toBeInTheDocument()
  })

  it('sends the edited code and the input to Python', async () => {
    const user = userEvent.setup()
    const runner = fakeRunner()
    render(<CodeRunner initialCode="" runner={runner} />)
    await user.type(screen.getByLabelText('Python code'), 'print(input())')
    await user.type(screen.getByLabelText(/Input for Run/), 'Ada')
    await user.click(screen.getByRole('button', { name: 'Run' }))
    expect(runner.run).toHaveBeenCalledWith('print(input())', 'Ada')
  })

  it('shows the traceback when the program crashes', async () => {
    const runner = fakeRunner({
      run: {
        kind: 'done',
        result: { output: '', error: 'ZeroDivisionError: division by zero' },
      },
    })
    render(<CodeRunner initialCode="1/0" runner={runner} />)
    await userEvent.click(screen.getByRole('button', { name: 'Run' }))
    expect(
      await screen.findByText(/ZeroDivisionError: division by zero/),
    ).toBeInTheDocument()
  })

  it('explains when code runs too long', async () => {
    const runner = fakeRunner({ run: { kind: 'timeout' } })
    render(<CodeRunner initialCode="while True: pass" runner={runner} />)
    await userEvent.click(screen.getByRole('button', { name: 'Run' }))
    expect(
      await screen.findByText(/ran for more than 5 seconds/),
    ).toBeInTheDocument()
  })

  it('only offers Check when there are tests', () => {
    render(<CodeRunner initialCode="" runner={fakeRunner()} />)
    expect(
      screen.queryByRole('button', { name: 'Check' }),
    ).not.toBeInTheDocument()
  })

  it('lists each check with its result', async () => {
    const runner = fakeRunner({
      check: report({
        passed: 1,
        total: 2,
        results: [
          {
            name: 'test_a',
            description: 'Greets the person',
            outcome: 'pass',
            message: '',
          },
          {
            name: 'test_b',
            description: 'Handles an empty name',
            outcome: 'fail',
            message: 'Check failed: assert run("\\n") == "Hello!\\n"',
          },
        ],
      }),
    })
    render(<CodeRunner initialCode="" tests="tests" runner={runner} />)
    await userEvent.click(screen.getByRole('button', { name: 'Check' }))
    expect(await screen.findByText('1 of 2 checks passed')).toBeInTheDocument()
    expect(screen.getByText('Greets the person')).toBeInTheDocument()
    expect(screen.getByText('Handles an empty name')).toBeInTheDocument()
    expect(screen.getByText(/Check failed/)).toBeInTheDocument()
    expect(runner.check).toHaveBeenCalledWith('', 'tests')
  })

  it('hides failure details for hidden tests, but still shows errors in your code', async () => {
    const runner = fakeRunner({
      check: report({
        passed: 0,
        total: 2,
        results: [
          {
            name: 'test_a',
            description: 'Rotates a list',
            outcome: 'fail',
            message: 'Check failed: assert rotate([1, 2]) == [2, 1]',
          },
          {
            name: 'test_b',
            description: 'Handles an empty list',
            outcome: 'error',
            message:
              'IndexError: list index out of range (solution.py, line 2)',
          },
        ],
      }),
    })
    render(
      <CodeRunner initialCode="" tests="tests" hiddenTests runner={runner} />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'Check' }))
    expect(await screen.findByText('Rotates a list')).toBeInTheDocument()
    expect(screen.queryByText(/Check failed/)).not.toBeInTheDocument()
    expect(screen.getByText(/IndexError/)).toBeInTheDocument()
  })

  it("says when the learner's code couldn't be loaded", async () => {
    const message =
      "Your code couldn't be loaded. SyntaxError: expected ':' (solution.py, line 1)"
    const runner = fakeRunner({ check: report({ status: 'error', message }) })
    render(<CodeRunner initialCode="" tests="tests" runner={runner} />)
    await userEvent.click(screen.getByRole('button', { name: 'Check' }))
    expect(await screen.findByText(message)).toBeInTheDocument()
  })

  it("says when Python couldn't start", async () => {
    const runner = fakeRunner()
    runner.start.mockImplementation(() => Promise.reject(new Error('offline')))
    render(<CodeRunner initialCode="" runner={runner} />)
    expect(await screen.findByText(/Python couldn't start/)).toBeInTheDocument()
  })

  it.each([
    { passed: 1, expected: 'The check passed!' },
    { passed: 0, expected: "The check didn't pass yet." },
  ])(
    'words a single check naturally ($expected)',
    async ({ passed, expected }) => {
      const runner = fakeRunner({ check: report({ passed, total: 1 }) })
      render(<CodeRunner initialCode="" tests="tests" runner={runner} />)
      await userEvent.click(screen.getByRole('button', { name: 'Check' }))
      expect(await screen.findByText(expected)).toBeInTheDocument()
    },
  )
})
