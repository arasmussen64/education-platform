import { describe, expect, it, vi } from 'vitest'
import { eventRow } from '../test/fakeEvents.ts'
import { isTemporaryFailure, supabaseEventsClient } from './supabaseEvents.ts'

// A stand-in for the Supabase client: records upsert calls on the events
// table and answers with whatever the test chooses.
const upsert = vi.hoisted(() => vi.fn())
vi.mock('../supabase/client.ts', () => ({
  getSupabase: () => ({
    from: (table: string) => ({
      upsert: (...args: unknown[]) => upsert(table, ...args),
    }),
  }),
}))

describe('supabaseEventsClient', () => {
  it('inserts events, skipping any the server already has', async () => {
    upsert.mockResolvedValue({ error: null, status: 201 })
    const events = [eventRow()]

    expect(await supabaseEventsClient().send(events)).toEqual({ ok: true })
    expect(upsert).toHaveBeenCalledWith('events', events, {
      onConflict: 'id',
      ignoreDuplicates: true,
    })
  })

  it('says to try again later when there is no connection', async () => {
    upsert.mockResolvedValue({
      error: { code: '', message: 'TypeError: Failed to fetch' },
      status: 0,
    })
    expect(await supabaseEventsClient().send([eventRow()])).toEqual({
      ok: false,
      retryLater: true,
      message: '0 : TypeError: Failed to fetch',
    })
  })

  it('says not to retry when the server refuses the data itself', async () => {
    upsert.mockResolvedValue({
      error: { code: '23514', message: 'violates check constraint' },
      status: 400,
    })
    expect(await supabaseEventsClient().send([eventRow()])).toMatchObject({
      ok: false,
      retryLater: false,
    })
  })
})

describe('isTemporaryFailure', () => {
  it('retries connection, sign-in and server trouble, but not refused data', () => {
    for (const status of [0, 401, 408, 429, 500, 503]) {
      expect(isTemporaryFailure(status), String(status)).toBe(true)
    }
    for (const status of [400, 403, 409, 413]) {
      expect(isTemporaryFailure(status), String(status)).toBe(false)
    }
  })
})
