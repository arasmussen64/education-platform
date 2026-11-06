import { describe, expect, it, vi } from 'vitest'
import { eventRow, fakeEventsClient } from '../test/fakeEvents.ts'
import { createOutbox } from './outbox.ts'
import { type SendResult, syncOutbox } from './sync.ts'
import type { EventRow } from './types.ts'

const ADA = '11111111-1111-1111-1111-111111111111'
const BOB = '33333333-3333-3333-3333-333333333333'

describe('syncOutbox', () => {
  it('sends events in batches and forgets each batch once the server has it', async () => {
    const outbox = createOutbox()
    for (let index = 0; index < 120; index++) {
      outbox.add(eventRow({ id: `e${index}` }))
    }
    const client = fakeEventsClient()

    expect(await syncOutbox(outbox, client, ADA)).toBe('done')
    expect(client.send.mock.calls.map(([batch]) => batch.length)).toEqual([
      50, 50, 20,
    ])
    expect(outbox.count(ADA)).toBe(0)
  })

  it("only sends the given learner's events", async () => {
    const outbox = createOutbox()
    outbox.add(eventRow({ id: 'ada' }))
    outbox.add(eventRow({ id: 'bob', user_id: BOB }))
    const client = fakeEventsClient()

    await syncOutbox(outbox, client, ADA)
    expect(client.send).toHaveBeenCalledWith([
      expect.objectContaining({ id: 'ada' }),
    ])
    expect(outbox.count(BOB)).toBe(1)
  })

  it('keeps everything when the connection fails, to try again later', async () => {
    const outbox = createOutbox()
    outbox.add(eventRow())
    const client = fakeEventsClient({
      ok: false,
      retryLater: true,
      message: '0 : TypeError: Failed to fetch',
    })

    expect(await syncOutbox(outbox, client, ADA)).toBe('retry-later')
    expect(outbox.count(ADA)).toBe(1)
  })

  it('sets aside an event the server refuses, and still sends the rest', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const outbox = createOutbox()
    for (const id of ['good-1', 'bad', 'good-2']) outbox.add(eventRow({ id }))
    const stored: string[] = []
    const client = {
      send: vi.fn(async (events: EventRow[]): Promise<SendResult> => {
        if (events.some((event) => event.id === 'bad')) {
          return { ok: false, retryLater: false, message: '400 23514: bad' }
        }
        stored.push(...events.map((event) => event.id))
        return { ok: true }
      }),
    }

    expect(await syncOutbox(outbox, client, ADA)).toBe('done')
    expect(stored).toEqual(['good-1', 'good-2'])
    expect(outbox.count(ADA)).toBe(0)
    expect(outbox.rejected().map((rejected) => rejected.event.id)).toEqual([
      'bad',
    ])
  })

  it("stops, rather than sending forever, if the outbox can't forget sent events", async () => {
    const outbox = createOutbox()
    outbox.add(eventRow())
    // As if storage were failing: nothing ever gets removed.
    vi.spyOn(outbox, 'remove').mockImplementation(() => {})
    const client = fakeEventsClient()

    expect(await syncOutbox(outbox, client, ADA)).toBe('done')
    expect(client.send).toHaveBeenCalledTimes(1)
  })
})
