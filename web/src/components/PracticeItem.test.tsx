import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { EventLogContext } from '../events/eventLogContext.ts'
import { fakeAuth } from '../test/fakeAuth.ts'
import { fakeContent, fakeLab, PARSONS } from '../test/fakeContent.tsx'
import { recordingEventLog } from '../test/fakeEvents.ts'
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
