import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { fakeLab } from '../test/fakeContent.tsx'
import { ExerciseView } from './ExerciseView.tsx'

const TOPIC = 'csa.linux.shell'

function printed(
  checks: Record<string, boolean>,
  rev = 1,
  lab = `${TOPIC}/build-report`,
) {
  const list = Object.entries(checks).map(([id, passed]) => ({ id, passed }))
  return JSON.stringify({
    lab,
    rev,
    checker: '1',
    checked_at: '2026-11-09T18:00:00+00:00',
    passed: list.filter((c) => c.passed).length,
    total: list.length,
    checks: list,
  })
}

async function paste(text: string) {
  await userEvent.click(screen.getByLabelText("The checker's result"))
  await userEvent.paste(text)
  await userEvent.click(screen.getByRole('button', { name: 'Record result' }))
}

describe('a lab exercise', () => {
  it('says how to run it, names the checks, and waits for a result', () => {
    render(
      <ExerciseView
        exercise={fakeLab({ id: 'build-report', stage: 'build' })}
        topicId={TOPIC}
      />,
    )
    const commands = screen.getByText(/labcheck\.py start/)
    expect(commands.textContent).toContain(
      `tools/labcheck.py start ${TOPIC} build-report`,
    )
    expect(commands.textContent).toContain(`check ${TOPIC} build-report`)
    expect(commands.textContent).toContain(`stop ${TOPIC} build-report`)
    const checks = screen.getByRole('region', {
      name: 'What the checker looks for',
    })
    expect(within(checks).getAllByRole('listitem')).toHaveLength(2)
    expect(
      within(checks).getByText('A report folder exists.'),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Record result' })).toBeDisabled()
    // No code runner: the work happens in the container.
    expect(
      screen.queryByRole('button', { name: 'Check' }),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText(/Compare with a reference solution/),
    ).not.toBeInTheDocument()
  })

  it('records a passing result, ticks the checks and shows the reference solution', async () => {
    const onActivity = vi.fn()
    render(
      <ExerciseView
        exercise={fakeLab({ id: 'build-report', stage: 'build' })}
        topicId={TOPIC}
        onActivity={onActivity}
      />,
    )
    await paste(printed({ 'report-folder': true, 'failed-count': true }))
    expect(screen.getByText('All checks passed.')).toBeInTheDocument()
    expect(screen.getAllByText('(passed)')).toHaveLength(2)
    expect(
      screen.getByText('Compare with a reference solution'),
    ).toBeInTheDocument()
    expect(onActivity).toHaveBeenCalledWith({
      kind: 'lab',
      hintsUsed: 0,
      result: expect.objectContaining({
        lab: `${TOPIC}/build-report`,
        passed: 2,
        total: 2,
      }),
    })
  })

  it('records a partial result without giving the solution away', async () => {
    const onActivity = vi.fn()
    render(
      <ExerciseView
        exercise={fakeLab({ id: 'build-report', stage: 'build' })}
        topicId={TOPIC}
        onActivity={onActivity}
      />,
    )
    await paste(printed({ 'report-folder': true, 'failed-count': false }))
    expect(screen.getByText('1 of 2 checks passed.')).toBeInTheDocument()
    expect(screen.getByText('(failed)')).toBeInTheDocument()
    expect(
      screen.queryByText('Compare with a reference solution'),
    ).not.toBeInTheDocument()
    expect(onActivity).toHaveBeenCalledWith(
      expect.objectContaining({
        kind: 'lab',
        result: expect.objectContaining({ passed: 1, total: 2 }),
      }),
    )
  })

  it('refuses a result for another lab or revision, recording nothing', async () => {
    const onActivity = vi.fn()
    render(
      <ExerciseView
        exercise={fakeLab({ id: 'build-report', stage: 'build', rev: 2 })}
        topicId={TOPIC}
        onActivity={onActivity}
      />,
    )
    await paste(printed({ 'report-folder': true }, 2, `${TOPIC}/other-lab`))
    expect(screen.getByRole('alert')).toHaveTextContent(
      `That result is for another lab (${TOPIC}/other-lab).`,
    )
    await userEvent.clear(screen.getByLabelText("The checker's result"))
    await paste(printed({ 'report-folder': true }, 1))
    expect(screen.getByRole('alert')).toHaveTextContent(
      /revision 1 of this lab/,
    )
    await userEvent.clear(screen.getByLabelText("The checker's result"))
    await paste('not json')
    expect(screen.getByRole('alert')).toHaveTextContent(
      /isn't the checker's result/,
    )
    expect(onActivity).not.toHaveBeenCalled()
  })

  it('offers written hints where the stage allows them, and counts them', async () => {
    const onActivity = vi.fn()
    render(
      <ExerciseView
        exercise={fakeLab({
          id: 'fill-report',
          stage: 'fill_in',
          hints: ['Look at the third field.'],
        })}
        topicId={TOPIC}
        onActivity={onActivity}
      />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'Show a hint' }))
    expect(screen.getByText('Look at the third field.')).toBeInTheDocument()
    expect(onActivity).toHaveBeenCalledWith({ kind: 'hint', hintsUsed: 1 })
    await paste(
      printed(
        { 'report-folder': true, 'failed-count': true },
        1,
        `${TOPIC}/fill-report`,
      ),
    )
    expect(onActivity).toHaveBeenLastCalledWith(
      expect.objectContaining({ kind: 'lab', hintsUsed: 1 }),
    )
  })

  it('shows a worked-example lab as a walkthrough with its steps', () => {
    render(
      <ExerciseView
        exercise={fakeLab({
          id: 'example-report',
          stage: 'worked_example',
          solution: 'mkdir -p ~/report\ncd /var/log/shop\n',
          steps: [
            { label: 'Make the folder', lines: '1', note: 'With -p.' },
            { label: 'Go to the logs', lines: '2', note: 'cd there.' },
          ],
        })}
        topicId={TOPIC}
      />,
    )
    expect(screen.getByText('The walkthrough')).toBeInTheDocument()
    expect(
      screen.getByText(
        (_, node) =>
          node?.tagName === 'PRE' &&
          node.textContent === 'mkdir -p ~/report\ncd /var/log/shop\n',
      ),
    ).toBeInTheDocument()
    expect(screen.getByText('Make the folder')).toBeInTheDocument()
    expect(screen.getByText('(line 2)')).toBeInTheDocument()
  })
})
