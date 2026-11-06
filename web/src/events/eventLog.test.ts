import { afterEach, describe, expect, it, vi } from 'vitest'
import { fakeEventsClient } from '../test/fakeEvents.ts'
import { createEventLog, FIRST_RETRY_MS, SESSION_IDLE_MS } from './eventLog.ts'
import { createOutbox } from './outbox.ts'
import type { NewEvent } from './types.ts'

const ADA = '11111111-1111-1111-1111-111111111111'

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
    expect(log.getStatus()).toEqual({ pending: 1, syncing: false })

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
    expect(log.getStatus()).toEqual({ pending: 0, syncing: false })
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
