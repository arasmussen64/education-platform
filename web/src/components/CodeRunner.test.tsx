import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ComponentProps } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { loadDraft, saveDraft } from '../drafts/drafts.ts'
import {
  allPassed,
  fakeRunner,
  oneFailed,
  printed,
  report,
} from '../test/fakePython.ts'
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
      packages: [],
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
      { stdin: '', seed: expect.any(Number), timeLimitMs: 5000, packages: [] },
    ])
    // The re-run uses the same seed, so random choices repeat.
    expect(second).toEqual([
      'code',
      {
        stdin: 'Ada\n',
        seed: first[1]?.seed,
        timeLimitMs: 5000,
        packages: [],
      },
    ])
  })

  it('reports each press of Run once, with its code, but not typed input', async () => {
    const user = userEvent.setup()
    const runner = fakeRunner()
    runner.run
      .mockResolvedValueOnce(printed('Name? ', true))
      .mockResolvedValueOnce(printed('Name? Ada\nHi, Ada\n'))
    const onRun = vi.fn()
    render(<CodeRunner initialCode="code" runner={runner} onRun={onRun} />)

    await user.click(screen.getByRole('button', { name: 'Run' }))
    await user.type(await screen.findByLabelText('Program input'), 'Ada{Enter}')
    await screen.findByText(/Hi, Ada/)

    expect(onRun).toHaveBeenCalledTimes(1)
    expect(onRun).toHaveBeenCalledWith(printed('Name? ', true), 'code')
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
    const onCheck = vi.fn()
    render(
      <CodeRunner
        initialCode=""
        tests="tests"
        runner={runner}
        onCheck={onCheck}
      />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'Check' }))
    expect(await screen.findByText('1 of 2 checks passed')).toBeInTheDocument()
    expect(screen.getByText('Greets the person')).toBeInTheDocument()
    expect(screen.getByText('Handles an empty name')).toBeInTheDocument()
    expect(screen.getByText(/Check failed/)).toBeInTheDocument()
    expect(runner.check).toHaveBeenCalledWith('', 'tests', {
      timeLimitMs: 5000,
      packages: [],
    })
    // The result is reported along with the code that was checked.
    expect(onCheck).toHaveBeenCalledWith(
      expect.objectContaining({ kind: 'done' }),
      '',
    )
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

  it('steps through the code, with the input and seed of the last run', async () => {
    const user = userEvent.setup()
    const runner = fakeRunner()
    runner.run
      .mockResolvedValueOnce(printed('Name? ', true))
      .mockResolvedValueOnce(printed('Name? Ada\nHi Ada\n'))
    const onTrace = vi.fn()
    render(<CodeRunner initialCode="code" runner={runner} onTrace={onTrace} />)

    await user.click(screen.getByRole('button', { name: 'Run' }))
    await user.type(
      await screen.findByRole('textbox', { name: 'Program input' }),
      'Ada{Enter}',
    )
    await screen.findByText(/Hi Ada!?/)
    await user.click(screen.getByRole('button', { name: 'Step through' }))

    expect(
      await screen.findByRole('heading', { name: 'Step through' }),
    ).toBeInTheDocument()
    expect(screen.getByText('Step 1 of 4')).toBeInTheDocument()
    const seed = runner.run.mock.calls[0]?.[1]?.seed
    expect(runner.trace).toHaveBeenCalledWith('code', {
      stdin: 'Ada\n',
      seed,
      timeLimitMs: 5000,
      packages: [],
    })
    expect(onTrace).toHaveBeenCalledWith(
      await runner.trace.mock.results[0]?.value,
      'code',
    )
  })

  it('says when stepping through ran out of time', async () => {
    const runner = fakeRunner({ trace: { kind: 'timeout' } })
    render(<CodeRunner initialCode="while True: pass" runner={runner} />)
    await userEvent.click(screen.getByRole('button', { name: 'Step through' }))
    expect(
      await screen.findByText(/ran for more than 5 seconds/),
    ).toBeInTheDocument()
  })
})

describe('CodeRunner drafts', () => {
  const WHERE = { topicId: 'py.loops', itemId: 'fill-sum', rev: 1 }
  const STARTER = 'total = 0'

  beforeEach(() => {
    // Drafts note when they were saved; pinned, so no test reads the clock.
    vi.useFakeTimers({ toFake: ['Date'] })
    vi.setSystemTime(new Date('2026-11-11T12:00:00.000Z'))
  })
  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  function renderRunner(
    props: Partial<ComponentProps<typeof CodeRunner>> = {},
  ) {
    return render(
      <CodeRunner
        initialCode={STARTER}
        draft={WHERE}
        tests="tests"
        runner={fakeRunner()}
        {...props}
      />,
    )
  }
  const editor = () => screen.getByLabelText('Python code')
  const startOver = () => screen.queryByRole('button', { name: 'Start over' })
  const restoredNote = () => screen.queryByText(/your code from last time/)

  it('keeps the code typed so far when the editor comes back', async () => {
    const user = userEvent.setup()
    const first = renderRunner()
    await user.type(editor(), '\nfor n in nums:')
    // A link, "Prove it now" or "Hide the steps" takes the editor away.
    first.unmount()

    renderRunner()
    expect(editor()).toHaveValue('total = 0\nfor n in nums:')
    expect(restoredNote()).toBeInTheDocument()
  })

  it('runs the restored code, and tells the parent it is the code now', async () => {
    saveDraft(WHERE, 'total = 0\nprint(total)')
    const runner = fakeRunner()
    const onCodeChange = vi.fn()
    renderRunner({ runner, onCodeChange })
    // The tutor reads the code through onCodeChange.
    expect(onCodeChange).toHaveBeenCalledWith('total = 0\nprint(total)')
    await userEvent.click(screen.getByRole('button', { name: 'Run' }))
    expect(runner.run.mock.calls[0]?.[0]).toBe('total = 0\nprint(total)')
  })

  it('starts from the starter next time, once the checks pass', async () => {
    const user = userEvent.setup()
    const first = renderRunner({
      runner: fakeRunner({ check: allPassed('Sums the numbers') }),
    })
    await user.type(editor(), '\nfor n in nums:')
    await user.click(screen.getByRole('button', { name: 'Check' }))
    await screen.findByText('The check passed!')
    first.unmount()

    expect(loadDraft(WHERE)).toBeNull()
    renderRunner()
    expect(editor()).toHaveValue(STARTER)
    expect(restoredNote()).not.toBeInTheDocument()
  })

  it('keeps the draft after a Check that fails', async () => {
    const user = userEvent.setup()
    const first = renderRunner({
      runner: fakeRunner({ check: oneFailed('Sums the numbers') }),
    })
    await user.type(editor(), '\nfor n in nums:')
    await user.click(screen.getByRole('button', { name: 'Check' }))
    await screen.findByText("The check didn't pass yet.")
    first.unmount()

    renderRunner()
    expect(editor()).toHaveValue('total = 0\nfor n in nums:')
  })

  it('starts over from the starter, after asking first', async () => {
    const user = userEvent.setup()
    saveDraft(WHERE, 'total = 0\nfor n in nums:')
    const onCodeChange = vi.fn()
    const first = renderRunner({ onCodeChange })
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)

    // Saying no leaves everything as it was.
    await user.click(startOver()!)
    expect(confirm).toHaveBeenCalledTimes(1)
    expect(editor()).toHaveValue('total = 0\nfor n in nums:')

    confirm.mockReturnValue(true)
    await user.click(startOver()!)
    expect(editor()).toHaveValue(STARTER)
    // The button has gone, so the cursor goes to the fresh editor.
    expect(editor()).toHaveFocus()
    expect(onCodeChange).toHaveBeenLastCalledWith(STARTER)
    expect(startOver()).not.toBeInTheDocument()
    expect(restoredNote()).not.toBeInTheDocument()
    first.unmount()

    // And it stays started over.
    renderRunner()
    expect(editor()).toHaveValue(STARTER)
  })

  it('only offers Start over once the code has changed', async () => {
    renderRunner({ draft: undefined })
    expect(startOver()).not.toBeInTheDocument()
    await userEvent.type(editor(), '!')
    expect(startOver()).toBeInTheDocument()
  })

  it('shows the new starter when the item has changed since the draft (a new rev)', () => {
    saveDraft(WHERE, 'written for the old version')
    renderRunner({ initialCode: 'count = 0', draft: { ...WHERE, rev: 2 } })
    expect(editor()).toHaveValue('count = 0')
    expect(restoredNote()).not.toBeInTheDocument()
  })

  it('works without drafts when the browser blocks storage', async () => {
    const blocked = () => {
      throw new DOMException('The operation is insecure.', 'SecurityError')
    }
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(blocked)
    const setItem = vi
      .spyOn(Storage.prototype, 'setItem')
      .mockImplementation(blocked)
    const user = userEvent.setup()
    const runner = fakeRunner()
    const first = renderRunner({ runner })
    await user.type(editor(), '\nprint(total)')
    await user.click(screen.getByRole('button', { name: 'Run' }))
    expect(runner.run.mock.calls[0]?.[0]).toBe('total = 0\nprint(total)')
    first.unmount()
    // It tried to save, and carried on when the browser said no.
    expect(setItem).toHaveBeenCalled()

    renderRunner()
    expect(editor()).toHaveValue(STARTER)
  })

  it('keeps nothing when it is given nowhere to keep it', async () => {
    const first = renderRunner({ draft: undefined })
    await userEvent.type(editor(), '\nfor n in nums:')
    first.unmount()
    expect(localStorage.length).toBe(0)
  })
})
