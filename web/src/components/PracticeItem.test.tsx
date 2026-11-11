import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { EventLogContext } from '../events/eventLogContext.ts'
import type { CheckOutcome } from '../python/runner.ts'
import { fakeAuth } from '../test/fakeAuth.ts'
import { fakeContent, fakeLab, PARSONS } from '../test/fakeContent.tsx'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { allPassed, oneFailed, report } from '../test/fakePython.ts'
import { PracticeItem } from './PracticeItem.tsx'

// Worked examples hold a code runner: use the fake Python and plain-textbox
// editor instead of Pyodide and CodeMirror.
vi.mock('../python/runner.ts', () =>
  import('../test/mockPython.ts').then((module) => module.mockRunnerModule()),
)
vi.mock('./CodeEditor.tsx', () => import('../test/FakeCodeEditor.tsx'))

describe('a Parsons problem as a practice item', () => {
  it('has its own heading, and saves the program as an answer', async () => {
    const base = fakeContent()
    const content = {
      ...base,
      recall: { ...base.recall, [PARSONS.id]: PARSONS },
    }
    const { log, events } = recordingEventLog()
    render(
      <AuthProvider auth={fakeAuth(null)}>
        <EventLogContext value={log}>
          <MemoryRouter>
            <PracticeItem
              itemId={PARSONS.id}
              content={content}
              context="practice"
              position="Practice 2 of 6"
            />
          </MemoryRouter>
        </EventLogContext>
      </AuthProvider>,
    )
    expect(
      screen.getByRole('heading', { name: 'Put the lines in order' }),
    ).toBeInTheDocument()
    for (const line of PARSONS.lines) {
      await userEvent.click(
        screen.getByRole('button', { name: `Add: ${line.trim()}` }),
      )
    }
    await userEvent.click(screen.getByRole('button', { name: 'Check' }))
    expect(screen.getByText('Correct!')).toBeInTheDocument()
    expect(events).toEqual([
      expect.objectContaining({
        type: 'answer',
        topic_id: content.topic.id,
        item_id: PARSONS.id,
        item_rev: 1,
        context: 'practice',
        correct: true,
        data: { program: PARSONS.lines.join('\n') },
      }),
    ])
  })
})

describe('a lab as a proof item', () => {
  it("records the checker's result as a code check, marked as a lab", async () => {
    const base = fakeContent()
    const lab = fakeLab({ id: 'build-report', stage: 'build' })
    const content = {
      ...base,
      topic: { ...base.topic, prove: { ...base.topic.prove, build: lab.id } },
      exercises: { ...base.exercises, [lab.id]: lab },
    }
    const { log, events } = recordingEventLog()
    const onCheck = vi.fn()
    render(
      <AuthProvider auth={fakeAuth(null)}>
        <EventLogContext value={log}>
          <MemoryRouter>
            <PracticeItem
              itemId={lab.id}
              content={content}
              context="prove"
              onCheck={onCheck}
            />
          </MemoryRouter>
        </EventLogContext>
      </AuthProvider>,
    )
    expect(
      screen.getByRole('heading', { name: 'Build: A report from the logs' }),
    ).toBeInTheDocument()
    await userEvent.click(screen.getByLabelText("The checker's result"))
    await userEvent.paste(
      JSON.stringify({
        lab: `${content.topic.id}/${lab.id}`,
        rev: 1,
        checker: '1',
        checked_at: '2026-11-09T18:00:00+00:00',
        passed: 1,
        total: 2,
        checks: [
          { id: 'report-folder', passed: true },
          { id: 'failed-count', passed: false },
        ],
      }),
    )
    await userEvent.click(screen.getByRole('button', { name: 'Record result' }))
    expect(onCheck).toHaveBeenCalledWith(false)
    expect(events).toEqual([
      expect.objectContaining({
        type: 'code_check',
        topic_id: content.topic.id,
        item_id: lab.id,
        context: 'prove',
        correct: false,
        hints_used: 0,
        data: {
          runtime: 'lab',
          checker: '1',
          checked_at: '2026-11-09T18:00:00+00:00',
          passed: 1,
          total: 2,
          failing: ['failed-count'],
        },
      }),
    ])
  })
})

describe('a Check of an exercise', () => {
  /** Renders the fake topic's "write" exercise in a review, with spies. */
  async function renderExercise(...outcomes: CheckOutcome[]) {
    const { setFakeRunner } = await import('../test/mockPython.ts')
    const runner = setFakeRunner()
    for (const outcome of outcomes) runner.check.mockResolvedValueOnce(outcome)
    const { log, events } = recordingEventLog()
    const onCheck = vi.fn()
    const onGraded = vi.fn()
    render(
      <AuthProvider auth={fakeAuth(null)}>
        <EventLogContext value={log}>
          <MemoryRouter>
            <PracticeItem
              itemId="write-hello"
              content={fakeContent()}
              context="review"
              onCheck={onCheck}
              onGraded={onGraded}
            />
          </MemoryRouter>
        </EventLogContext>
      </AuthProvider>,
    )
    const check = () =>
      userEvent.click(screen.getByRole('button', { name: 'Check' }))
    return { events, onCheck, onGraded, check }
  }

  const NOT_RUN = /couldn't run, so it doesn't count/

  it.each<[string, CheckOutcome]>([
    [
      "Python couldn't start",
      {
        kind: 'failed',
        message: 'Failed to fetch dynamically imported module',
      },
    ],
    [
      'the worker crashed',
      { kind: 'failed', message: 'Python stopped unexpectedly.' },
    ],
    [
      "the exercise's tests couldn't be loaded",
      report({
        status: 'error',
        message:
          "The tests couldn't be loaded. This is a problem with the exercise. ImportError: x",
      }),
    ],
  ])(
    "saves a Check that couldn't run ungraded, and counts it nowhere: %s",
    async (_why, outcome) => {
      const { events, onCheck, onGraded, check } = await renderExercise(outcome)
      await check()

      await vi.waitFor(() => expect(events).toHaveLength(1))
      // Saved, so the history shows what happened, but with no verdict and
      // no time: the time so far goes to the next real attempt.
      expect(events).toEqual([
        expect.objectContaining({
          type: 'code_check',
          item_id: 'write-hello',
          context: 'review',
          correct: undefined,
          duration_ms: null,
        }),
      ])
      expect(onCheck).not.toHaveBeenCalled()
      expect(onGraded).not.toHaveBeenCalled()
      // The learner is told, so they know to press Check again.
      expect(screen.getByText(NOT_RUN)).toBeInTheDocument()
    },
  )

  it('lets the learner try again, and the next Check that runs counts', async () => {
    const { events, onGraded, check } = await renderExercise(
      { kind: 'failed', message: 'Python stopped unexpectedly.' },
      allPassed('Greets'),
    )
    await check()
    expect(await screen.findByText(NOT_RUN)).toBeInTheDocument()

    await check()
    await vi.waitFor(() => expect(onGraded).toHaveBeenCalledWith(true))
    expect(onGraded).toHaveBeenCalledTimes(1)
    expect(screen.queryByText(NOT_RUN)).not.toBeInTheDocument()
    expect(events.map((event) => event.correct)).toEqual([undefined, true])
  })

  it.each<[string, CheckOutcome]>([
    ['a test failed', oneFailed('Greets')],
    ['the code ran past the time limit', { kind: 'timeout' }],
  ])('counts a Check that ran as wrong when %s', async (_why, outcome) => {
    const { events, onCheck, onGraded, check } = await renderExercise(outcome)
    await check()

    await vi.waitFor(() => expect(onGraded).toHaveBeenCalledWith(false))
    expect(onCheck).toHaveBeenCalledWith(false)
    expect(events).toEqual([
      expect.objectContaining({ type: 'code_check', correct: false }),
    ])
    expect(screen.queryByText(NOT_RUN)).not.toBeInTheDocument()
  })
})

describe('a worked example, stepped through (ADR-0022)', () => {
  it('saves the Step through as a run, marked as stepped', async () => {
    const { setFakeRunner } = await import('../test/mockPython.ts')
    setFakeRunner()
    const content = fakeContent()
    const { log, events } = recordingEventLog()
    render(
      <AuthProvider auth={fakeAuth(null)}>
        <EventLogContext value={log}>
          <MemoryRouter>
            <PracticeItem
              itemId="example-hello"
              content={content}
              context="practice"
            />
          </MemoryRouter>
        </EventLogContext>
      </AuthProvider>,
    )
    await userEvent.click(screen.getByRole('button', { name: 'Step through' }))
    expect(await screen.findByText('Step 1 of 4')).toBeInTheDocument()
    expect(events).toEqual([
      expect.objectContaining({
        type: 'code_run',
        topic_id: content.topic.id,
        item_id: 'example-hello',
        context: 'practice',
        data: expect.objectContaining({
          outcome: 'done',
          stepped: true,
          steps: 4,
          truncated: false,
        }),
      }),
    ])
  })
})
