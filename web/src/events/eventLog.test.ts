import { afterEach, describe, expect, it, vi } from 'vitest'
import { fakeEventsClient } from '../test/fakeEvents.ts'
import { createEventLog, FIRST_RETRY_MS, SESSION_IDLE_MS } from './eventLog.ts'
import { createOutbox } from './outbox.ts'
import { RETRY_REFUSED_AFTER_MS } from './sync.ts'
import type { NewEvent } from './types.ts'

const ADA = '11111111-1111-1111-1111-111111111111'
const BOB = '33333333-3333-3333-3333-333333333333'

const ANSWER: NewEvent = {
  type: 'answer',
  topic_id: 'py.variables',
  item_id: 'mcq-1',
  item_rev: 2,
  context: 'practice',
  correct: true,
  duration_ms: 1234.4,
  data: { choice: 0 },
}

const OFFLINE = {
  ok: false,
  retryLater: true,
  message: '0 : TypeError: Failed to fetch',
} as const

/** What the server says to an event its database isn't ready for. */
const REFUSED = {
  ok: false,
  retryLater: false,
  message: '400 23514: violates check constraint',
} as const

/** An event log with a fake server, clock and IDs (id-1, id-2, ...). */
function setup(client = fakeEventsClient()) {
  let time = Date.parse('2026-11-06T12:00:00.000Z')
  let lastId = 0
  const outbox = createOutbox()
  const log = createEventLog({
    outbox,
    client: () => client,
    contentBuild: 'abc123',
    now: () => time,
    newId: () => `id-${++lastId}`,
  })
  return {
    log,
    outbox,
    client,
    /** Moves the fake clock forward. */
    wait(ms: number) {
      time += ms
    },
  }
}

afterEach(() => {
  vi.useRealTimers()
})

describe('the event log', () => {
  it('turns what happened into a complete row for the signed-in learner', async () => {
    const { log, client } = setup()
    log.setUser(ADA)
    log.record(ANSWER)

    await vi.waitFor(() => expect(client.send).toHaveBeenCalled())
    expect(client.send.mock.calls[0]?.[0]).toEqual([
      {
        id: 'id-2',
        user_id: ADA,
        type: 'answer',
        topic_id: 'py.variables',
        item_id: 'mcq-1',
        context: 'practice',
        correct: true,
        duration_ms: 1234,
        hints_used: 0,
        item_rev: 2,
        content_build: 'abc123',
        session_id: 'id-1',
        occurred_at: '2026-11-06T12:00:00.000Z',
        data: { choice: 0 },
      },
    ])
  })

  it('fills in every column, so all rows in a batch have the same shape', () => {
    const { log, outbox } = setup(fakeEventsClient(OFFLINE))
    log.setUser(ADA)
    log.record({
      type: 'lesson_view',
      topic_id: 'py.variables',
      context: 'learn',
    })
    expect(outbox.pending(ADA)[0]).toMatchObject({
      item_id: null,
      correct: null,
      duration_ms: null,
      hints_used: 0,
      item_rev: null,
      data: {},
    })
    log.stop()
  })

  it('saves nothing while signed out', () => {
    const { log, client } = setup()
    log.setUser(null)
    log.record(ANSWER)
    expect(localStorage.length).toBe(0)
    expect(client.send).not.toHaveBeenCalled()
  })

  it('holds events from while sign-in was loading, then saves them for the learner', async () => {
    const { log, client } = setup()
    log.record(ANSWER)
    expect(client.send).not.toHaveBeenCalled()

    log.setUser(ADA)
    await vi.waitFor(() =>
      expect(client.send).toHaveBeenCalledWith([
        expect.objectContaining({ user_id: ADA, item_id: 'mcq-1' }),
      ]),
    )
  })

  it('drops held events if the visitor turns out to be signed out', async () => {
    const { log, client } = setup()
    log.record(ANSWER)
    log.setUser(null)
    log.setUser(ADA)
    await vi.waitFor(() => expect(log.getStatus().syncing).toBe(false))
    expect(client.send).not.toHaveBeenCalled()
  })

  it('starts a new study session after 30 minutes without activity', () => {
    const { log, outbox, wait } = setup(fakeEventsClient(OFFLINE))
    log.setUser(ADA)
    log.record(ANSWER)
    wait(SESSION_IDLE_MS - 1000)
    log.record(ANSWER)
    wait(SESSION_IDLE_MS + 1000)
    log.record(ANSWER)

    const [first, second, third] = outbox
      .pending(ADA)
      .map((event) => event.session_id)
    expect(second).toBe(first)
    expect(third).not.toBe(second)
    log.stop()
  })

  it('keeps events through failed saves, retrying with growing waits', async () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    const { log, outbox, client } = setup(fakeEventsClient(OFFLINE))
    log.setUser(ADA)
    log.record(ANSWER)
    await vi.advanceTimersByTimeAsync(0)
    expect(client.send).toHaveBeenCalledTimes(1)
    expect(log.getStatus()).toEqual({ pending: 1, syncing: false, refused: 0 })

    // The first retry comes after 5 seconds...
    await vi.advanceTimersByTimeAsync(FIRST_RETRY_MS)
    expect(client.send).toHaveBeenCalledTimes(2)
    // ...the next one after twice as long.
    await vi.advanceTimersByTimeAsync(FIRST_RETRY_MS)
    expect(client.send).toHaveBeenCalledTimes(2)

    client.send.mockResolvedValue({ ok: true })
    await vi.advanceTimersByTimeAsync(FIRST_RETRY_MS)
    expect(client.send).toHaveBeenCalledTimes(3)
    expect(outbox.count(ADA)).toBe(0)
    expect(log.getStatus()).toEqual({ pending: 0, syncing: false, refused: 0 })
  })

  it('tries again straight away when asked, e.g. when the connection returns', async () => {
    const { log, outbox, client } = setup(fakeEventsClient(OFFLINE))
    log.setUser(ADA)
    log.record(ANSWER)
    await vi.waitFor(() => expect(log.getStatus().syncing).toBe(false))

    client.send.mockResolvedValue({ ok: true })
    await log.sync()
    expect(outbox.count(ADA)).toBe(0)
  })

  it("keeps this device's events available, even after they're sent", async () => {
    const { log, client } = setup()
    const before = log.getLocalRows()
    log.setUser(ADA)
    log.record(ANSWER)
    await vi.waitFor(() => expect(client.send).toHaveBeenCalled())
    await vi.waitFor(() => expect(log.getStatus().pending).toBe(0))

    const rows = log.getLocalRows()
    expect(rows).toHaveLength(1)
    expect(rows[0]).toMatchObject({ user_id: ADA, item_id: 'mcq-1' })
    // A new array when something changes, as useSyncExternalStore needs.
    expect(rows).not.toBe(before)
    expect(log.getLocalRows()).toBe(rows)

    log.setUser(null)
    expect(log.getLocalRows()).toEqual([])
  })

  it("lists what's still waiting to be sent, including other tabs' events", async () => {
    const { log, outbox } = setup(fakeEventsClient(OFFLINE))
    log.setUser(ADA)
    log.record(ANSWER)
    await vi.waitFor(() => expect(log.getStatus().syncing).toBe(false))
    // Another tab shares the outbox: it records an event of its own.
    outbox.add({ ...log.getPendingRows()[0]!, id: 'from-another-tab' })

    expect(log.getPendingRows().map((row) => row.id)).toEqual([
      'id-2',
      'from-another-tab',
    ])
    log.setUser(null)
    expect(log.getPendingRows()).toEqual([])
    log.stop()
  })

  it('tells subscribers when the number of unsaved events changes', async () => {
    const { log } = setup(fakeEventsClient(OFFLINE))
    const seen: number[] = []
    log.subscribe(() => seen.push(log.getStatus().pending))
    log.setUser(ADA)
    log.record(ANSWER)
    await vi.waitFor(() => expect(log.getStatus().syncing).toBe(false))
    expect(seen).toContain(1)
    log.stop()
  })
})

describe('events the server refuses', () => {
  /** Records one answer that the server refuses, and waits for that. */
  async function refuseOneAnswer() {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const all = setup(fakeEventsClient(REFUSED))
    all.log.setUser(ADA)
    all.log.record(ANSWER)
    await vi.waitFor(() => expect(all.log.getStatus().refused).toBe(1))
    await vi.waitFor(() => expect(all.log.getStatus().syncing).toBe(false))
    all.client.send.mockClear()
    return all
  }

  it('counts them apart from what is waiting, and lists them with the reason', async () => {
    const { log } = await refuseOneAnswer()
    expect(log.getStatus()).toEqual({ pending: 0, syncing: false, refused: 1 })
    expect(log.getRefusedEvents()).toEqual([
      {
        event: expect.objectContaining({ user_id: ADA, item_id: 'mcq-1' }),
        reason: REFUSED.message,
        at: '2026-11-06T12:00:00.000Z',
        attempts: 1,
      },
    ])

    log.setUser(null)
    expect(log.getStatus().refused).toBe(0)
    expect(log.getRefusedEvents()).toEqual([])
  })

  it('saves them on a later sync, once the server accepts them', async () => {
    const { log, client, wait } = await refuseOneAnswer()
    const seen: number[] = []
    log.subscribe(() => seen.push(log.getStatus().refused))

    // The database has caught up, and half a day has gone by.
    client.send.mockResolvedValue({ ok: true })
    wait(RETRY_REFUSED_AFTER_MS + 1000)
    await log.sync()

    expect(client.send).toHaveBeenCalledWith([
      expect.objectContaining({ user_id: ADA, item_id: 'mcq-1' }),
    ])
    expect(log.getStatus()).toEqual({ pending: 0, syncing: false, refused: 0 })
    expect(log.getRefusedEvents()).toEqual([])
    // Subscribers heard, so the page's warning goes away.
    expect(seen.at(-1)).toBe(0)
  })

  it('leaves them alone for 12 hours after the last attempt', async () => {
    const { log, client, wait } = await refuseOneAnswer()
    client.send.mockResolvedValue({ ok: true })

    wait(RETRY_REFUSED_AFTER_MS - 1000)
    await log.sync()
    expect(client.send).not.toHaveBeenCalled()
    expect(log.getStatus().refused).toBe(1)
  })

  it('keeps one that is refused again, and counts the attempt', async () => {
    const { log, wait } = await refuseOneAnswer()
    wait(RETRY_REFUSED_AFTER_MS + 1000)
    await log.sync()

    expect(log.getStatus().refused).toBe(1)
    expect(log.getRefusedEvents()[0]).toMatchObject({
      attempts: 2,
      at: '2026-11-07T00:00:01.000Z',
    })
  })

  it('waits until everything new is saved before trying them again', async () => {
    const { log, client, wait } = await refuseOneAnswer()
    wait(RETRY_REFUSED_AFTER_MS + 1000)
    // Offline: the new answer can't be sent, so nothing else is tried.
    client.send.mockResolvedValue(OFFLINE)
    log.record(ANSWER)
    await vi.waitFor(() => expect(log.getStatus().syncing).toBe(false))

    expect(client.send).toHaveBeenCalledTimes(1)
    expect(log.getRefusedEvents()[0]).toMatchObject({ attempts: 1 })
    log.stop()
  })

  it("doesn't start a retry timer when only the second try fails for now", async () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    const { log, client, wait } = await refuseOneAnswer()
    wait(RETRY_REFUSED_AFTER_MS + 1000)
    client.send.mockResolvedValue(OFFLINE)
    await log.sync()
    expect(client.send).toHaveBeenCalledTimes(1)

    // Nothing is waiting in the outbox, so the log stays quiet until the
    // next save, however long that takes.
    await vi.advanceTimersByTimeAsync(60 * 60 * 1000)
    expect(client.send).toHaveBeenCalledTimes(1)
    expect(log.getStatus()).toEqual({ pending: 0, syncing: false, refused: 1 })
  })

  it("never sends another learner's refused events", async () => {
    const { log, outbox, client, wait } = await refuseOneAnswer()
    wait(RETRY_REFUSED_AFTER_MS + 1000)
    client.send.mockResolvedValue({ ok: true })

    // Someone else signs in on this device.
    log.setUser(BOB)
    await log.sync()
    await vi.waitFor(() => expect(log.getStatus().syncing).toBe(false))

    expect(client.send).not.toHaveBeenCalled()
    expect(log.getStatus().refused).toBe(0)
    expect(outbox.refused(ADA)).toHaveLength(1)
  })
})
