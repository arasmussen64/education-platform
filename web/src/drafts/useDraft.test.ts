import { renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { loadDraft, saveDraft } from './drafts.ts'
import { SAVE_DELAY_MS, useDraft } from './useDraft.ts'

const KEY = { topicId: 'py.loops', itemId: 'fill-sum', rev: 1 }
const STARTER = 'total = 0\n'

describe('useDraft', () => {
  beforeEach(() => {
    // Pinned, so no test reads the real clock (drafts note when they were saved).
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout', 'Date'] })
    vi.setSystemTime(new Date('2026-11-11T12:00:00.000Z'))
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('starts from the starter when there is no draft', () => {
    const { result } = renderHook(() => useDraft(KEY, STARTER))
    expect(result.current.initial).toBe(STARTER)
    expect(result.current.restored).toBe(false)
  })

  it('starts from the draft from last time', () => {
    saveDraft(KEY, 'total = 0\nfor n in nums:\n')
    const { result } = renderHook(() => useDraft(KEY, STARTER))
    expect(result.current.initial).toBe('total = 0\nfor n in nums:\n')
    expect(result.current.restored).toBe(true)
  })

  it('saves once typing pauses, not on every key', () => {
    const { result } = renderHook(() => useDraft(KEY, STARTER))
    result.current.save('total = 0\nf')
    result.current.save('total = 0\nfo')
    vi.advanceTimersByTime(SAVE_DELAY_MS - 1)
    expect(loadDraft(KEY)).toBeNull()
    vi.advanceTimersByTime(1)
    expect(loadDraft(KEY)).toBe('total = 0\nfo')
  })

  it('saves what is waiting when the page is closed or reloaded', () => {
    const { result } = renderHook(() => useDraft(KEY, STARTER))
    result.current.save('total = 0\nfor')
    window.dispatchEvent(new Event('pagehide'))
    expect(loadDraft(KEY)).toBe('total = 0\nfor')
  })

  it('saves what is waiting when the editor goes away', () => {
    const { result, unmount } = renderHook(() => useDraft(KEY, STARTER))
    result.current.save('total = 0\nfor')
    unmount()
    expect(loadDraft(KEY)).toBe('total = 0\nfor')
  })

  it('forgets the draft when the text is back to the starter', () => {
    saveDraft(KEY, 'total = 0\nfor')
    const { result } = renderHook(() => useDraft(KEY, STARTER))
    result.current.save(STARTER)
    vi.advanceTimersByTime(SAVE_DELAY_MS)
    expect(loadDraft(KEY)).toBeNull()
  })

  it('forgets the draft on Start over, and keeps saving after it', () => {
    saveDraft(KEY, 'total = 0\nfor')
    const { result } = renderHook(() => useDraft(KEY, STARTER))
    result.current.save('total = 0\nfor n')
    result.current.discard()
    expect(loadDraft(KEY)).toBeNull()
    // The change typed just before Start over isn't saved later, either.
    vi.advanceTimersByTime(SAVE_DELAY_MS)
    expect(loadDraft(KEY)).toBeNull()

    result.current.save('total = 1')
    vi.advanceTimersByTime(SAVE_DELAY_MS)
    expect(loadDraft(KEY)).toBe('total = 1')
  })

  it('forgets the draft when the item passes, and saves nothing more', () => {
    saveDraft(KEY, 'total = 0\nfor')
    const { result, unmount } = renderHook(() => useDraft(KEY, STARTER))
    result.current.finish()
    expect(loadDraft(KEY)).toBeNull()

    result.current.save('trying something after passing')
    vi.advanceTimersByTime(SAVE_DELAY_MS)
    unmount()
    expect(loadDraft(KEY)).toBeNull()
  })

  it('keeps nothing without a key', () => {
    const { result, unmount } = renderHook(() => useDraft(undefined, STARTER))
    result.current.save('total = 0\nfor')
    vi.advanceTimersByTime(SAVE_DELAY_MS)
    unmount()
    expect(localStorage.length).toBe(0)
  })
})
