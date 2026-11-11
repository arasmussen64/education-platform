import { describe, expect, it, vi } from 'vitest'
import { PAGE_SIZE } from '../followups/history.ts'
import { fakeCheckpointContent } from '../test/fakeContent.tsx'
import { eventRow } from '../test/fakeEvents.ts'
import {
  fetchStepsOpened,
  localStepsOpened,
  stepsOpenedEvent,
  toStepsOpened,
} from './stepsOpened.ts'

// A stand-in for Supabase's query builder: every call returns the builder,
// and range() answers with the next page from `pages`.
const pages = vi.hoisted(() => ({
  rows: [] as unknown[][],
  ranges: [] as number[][],
  filters: [] as unknown[][],
}))
vi.mock('../supabase/client.ts', () => {
  const builder = {
    from: () => builder,
    select: () => builder,
    eq: (column: string, value: unknown) => {
      pages.filters.push([column, value])
      return builder
    },
    order: () => builder,
    range: (from: number, to: number) => {
      pages.ranges.push([from, to])
      return Promise.resolve({ data: pages.rows.shift() ?? [], error: null })
    },
  }
  return { getSupabase: () => builder }
})

/** A row as the server sends it back. */
function row(overrides: Record<string, unknown> = {}) {
  return {
    type: 'hint',
    topic_id: 'py.m1.checkpoint',
    occurred_at: '2026-11-11T09:30:00.000+00:00',
    source: 'steps',
    ...overrides,
  }
}

describe('the event saved when the steps open', () => {
  it("is a hint on the checkpoint's build, from the steps", () => {
    const content = fakeCheckpointContent()
    expect(stepsOpenedEvent(content)).toEqual({
      type: 'hint',
      topic_id: 'py.m1.checkpoint',
      item_id: 'build-receipt',
      item_rev: content.exercises['build-receipt']?.rev,
      context: 'prove',
      data: { source: 'steps' },
    })
  })
})

describe('toStepsOpened', () => {
  it('reads an opening of the steps, in one time format', () => {
    expect(toStepsOpened(row())).toEqual({
      topic_id: 'py.m1.checkpoint',
      occurred_at: '2026-11-11T09:30:00.000Z',
    })
  })

  it('skips hints from anywhere else, and other events', () => {
    expect(toStepsOpened(row({ source: 'author' }))).toBeNull()
    expect(toStepsOpened(row({ source: 'tutor' }))).toBeNull()
    expect(toStepsOpened(row({ source: undefined }))).toBeNull()
    expect(toStepsOpened(row({ type: 'code_check' }))).toBeNull()
  })
})

describe('localStepsOpened', () => {
  it("reads the source from the event's data", () => {
    const opened = eventRow({
      type: 'hint',
      topic_id: 'py.m1.checkpoint',
      item_id: 'build-receipt',
      context: 'prove',
      correct: null,
      occurred_at: '2026-11-11T09:30:00.000Z',
      data: { source: 'steps' },
    })
    expect(localStepsOpened(opened)).toEqual({
      topic_id: 'py.m1.checkpoint',
      occurred_at: '2026-11-11T09:30:00.000Z',
    })
    expect(
      localStepsOpened({ ...opened, data: { source: 'author', level: 1 } }),
    ).toBeNull()
    expect(localStepsOpened(eventRow())).toBeNull()
  })
})

describe('fetchStepsOpened', () => {
  it('asks only for openings of the steps, and reads every page', async () => {
    pages.ranges = []
    pages.filters = []
    pages.rows = [Array.from({ length: PAGE_SIZE }, () => row()), [row()]]
    expect(await fetchStepsOpened()).toHaveLength(PAGE_SIZE + 1)
    expect(pages.ranges).toEqual([
      [0, PAGE_SIZE - 1],
      [PAGE_SIZE, 2 * PAGE_SIZE - 1],
    ])
    expect(pages.filters.slice(0, 2)).toEqual([
      ['type', 'hint'],
      ['data->>source', 'steps'],
    ])
  })
})
