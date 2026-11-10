import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import { fakeExercise } from '../test/fakeContent.tsx'
import {
  allPassed,
  fakeRunner,
  oneFailed,
  printed,
} from '../test/fakePython.ts'
import { setFakeRunner } from '../test/mockPython.ts'
import { askTutor } from '../tutor/hint.ts'
import { ExerciseView } from './ExerciseView.tsx'

vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock('./CodeEditor.tsx', () => import('../test/FakeCodeEditor.tsx'))
vi.mock('../tutor/hint.ts', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../tutor/hint.ts')>()),
  askTutor: vi.fn(),
}))

const check = () =>
  userEvent.click(screen.getByRole('button', { name: 'Check' }))

describe('ExerciseView', () => {
  it('shows a worked example to run, explained step by step', () => {
    setFakeRunner()
    render(
      <ExerciseView
        exercise={fakeExercise({
          id: 'example',
          stage: 'worked_example',
          solution: 'name = "Ada"\nprint(name)\n',
          steps: [
            { label: 'Store the name', lines: '1', note: 'A variable.' },
            { label: 'Show it', lines: '2-3', note: 'Print it.' },
          ],
        })}
      />,
    )
    expect(screen.getByLabelText('Python code')).toHaveValue(
      'name = "Ada"\nprint(name)\n',
    )
    expect(screen.getByText('Store the name')).toBeInTheDocument()
    expect(screen.getByText('(line 1)')).toBeInTheDocument()
    expect(screen.getByText('(lines 2–3)')).toBeInTheDocument()
    // Nothing to check: the learner studies and runs it.
    expect(screen.getByRole('button', { name: 'Run' })).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Check' }),
    ).not.toBeInTheDocument()
  })

  it('starts from the starter code and checks with the time limit', async () => {
    const runner = setFakeRunner(fakeRunner({ check: oneFailed('Says hi') }))
    render(
      <ExerciseView
        exercise={fakeExercise({
          id: 'fill',
          stage: 'fill_in',
          starter: 'print(...)',
          time_limit_ms: 2000,
        })}
      />,
    )
    expect(screen.getByLabelText('Python code')).toHaveValue('print(...)')
    await check()
    expect(runner.check).toHaveBeenCalledWith('print(...)', 'the tests', {
      timeLimitMs: 2000,
      packages: [],
    })
  })

  it('gives hints one at a time', async () => {
    setFakeRunner()
    render(
      <ExerciseView
        exercise={fakeExercise({
          id: 'write',
          stage: 'write',
          hints: ['First hint', 'Second hint'],
        })}
      />,
    )
    expect(screen.queryByText('First hint')).not.toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Show a hint' }))
    expect(screen.getByText('First hint')).toBeInTheDocument()
    expect(screen.queryByText('Second hint')).not.toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Show another hint' }),
    )
    expect(screen.getByText('Second hint')).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: /hint/ }),
    ).not.toBeInTheDocument()
  })

  it('offers no hints during a proof check, where the tutor is off', () => {
    setFakeRunner()
    render(
      <ExerciseView
        exercise={fakeExercise({
          id: 'build',
          stage: 'build',
          hints: ['A hint'],
        })}
      />,
    )
    expect(
      screen.queryByRole('button', { name: 'Show a hint' }),
    ).not.toBeInTheDocument()
  })

  it('shows the reference solution only after a pass', async () => {
    const runner = setFakeRunner(fakeRunner({ check: oneFailed('Says hi') }))
    render(
      <ExerciseView
        exercise={fakeExercise({
          id: 'write',
          stage: 'write',
          solution: 'print("the answer")',
        })}
      />,
    )
    await check()
    expect(await screen.findByText("The check didn't pass yet.")).toBeVisible()
    expect(screen.queryByText(/reference solution/)).not.toBeInTheDocument()

    runner.check.mockResolvedValue(allPassed('Says hi'))
    await check()
    expect(
      await screen.findByText('Compare with a reference solution'),
    ).toBeInTheDocument()
    expect(screen.getByText('print("the answer")')).toBeInTheDocument()
  })

  it('reports runs, hints and checks, so they can be saved', async () => {
    const runner = setFakeRunner(
      fakeRunner({ run: printed('hi\n'), check: oneFailed('Says hi') }),
    )
    const onActivity = vi.fn()
    render(
      <ExerciseView
        exercise={fakeExercise({
          id: 'write',
          stage: 'write',
          starter: 'print("hi")',
          hints: ['A hint'],
        })}
        onActivity={onActivity}
      />,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Run' }))
    await userEvent.click(screen.getByRole('button', { name: 'Show a hint' }))
    await check()

    await vi.waitFor(() => expect(onActivity).toHaveBeenCalledTimes(3))
    expect(onActivity.mock.calls.map(([activity]) => activity)).toEqual([
      { kind: 'run', code: 'print("hi")', outcome: printed('hi\n') },
      { kind: 'hint', hintsUsed: 1 },
      {
        kind: 'check',
        code: 'print("hi")',
        outcome: oneFailed('Says hi'),
        hintsUsed: 1,
      },
    ])
    expect(runner.run).toHaveBeenCalledTimes(1)
  })
})

describe('the tutor in an exercise', () => {
  function renderInPractice(onActivity = vi.fn()) {
    render(
      <AuthProvider auth={fakeAuth(fakeUser())}>
        <MemoryRouter>
          <ExerciseView
            exercise={fakeExercise({
              id: 'write',
              stage: 'write',
              hints: ['A written hint'],
            })}
            onActivity={onActivity}
            allowTutor
            topicId="py.values-and-types"
          />
        </MemoryRouter>
      </AuthProvider>,
    )
    return onActivity
  }

  it('sees the code as typed and the latest Check, and its hints count as hints', async () => {
    setFakeRunner(fakeRunner({ check: oneFailed('Says hi') }))
    vi.mocked(askTutor).mockResolvedValue({
      status: 'hinted',
      hint: {
        text: 'What did the check expect?',
        level: 'nudge',
        replaced: false,
      },
      ai_call_id: 'call-1',
      model: 'claude-haiku-5-5',
    })
    const onActivity = renderInPractice()

    await userEvent.type(screen.getByLabelText('Python code'), 'print(hi)')
    await check()
    await userEvent.click(screen.getByRole('button', { name: 'Ask the tutor' }))

    expect(askTutor).toHaveBeenCalledWith(
      expect.objectContaining({
        topicId: 'py.values-and-types',
        itemId: 'write',
        code: 'print(hi)',
        check: oneFailed('Says hi'),
        earlier: [],
      }),
    )
    const tutor = screen.getByRole('region', { name: 'Tutor' })
    expect(
      within(tutor).getByText('What did the check expect?'),
    ).toBeInTheDocument()
    expect(onActivity).toHaveBeenLastCalledWith({
      kind: 'tutor',
      hintsUsed: 1,
      given: {
        hint: {
          text: 'What did the check expect?',
          level: 'nudge',
          replaced: false,
        },
        count: 1,
        question: '',
        aiCallId: 'call-1',
        model: 'claude-haiku-5-5',
      },
    })

    // A written hint on top makes two, and the next Check says so.
    await userEvent.click(screen.getByRole('button', { name: 'Show a hint' }))
    await check()
    expect(onActivity).toHaveBeenLastCalledWith(
      expect.objectContaining({ kind: 'check', hintsUsed: 2 }),
    )
  })

  it('is off unless the item allows it, and never in a proof check', () => {
    setFakeRunner()
    render(
      <ExerciseView exercise={fakeExercise({ id: 'write', stage: 'write' })} />,
    )
    expect(
      screen.queryByRole('region', { name: 'Tutor' }),
    ).not.toBeInTheDocument()
    render(
      <ExerciseView
        exercise={fakeExercise({ id: 'build', stage: 'build' })}
        allowTutor
      />,
    )
    expect(
      screen.queryByRole('region', { name: 'Tutor' }),
    ).not.toBeInTheDocument()
  })
})
