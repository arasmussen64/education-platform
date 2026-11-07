import { beforeEach, describe, expect, it, vi } from 'vitest'
import { eventRow } from '../test/fakeEvents.ts'
import {
  collectExport,
  EXPORT_FORMAT,
  exportFileName,
  PAGE_SIZE,
} from './exportData.ts'

const ADA = '11111111-1111-1111-1111-111111111111'
const RECEIVED = '2026-11-06T12:00:05.123456+00:00'

// A stand-in for Supabase's query builder. Events come back a page at a
// time from `server.pages`, and the profile from `server.profile`. It notes
// which table each request was for, in order, in `server.calls`.
const server = vi.hoisted(() => ({
  pages: [] as unknown[][],
  profile: null as unknown,
  error: null as { message: string } | null,
  calls: [] as string[],
  ranges: [] as number[][],
  filters: [] as unknown[][],
}))
vi.mock('../supabase/client.ts', () => {
  const answer = (data: unknown) =>
    Promise.resolve(
      server.error
        ? { data: null, error: server.error }
        : { data, error: null },
    )
  const builder = {
    from: (table: string) => {
      server.calls.push(table)
      return builder
    },
    select: () => builder,
    eq: (column: string, value: unknown) => {
      server.filters.push([column, value])
      return builder
    },
    order: () => builder,
    range: (from: number, to: number) => {
      server.ranges.push([from, to])
      return answer(server.pages.shift() ?? [])
    },
    maybeSingle: () => answer(server.profile),
  }
  return { getSupabase: () => builder }
})

/** An event as the server sends it back: with the time it arrived. */
function saved(id: string, occurredAt = '2026-11-06T12:00:00.000+00:00') {
  return { ...eventRow({ id, occurred_at: occurredAt }), received_at: RECEIVED }
}

beforeEach(() => {
  server.pages = []
  server.profile = null
  server.error = null
  server.calls = []
  server.ranges = []
  server.filters = []
})

describe('collectExport', () => {
  it('reads every event, a page at a time, until a page comes back empty', async () => {
    server.pages = [
      Array.from({ length: PAGE_SIZE }, (_, index) => saved(`event-${index}`)),
      [saved('the-last-one')],
    ]
    const data = await collectExport(ADA, () => [])

    expect(data.events).toHaveLength(PAGE_SIZE + 1)
    expect(server.ranges).toEqual([
      [0, PAGE_SIZE - 1],
      [PAGE_SIZE, 2 * PAGE_SIZE - 1],
      [PAGE_SIZE + 1, 2 * PAGE_SIZE],
    ])
    // Only this learner's events, even if row-level security were missing.
    expect(server.filters).toContainEqual(['user_id', ADA])
  })

  it('keeps reading when the server sends fewer rows than it was asked for', async () => {
    server.pages = [[saved('a'), saved('b')], [saved('c')]]
    const data = await collectExport(ADA, () => [])
    expect(data.events.map((event) => event.id)).toEqual(['a', 'b', 'c'])
  })

  it("adds the events still waiting in this browser's outbox, each once, in time order", async () => {
    // "b" reached the server but is still in the outbox; "c" is only there.
    server.pages = [
      [
        saved('a', '2026-11-06T09:00:00+00:00'),
        saved('b', '2026-11-06T11:00:00+00:00'),
      ],
    ]
    const pending = [
      eventRow({ id: 'b', occurred_at: '2026-11-06T11:00:00.000Z' }),
      eventRow({ id: 'c', occurred_at: '2026-11-06T10:00:00.000Z' }),
    ]
    const data = await collectExport(ADA, () => pending)

    expect(data.events.map((event) => [event.id, event.received_at])).toEqual([
      ['a', RECEIVED],
      ['c', null],
      ['b', RECEIVED],
    ])
  })

  it('reads the outbox before asking the server, so no event can fall between them', async () => {
    const readPending = vi.fn(() => {
      server.calls.push('outbox')
      return []
    })
    await collectExport(ADA, readPending)
    expect(server.calls[0]).toBe('outbox')
  })

  it('includes the profile, the time, and the app that made the file', async () => {
    server.profile = {
      id: ADA,
      display_name: null,
      allowed: false,
      settings: {},
      created_at: '2026-11-06T10:25:00+00:00',
    }
    const now = Date.parse('2026-11-07T09:15:00.000Z')
    const data = await collectExport(ADA, () => [], now)

    expect(data).toMatchObject({
      format: EXPORT_FORMAT,
      exported_at: '2026-11-07T09:15:00.000Z',
      user_id: ADA,
      profile: server.profile,
      events: [],
    })
    expect(data.content_build).toEqual(expect.any(String))
    expect(server.filters).toContainEqual(['id', ADA])
  })

  it("fails when the server can't be read, so the page can say so", async () => {
    server.error = { message: 'TypeError: Failed to fetch' }
    await expect(collectExport(ADA, () => [])).rejects.toThrow(
      'Failed to fetch',
    )
  })
})

describe('exportFileName', () => {
  it("names the file after the app and the learner's own date", () => {
    // Noon on November 7, wherever the test runs.
    const noon = new Date(2026, 10, 7, 12).getTime()
    expect(exportFileName(noon)).toMatch(/^[a-z0-9-]+-data-2026-11-07\.json$/)
  })
})
