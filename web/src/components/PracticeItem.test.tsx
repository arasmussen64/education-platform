import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider.tsx'
import { EventLogContext } from '../events/eventLogContext.ts'
import { fakeAuth } from '../test/fakeAuth.ts'
import { fakeContent, PARSONS } from '../test/fakeContent.tsx'
import { recordingEventLog } from '../test/fakeEvents.ts'
import { PracticeItem } from './PracticeItem.tsx'

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
