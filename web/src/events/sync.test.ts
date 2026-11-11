import { describe, expect, it, vi } from 'vitest'
import { eventRow, fakeEventsClient } from '../test/fakeEvents.ts'
import { createOutbox } from './outbox.ts'
import {
  RETRY_REFUSED_AFTER_MS,
  retryRefused,
  type SendResult,
  syncOutbox,
} from './sync.ts'
import type { EventRow } from './types.ts'

const ADA = '11111111-1111-1111-1111-111111111111'
const BOB = '33333333-3333-3333-3333-333333333333'

const NOON = Date.parse('2026-11-10T12:00:00.000Z')
/** Long enough after NOON for a refused event to be tried again. */
const NEXT_DAY = NOON + RETRY_REFUSED_AFTER_MS + 1000
const REFUSED: SendResult = {
  ok: false,
  retryLater: false,
  message: '400 23514: violates check constraint',
}
const OFFLINE: SendResult = {
  ok: false,
  retryLater: true,
  message: '0 : TypeError: Failed to fetch',
}

/**
 * A fake server that refuses the events with these IDs and stores the rest.
 * `stored` lists what it has, in order.
 */
function pickyServer(refusedIds: string[]) {
  const stored: string[] = []
  const send = vi.fn(async (events: EventRow[]): Promise<SendResult> => {
    if (events.some((event) => refusedIds.includes(event.id))) return REFUSED
    stored.push(...events.map((event) => event.id))
    return { ok: true }
  })
  return { send, stored }
}

const refusedIds = (outbox: ReturnType<typeof createOutbox>, userId = ADA) =>
  outbox.refused(userId).map(({ event }) => event.id)

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
    expect(refusedIds(outbox)).toEqual(['bad'])
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

describe('retryRefused', () => {
  it('sends a refused event again later, and forgets it once the server accepts it', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const outbox = createOutbox()
    outbox.add(eventRow({ id: 'placement-answer' }))
    // The app is ahead of the database: the server refuses the event.
    const early = pickyServer(['placement-answer'])
    await syncOutbox(outbox, early, ADA, NOON)
    expect(refusedIds(outbox)).toEqual(['placement-answer'])

    // The database has caught up by the next day.
    const server = pickyServer([])
    expect(await retryRefused(outbox, server, ADA, NEXT_DAY)).toBe('done')
    expect(server.stored).toEqual(['placement-answer'])
    expect(outbox.refused(ADA)).toEqual([])
  })

  it('keeps an event that is refused again, with the new reason and time and the attempt counted', async () => {
    const outbox = createOutbox()
    const bad = eventRow({ id: 'bad' })
    outbox.refuse(bad, '400 23514: violates check constraint', NOON)
    const client = fakeEventsClient({
      ok: false,
      retryLater: false,
      message: '413 : too large',
    })

    expect(await retryRefused(outbox, client, ADA, NEXT_DAY)).toBe('done')
    expect(client.send).toHaveBeenCalledTimes(1)
    expect(outbox.refused(ADA)).toEqual([
      {
        event: bad,
        reason: '413 : too large',
        at: new Date(NEXT_DAY).toISOString(),
        attempts: 2,
      },
    ])
  })

  it('tries nothing within 12 hours of the last attempt', async () => {
    const outbox = createOutbox()
    outbox.refuse(eventRow({ id: 'bad' }), REFUSED.message, NOON)
    const client = fakeEventsClient()

    const justUnder = NOON + RETRY_REFUSED_AFTER_MS - 1000
    expect(await retryRefused(outbox, client, ADA, justUnder)).toBe('done')
    expect(client.send).not.toHaveBeenCalled()
    expect(outbox.refused(ADA)[0]).toMatchObject({ attempts: 1 })

    // A second refusal starts the 12 hours again.
    client.send.mockResolvedValue(REFUSED)
    await retryRefused(outbox, client, ADA, NEXT_DAY)
    client.send.mockClear()
    await retryRefused(outbox, client, ADA, NEXT_DAY + 60 * 60 * 1000)
    expect(client.send).not.toHaveBeenCalled()
  })

  it("leaves another learner's refused events alone", async () => {
    const outbox = createOutbox()
    outbox.refuse(eventRow({ id: 'ada' }), REFUSED.message, NOON)
    outbox.refuse(eventRow({ id: 'bob', user_id: BOB }), REFUSED.message, NOON)
    const bobsBefore = outbox.refused(BOB)
    const server = pickyServer([])

    await retryRefused(outbox, server, ADA, NEXT_DAY)
    expect(server.stored).toEqual(['ada'])
    expect(outbox.refused(BOB)).toEqual(bobsBefore)
  })

  it('sends them one at a time, so one refused again never holds up the others', async () => {
    const outbox = createOutbox()
    for (const id of ['good-1', 'bad', 'good-2']) {
      outbox.refuse(eventRow({ id }), REFUSED.message, NOON)
    }
    const server = pickyServer(['bad'])

    expect(await retryRefused(outbox, server, ADA, NEXT_DAY)).toBe('done')
    expect(server.send.mock.calls.map(([batch]) => batch.length)).toEqual([
      1, 1, 1,
    ])
    expect(server.stored).toEqual(['good-1', 'good-2'])
    expect(refusedIds(outbox)).toEqual(['bad'])
  })

  it('stops at a passing problem and leaves the rest as they were', async () => {
    const outbox = createOutbox()
    for (const id of ['first', 'second']) {
      outbox.refuse(eventRow({ id }), REFUSED.message, NOON)
    }
    const before = outbox.refused(ADA)
    const client = fakeEventsClient(OFFLINE)

    expect(await retryRefused(outbox, client, ADA, NEXT_DAY)).toBe(
      'retry-later',
    )
    expect(client.send).toHaveBeenCalledTimes(1)
    // No attempt counted and no time moved: they're due again straight away.
    expect(outbox.refused(ADA)).toEqual(before)
  })

  it('tries an event whose last attempt time cannot be read', async () => {
    const outbox = createOutbox()
    localStorage.setItem(
      'learner-events-rejected-v1',
      JSON.stringify([{ event: eventRow({ id: 'no-time' }), reason: '400' }]),
    )
    const server = pickyServer([])

    await retryRefused(outbox, server, ADA, NOON)
    expect(server.stored).toEqual(['no-time'])
  })

  it('tries an event whose last attempt is dated far in the future', async () => {
    // The device's clock was a year ahead when the event was refused, and
    // has been put right since. Waiting for that date would take a year.
    const outbox = createOutbox()
    const aYearAhead = NOON + 365 * 24 * 60 * 60 * 1000
    outbox.refuse(eventRow({ id: 'wrong-clock' }), REFUSED.message, aYearAhead)
    const server = pickyServer([])

    await retryRefused(outbox, server, ADA, NOON)
    expect(server.stored).toEqual(['wrong-clock'])
  })

  it('sends an event that storage holds twice only once, and waits 12 hours after it is refused again', async () => {
    // Two copies of one event, as two tabs could leave before retries
    // existed.
    const twice = eventRow({ id: 'twice' })
    const old = { event: twice, reason: '400', at: '2026-11-09T08:00:00.000Z' }
    localStorage.setItem(
      'learner-events-rejected-v1',
      JSON.stringify([old, old]),
    )
    const outbox = createOutbox()
    const client = fakeEventsClient(REFUSED)

    await retryRefused(outbox, client, ADA, NOON)
    expect(client.send).toHaveBeenCalledTimes(1)
    expect(outbox.refused(ADA)).toEqual([
      expect.objectContaining({ event: twice, attempts: 2 }),
    ])

    // An hour later, on the next save: nothing is due.
    client.send.mockClear()
    await retryRefused(outbox, client, ADA, NOON + 60 * 60 * 1000)
    expect(client.send).not.toHaveBeenCalled()
  })

  it('stops as soon as the learner is no longer the one signed in', async () => {
    const outbox = createOutbox()
    for (const id of ['first', 'second', 'third']) {
      outbox.refuse(eventRow({ id }), REFUSED.message, NOON)
    }
    // The sign-in changes while the first event is on its way.
    let signedIn = true
    const client = fakeEventsClient(REFUSED)
    client.send.mockImplementation(() => {
      signedIn = false
      return Promise.resolve(REFUSED)
    })

    expect(
      await retryRefused(outbox, client, ADA, NEXT_DAY, () => signedIn),
    ).toBe('retry-later')
    expect(client.send).toHaveBeenCalledTimes(1)
    // The other two weren't sent, so they're still due next time.
    expect(outbox.refused(ADA).map(({ attempts }) => attempts)).toEqual([
      2, 1, 1,
    ])
  })
})
