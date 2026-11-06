import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { fakeRunner, printed, report } from '../test/fakePython.ts'
import { CodeRunner } from './CodeRunner.tsx'

vi.mock('./CodeEditor.tsx', () => import('../test/FakeCodeEditor.tsx'))

describe('CodeRunner', () => {
  it('runs the code and shows what it printed', async () => {
    const runner = fakeRunner({ run: printed('Hello, world!\n') })
    render(<CodeRunner initialCode="print('hi')" runner={runner} />)
    await userEvent.click(screen.getByRole('button', { name: 'Run' }))
    expect(await screen.findByText('Hello, world!')).toBeInTheDocument()
  })

  it('runs the code that is in the editor', async () => {
    const user = userEvent.setup()
    const runner = fakeRunner()
    render(<CodeRunner initialCode="" runner={runner} />)
    await user.type(screen.getByLabelText('Python code'), 'print(1)')
    await user.click(screen.getByRole('button', { name: 'Run' }))
    expect(runner.run).toHaveBeenCalledWith('print(1)', {
      stdin: '',
      seed: expect.any(Number),
      timeLimitMs: 5000,
    })
  })

  it('asks for input like a terminal, then runs again with the answer', async () => {
    const user = userEvent.setup()
    const runner = fakeRunner()
    runner.run
      .mockResolvedValueOnce(printed("What's your name? ", true))
      .mockResolvedValueOnce(printed("What's your name? Ada\nHello, Ada!\n"))
    render(<CodeRunner initialCode="code" runner={runner} />)

    await user.click(screen.getByRole('button', { name: 'Run' }))
    const field = await screen.findByRole('textbox', { name: 'Program input' })
    expect(field).toHaveFocus()
    // Never a real form field: password managers (NordPass, for one) treat a
    // field after "What's your name?" as a contact form and pop up.
    expect(field.tagName).toBe('SPAN')
    expect(screen.getByText(/waiting for input/)).toBeInTheDocument()

    await user.type(field, 'Ada{Enter}')
    expect(await screen.findByText(/Hello, Ada!/)).toBeInTheDocument()
    expect(screen.queryByLabelText('Program input')).not.toBeInTheDocument()

    const [first, second] = runner.run.mock.calls
    expect(first).toEqual([
      'code',
      { stdin: '', seed: expect.any(Number), timeLimitMs: 5000 },
    ])
    // The re-run uses the same seed, so random choices repeat.
    expect(second).toEqual([
      'code',
      { stdin: 'Ada\n', seed: first[1]?.seed, timeLimitMs: 5000 },
    ])
  })

  it('keeps the code it started with while the program waits for input', async () => {
    const user = userEvent.setup()
    const runner = fakeRunner()
    runner.run.mockResolvedValueOnce(printed('Name? ', true))
    render(<CodeRunner initialCode="original" runner={runner} />)

    await user.click(screen.getByRole('button', { name: 'Run' }))
    const field = await screen.findByLabelText('Program input')
    await user.type(screen.getByLabelText('Python code'), ' edited')
    await user.type(field, 'Ada{Enter}')

    expect(runner.run.mock.calls[1]?.[0]).toBe('original')
  })

  it('shows the traceback when the program crashes', async () => {
    const runner = fakeRunner({
      run: {
        kind: 'done',
        result: {
          output: '',
          error: 'ZeroDivisionError: division by zero',
          waiting_for_input: false,
        },
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

  it("uses the exercise's own time limit", async () => {
    const runner = fakeRunner({ run: { kind: 'timeout' } })
    render(
      <CodeRunner
        initialCode="while True: pass"
        runner={runner}
        timeLimitMs={1000}
      />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'Run' }))
    expect(
      await screen.findByText(/ran for more than 1 second,/),
    ).toBeInTheDocument()
    expect(runner.run.mock.calls[0]?.[1]?.timeLimitMs).toBe(1000)
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
    expect(runner.check).toHaveBeenCalledWith('', 'tests', {
      timeLimitMs: 5000,
    })
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
