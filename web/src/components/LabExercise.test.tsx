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

const RUN = 'python -m uv run python tools/labcheck.py'

describe('a lab exercise', () => {
  it('says how to run it, names the checks, and waits for a result', () => {
    render(
      <ExerciseView
        exercise={fakeLab({ id: 'build-report', stage: 'build' })}
        topicId={TOPIC}
      />,
    )
    // One command per step, each with this lab's name filled in.
    for (const verb of ['start', 'shell', 'check', 'stop', 'start --fresh']) {
      expect(
        screen.getByText(`${RUN} ${verb} ${TOPIC} build-report`),
      ).toBeInTheDocument()
    }
    // The shell is the checker's own command now. A docker line pasted
    // into Git Bash is what used to fail.
    expect(document.body.textContent).not.toContain('docker exec')
    // Running start again is safe, and --fresh is what resets.
    expect(
      screen.getByText(/Running this again keeps your work/),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/To throw your work away and begin the lab again/),
    ).toBeInTheDocument()
    // And a way to find and stop a forgotten lab.
    expect(
      screen.getByText(
        (_, node) =>
          node?.tagName === 'PRE' &&
          node.textContent === `${RUN} status\n${RUN} stop --all`,
      ),
    ).toBeInTheDocument()
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

  it('says what a privileged lab may touch, and how to stop it', () => {
    // exercise.yaml's `lab: { init: systemd }`, as the loader hands it on.
    const booted = {
      ...fakeLab({ id: 'build-report', stage: 'build' }),
      lab: { init: 'systemd' },
    }
    render(<ExerciseView exercise={booted} topicId={TOPIC} />)
    const note = screen.getByText(/This lab's container is privileged/)
    expect(note).toHaveTextContent(
      /reach the disks and settings of the machine Docker runs on, not only its own files/,
    )
    expect(note).toHaveTextContent(
      /Stop it with the stop command, not from the Docker Desktop window/,
    )
  })

  it('says a lab that is not privileged is sealed off', () => {
    render(
      <ExerciseView
        exercise={fakeLab({ id: 'build-report', stage: 'build' })}
        topicId={TOPIC}
      />,
    )
    expect(
      screen.getByText(/This lab's container is an ordinary one/),
    ).toHaveTextContent(/can change files on the rest of your computer/)
    expect(screen.queryByText(/privileged/)).not.toBeInTheDocument()
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

  it("keeps a debug lab's checks back until a result is in", async () => {
    render(
      <ExerciseView
        exercise={fakeLab({ id: 'build-report', stage: 'debug' })}
        topicId={TOPIC}
      />,
    )
    const checks = screen.getByRole('region', {
      name: 'What the checker looks for',
    })
    // Before a try: how many there are, but not what they look for.
    expect(within(checks).queryAllByRole('listitem')).toHaveLength(0)
    expect(
      within(checks).queryByText('A report folder exists.'),
    ).not.toBeInTheDocument()
    expect(within(checks).getByText(/^2 checks\. They/)).toBeInTheDocument()
    // After one, the list, with its ticks.
    await paste(printed({ 'report-folder': true, 'failed-count': false }))
    expect(within(checks).getAllByRole('listitem')).toHaveLength(2)
    expect(
      within(checks).getByText('A report folder exists.'),
    ).toBeInTheDocument()
    expect(screen.getByText('1 of 2 checks passed.')).toBeInTheDocument()
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

  it("refuses a result that does not name exactly this lab's checks", async () => {
    const onActivity = vi.fn()
    render(
      <ExerciseView
        exercise={fakeLab({ id: 'build-report', stage: 'build' })}
        topicId={TOPIC}
        onActivity={onActivity}
      />,
    )
    // One made-up check that passed used to read as "All checks passed."
    await paste(printed({ a: true }))
    expect(screen.getByRole('alert')).toHaveTextContent(
      /doesn't list the same checks as this lab has now/,
    )
    // A result from before a check was renamed: stale, so run check again.
    await userEvent.clear(screen.getByLabelText("The checker's result"))
    await paste(printed({ 'report-folder': true, 'failures-counted': true }))
    expect(screen.getByRole('alert')).toHaveTextContent(
      /run the check command again and paste the new line/,
    )
    // Only some of the checks, all passing, is not the lab passing.
    await userEvent.clear(screen.getByLabelText("The checker's result"))
    await paste(printed({ 'report-folder': true }))
    expect(screen.getByRole('alert')).toHaveTextContent(
      /doesn't list the same checks/,
    )
    expect(screen.queryByText('All checks passed.')).not.toBeInTheDocument()
    expect(screen.queryByText('(passed)')).not.toBeInTheDocument()
    expect(
      screen.queryByText('Compare with a reference solution'),
    ).not.toBeInTheDocument()
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
