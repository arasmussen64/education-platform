import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'
import type { EventLogStatus } from '../events/eventLog.ts'
import { EventLogContext } from '../events/eventLogContext.ts'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { SaveStatus } from './SaveStatus.tsx'

function renderStatus(status: EventLogStatus) {
  const log = { ...recordingEventLog().log, getStatus: () => status }
  render(
    <EventLogContext value={log}>
      <MemoryRouter>
        <SaveStatus />
      </MemoryRouter>
    </EventLogContext>,
  )
  return screen.getByRole('status')
}

const SAVED = { pending: 0, syncing: false, refused: 0, lostIfClosed: 0 }
const PAGE_CLOSES = /this device can't keep it if the page closes/

describe('the save status', () => {
  it('says nothing when everything is saved', () => {
    expect(renderStatus(SAVED)).toBeEmptyDOMElement()
  })

  it('says when work is waiting after a failed save', () => {
    expect(renderStatus({ ...SAVED, pending: 2 })).toHaveTextContent(
      'Not saved yet',
    )
    expect(screen.queryByText(PAGE_CLOSES)).not.toBeInTheDocument()
  })

  it('says nothing while saving, which normally takes a moment', () => {
    expect(
      renderStatus({ ...SAVED, pending: 1, lostIfClosed: 1, syncing: true }),
    ).toBeEmptyDOMElement()
  })

  it("warns that closing the page loses work this device couldn't keep", () => {
    const status = renderStatus({ ...SAVED, pending: 3, lostIfClosed: 1 })
    expect(status).toHaveTextContent(
      "Not saved yet: this device can't keep it if the page closes",
    )
    // One line, not two: the warning stands in for "Not saved yet".
    expect(screen.getAllByText(/Not saved yet/)).toHaveLength(1)
  })

  it('warns too when the only work this page holds was refused', () => {
    renderStatus({ ...SAVED, refused: 1, lostIfClosed: 1 })
    expect(screen.getByText(PAGE_CLOSES)).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /couldn't be saved yet/ }),
    ).toHaveAttribute('href', '/account')
  })

  it('reads a status with no count of work only this page holds as none', () => {
    // As test fakes and older code give it.
    renderStatus({ pending: 1, syncing: false, refused: 0 })
    expect(screen.getByText('Not saved yet')).toBeInTheDocument()
    expect(screen.queryByText(PAGE_CLOSES)).not.toBeInTheDocument()
  })
})
