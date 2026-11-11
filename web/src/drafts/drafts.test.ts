import { describe, expect, it } from 'vitest'
import {
  clearDraft,
  DRAFTS_BUDGET,
  loadDraft,
  MAX_DRAFT_CHARS,
  saveDraft,
} from './drafts.ts'

const LOOPS = { topicId: 'py.loops', itemId: 'fill-sum', rev: 1 }
const SWAP = { topicId: 'py.variables', itemId: 'fill-swap', rev: 2 }

/**
 * A stand-in for localStorage. With `capacity`, it refuses to store more
 * than that many characters, the way a full browser storage does.
 */
function fakeStorage(capacity = Infinity) {
  const items = new Map<string, string>()
  return {
    items,
    getItem: (key: string) => items.get(key) ?? null,
    setItem(key: string, value: string) {
      if (value.length > capacity) throw new Error('QuotaExceededError')
      items.set(key, value)
    },
  }
}

/** Storage the browser has switched off: every use throws. */
const blocked = {
  getItem: (): string | null => {
    throw new Error('SecurityError')
  },
  setItem: () => {
    throw new Error('SecurityError')
  },
}

describe('drafts', () => {
  it('gives back what was saved, per topic and item', () => {
    const storage = fakeStorage()
    saveDraft(LOOPS, 'total = 0\nfor n in nums:', storage, 1000)
    saveDraft(SWAP, 'a, b = b, a', storage, 2000)
    expect(loadDraft(LOOPS, storage)).toBe('total = 0\nfor n in nums:')
    expect(loadDraft(SWAP, storage)).toBe('a, b = b, a')
    expect(loadDraft({ ...LOOPS, itemId: 'write-mean' }, storage)).toBeNull()
  })

  it('keeps one draft per item: a new save replaces the old', () => {
    const storage = fakeStorage()
    saveDraft(LOOPS, 'first', storage, 1000)
    saveDraft(LOOPS, 'second', storage, 2000)
    expect(loadDraft(LOOPS, storage)).toBe('second')
  })

  it("doesn't give back a draft saved for another revision of the item", () => {
    const storage = fakeStorage()
    saveDraft(LOOPS, 'written for rev 1', storage, 1000)
    expect(loadDraft({ ...LOOPS, rev: 2 }, storage)).toBeNull()
    // Typing in the new revision replaces the old draft.
    saveDraft({ ...LOOPS, rev: 2 }, 'written for rev 2', storage, 2000)
    expect(loadDraft({ ...LOOPS, rev: 2 }, storage)).toBe('written for rev 2')
    expect(loadDraft(LOOPS, storage)).toBeNull()
  })

  it('forgets a cleared draft, and only that one', () => {
    const storage = fakeStorage()
    saveDraft(LOOPS, 'loops', storage, 1000)
    saveDraft(SWAP, 'swap', storage, 2000)
    clearDraft(LOOPS, storage)
    expect(loadDraft(LOOPS, storage)).toBeNull()
    expect(loadDraft(SWAP, storage)).toBe('swap')
  })

  it('drops the oldest drafts when they would go over their budget', () => {
    const storage = fakeStorage()
    const long = 'x'.repeat(MAX_DRAFT_CHARS)
    const count = DRAFTS_BUDGET / MAX_DRAFT_CHARS + 1
    for (let index = 0; index < count; index++) {
      saveDraft({ ...LOOPS, itemId: `item-${index}` }, long, storage, index)
    }
    // The first one saved is the one that made room.
    expect(loadDraft({ ...LOOPS, itemId: 'item-0' }, storage)).toBeNull()
    for (let index = 1; index < count; index++) {
      expect(loadDraft({ ...LOOPS, itemId: `item-${index}` }, storage)).toBe(
        long,
      )
    }
  })

  it("doesn't keep a draft longer than any answer, nor let it push others out", () => {
    const storage = fakeStorage()
    saveDraft(SWAP, 'a, b = b, a', storage, 1000)
    saveDraft(LOOPS, 'x'.repeat(MAX_DRAFT_CHARS + 1), storage, 2000)
    expect(loadDraft(LOOPS, storage)).toBeNull()
    expect(loadDraft(SWAP, storage)).toBe('a, b = b, a')
  })

  it('makes room by dropping the oldest drafts when the browser says storage is full', () => {
    // Room for two of these drafts (about 310 characters stored), not three.
    const storage = fakeStorage(400)
    const text = (letter: string) => letter.repeat(100)
    saveDraft({ ...LOOPS, itemId: 'oldest' }, text('a'), storage, 1000)
    saveDraft({ ...LOOPS, itemId: 'middle' }, text('b'), storage, 2000)
    saveDraft({ ...LOOPS, itemId: 'newest' }, text('c'), storage, 3000)
    expect(loadDraft({ ...LOOPS, itemId: 'oldest' }, storage)).toBeNull()
    expect(loadDraft({ ...LOOPS, itemId: 'middle' }, storage)).toBe(text('b'))
    expect(loadDraft({ ...LOOPS, itemId: 'newest' }, storage)).toBe(text('c'))
  })

  it("leaves storage as it was when even one draft won't fit", () => {
    const storage = fakeStorage(150)
    saveDraft(SWAP, 'a, b = b, a', storage, 1000)
    const before = [...storage.items]
    saveDraft(LOOPS, 'y'.repeat(200), storage, 2000)
    expect([...storage.items]).toEqual(before)
    expect(loadDraft(SWAP, storage)).toBe('a, b = b, a')
  })

  it('works without storage, or with storage switched off, just without drafts', () => {
    expect(loadDraft(LOOPS, null)).toBeNull()
    expect(() => saveDraft(LOOPS, 'code', null, 1000)).not.toThrow()
    expect(() => clearDraft(LOOPS, null)).not.toThrow()

    expect(() => saveDraft(LOOPS, 'code', blocked, 1000)).not.toThrow()
    expect(loadDraft(LOOPS, blocked)).toBeNull()
    expect(() => clearDraft(LOOPS, blocked)).not.toThrow()
  })

  it('ignores saved drafts it cannot read, and keeps the rest', () => {
    const storage = fakeStorage()
    storage.setItem(
      'drafts-v1',
      JSON.stringify({
        'py.loops/fill-sum': { rev: 1, text: 'kept', savedAt: 1 },
        'py.loops/broken': null,
        'py.loops/no-text': { rev: 1, savedAt: 1 },
      }),
    )
    expect(loadDraft(LOOPS, storage)).toBe('kept')
    expect(loadDraft({ ...LOOPS, itemId: 'broken' }, storage)).toBeNull()
    saveDraft(SWAP, 'swap', storage, 2000)
    expect(loadDraft(LOOPS, storage)).toBe('kept')

    storage.setItem('drafts-v1', 'not json')
    expect(loadDraft(LOOPS, storage)).toBeNull()
    saveDraft(LOOPS, 'fresh', storage, 3000)
    expect(loadDraft(LOOPS, storage)).toBe('fresh')
  })
})
