import { describe, expect, it, vi } from 'vitest'
import {
  fetchAttempts,
  mergeAttempts,
  PAGE_SIZE,
  toAttempt,
} from './history.ts'

// A stand-in for Supabase's query builder: every call returns the builder,
// and range() answers with the next page from `pages`.
const pages = vi.hoisted(() => ({
  rows: [] as unknown[][],
  ranges: [] as number[][],
}))
vi.mock('../supabase/client.ts', () => {
  const builder = {
    from: () => builder,
    select: () => builder,
    in: () => builder,
    not: () => builder,
    order: () => builder,
    range: (from: number, to: number) => {
      pages.ranges.push([from, to])
      return Promise.resolve({ data: pages.rows.shift() ?? [], error: null })
    },
  }
  return { getSupabase: () => builder }
})

function row(id: number, overrides: Record<string, unknown> = {}) {
  return {
    id: `event-${id}`,
    type: 'answer',
    topic_id: 'py.variables',
    item_id: 'mcq-1',
    correct: true,
    occurred_at: '2026-11-06T18:35:57.823+00:00',
    ...overrides,
  }
}

describe('toAttempt', () => {
  it('keeps graded answers and Checks, in one time format', () => {
    expect(toAttempt(row(1))).toEqual({
      id: 'event-1',
      type: 'answer',
      topic_id: 'py.variables',
      item_id: 'mcq-1',
      correct: true,
      occurred_at: '2026-11-06T18:35:57.823Z',
    })
  })

  it('skips events that are not graded attempts', () => {
    expect(toAttempt(row(1, { type: 'lesson_view' }))).toBeNull()
    expect(toAttempt(row(1, { type: 'code_run', correct: null }))).toBeNull()
    expect(toAttempt(row(1, { item_id: null }))).toBeNull()
  })
})

describe('mergeAttempts', () => {
  it('keeps each event once, oldest first', () => {
    const early = toAttempt(row(1, { occurred_at: '2026-11-05T10:00:00Z' }))!
    const late = toAttempt(row(2, { occurred_at: '2026-11-06T10:00:00Z' }))!
    expect(mergeAttempts([late, early], [early])).toEqual([early, late])
  })
})

describe('fetchAttempts', () => {
  it('reads every page until a short one', async () => {
    pages.ranges = []
    pages.rows = [
      Array.from({ length: PAGE_SIZE }, (_, index) => row(index)),
      [row(PAGE_SIZE)],
    ]
    const attempts = await fetchAttempts()
    expect(attempts).toHaveLength(PAGE_SIZE + 1)
    expect(pages.ranges).toEqual([
      [0, PAGE_SIZE - 1],
      [PAGE_SIZE, 2 * PAGE_SIZE - 1],
    ])
  })
})
