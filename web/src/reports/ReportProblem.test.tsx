import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { fakeAuth, fakeUser } from '../test/fakeAuth.ts'
import type { SendReport } from './report.ts'
import { ReportProblem } from './ReportProblem.tsx'

const ABOUT = { topicId: 'py.variables', itemId: 'fill-swap', itemRev: 2 }

function renderReport(send: SendReport, { signedIn = true } = {}) {
  render(
    <AuthProvider auth={fakeAuth(signedIn ? fakeUser() : null)}>
      <ReportProblem about={ABOUT} send={send} />
    </AuthProvider>,
  )
}

const openIt = () =>
  userEvent.click(screen.getByRole('button', { name: 'Report a problem' }))

describe('ReportProblem', () => {
  it('opens a box, sends the report about this item, and says thanks', async () => {
    const send = vi.fn<SendReport>(() => Promise.resolve('sent'))
    renderReport(send)
    await openIt()
    const box = screen.getByLabelText("What's wrong here?")
    // Nothing to send yet.
    expect(screen.getByRole('button', { name: 'Send report' })).toBeDisabled()
    await userEvent.type(box, 'The hint mentions a line that is not there.')
    await userEvent.click(screen.getByRole('button', { name: 'Send report' }))

    expect(send).toHaveBeenCalledWith(
      fakeUser().id,
      ABOUT,
      'The hint mentions a line that is not there.',
    )
    expect(
      screen.getByText('Thanks. Your report is saved.'),
    ).toBeInTheDocument()
    expect(box).toHaveValue('')
    await userEvent.click(screen.getByRole('button', { name: 'Close' }))
    expect(
      screen.getByRole('button', { name: 'Report a problem' }),
    ).toBeInTheDocument()
  })

  it('keeps the text and says so when sending fails', async () => {
    const send = vi.fn<SendReport>(() => Promise.resolve('failed'))
    renderReport(send)
    await openIt()
    await userEvent.type(screen.getByLabelText("What's wrong here?"), 'Typo')
    await userEvent.click(screen.getByRole('button', { name: 'Send report' }))
    expect(screen.getByText(/couldn't be sent/)).toBeInTheDocument()
    expect(screen.getByLabelText("What's wrong here?")).toHaveValue('Typo')
    expect(screen.getByRole('button', { name: 'Send report' })).toBeEnabled()
  })

  it('can be cancelled, and is not there for signed-out visitors', async () => {
    renderReport(vi.fn<SendReport>())
    await openIt()
    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(
      screen.queryByLabelText("What's wrong here?"),
    ).not.toBeInTheDocument()

    render(
      <AuthProvider auth={fakeAuth(null)}>
        <ReportProblem about={ABOUT} />
      </AuthProvider>,
    )
    expect(
      screen.getAllByRole('button', { name: 'Report a problem' }),
    ).toHaveLength(1)
  })
})
