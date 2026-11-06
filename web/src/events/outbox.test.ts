import { describe, expect, it, vi } from 'vitest'
import { eventRow } from '../test/fakeEvents.ts'
import { createOutbox } from './outbox.ts'

const ADA = '11111111-1111-1111-1111-111111111111'
const BOB = '33333333-3333-3333-3333-333333333333'

const ids = (events: { id: string }[]) => events.map((event) => event.id)

describe('the outbox', () => {
  it("hands out a learner's events oldest first, and only theirs", () => {
    const outbox = createOutbox()
    outbox.add(eventRow({ id: 'a1' }))
    outbox.add(eventRow({ id: 'b1', user_id: BOB }))
    outbox.add(eventRow({ id: 'a2' }))
    expect(ids(outbox.pending(ADA))).toEqual(['a1', 'a2'])
    expect(ids(outbox.pending(ADA, 1))).toEqual(['a1'])
    expect(outbox.count(BOB)).toBe(1)
  })

  it('survives a reload: a new outbox sees what the last one saved', () => {
    createOutbox().add(eventRow({ id: 'e1' }))
    expect(ids(createOutbox().pending(ADA))).toEqual(['e1'])
  })

  it('forgets events once the server has them', () => {
    const outbox = createOutbox()
    outbox.add(eventRow({ id: 'e1' }))
    outbox.add(eventRow({ id: 'e2' }))
    outbox.remove(['e1'])
    expect(ids(outbox.pending(ADA))).toEqual(['e2'])
  })

  it("never loses another tab's new events when removing sent ones", () => {
    const thisTab = createOutbox()
    const otherTab = createOutbox()
    thisTab.add(eventRow({ id: 'sent' }))
    otherTab.add(eventRow({ id: 'new' }))
    thisTab.remove(['sent'])
    expect(ids(otherTab.pending(ADA))).toEqual(['new'])
  })

  it('moves refused events aside, out of the way of the rest', () => {
    const outbox = createOutbox()
    const bad = eventRow({ id: 'bad' })
    outbox.add(bad)
    outbox.reject(bad, '400 23514: violates check constraint')
    expect(outbox.pending(ADA)).toEqual([])
    expect(outbox.rejected()).toEqual([
      {
        event: bad,
        reason: '400 23514: violates check constraint',
        at: expect.any(String),
      },
    ])
  })

  it('treats unreadable storage as empty', () => {
    localStorage.setItem('learner-events-outbox-v1', 'not json')
    expect(createOutbox().pending(ADA)).toEqual([])
  })

  it("doesn't crash when storage is full or switched off", () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    const broken = {
      getItem: () => {
        throw new DOMException('denied', 'SecurityError')
      },
      setItem: () => {
        throw new DOMException('full', 'QuotaExceededError')
      },
    } as unknown as Storage
    const outbox = createOutbox(broken)
    expect(() => outbox.add(eventRow())).not.toThrow()
    expect(outbox.pending(ADA)).toEqual([])
  })
})
