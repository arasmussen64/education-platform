import { describe, expect, it, vi } from 'vitest'
import { eventRow } from '../test/fakeEvents.ts'
import { createOutbox } from './outbox.ts'

const ADA = '11111111-1111-1111-1111-111111111111'
const BOB = '33333333-3333-3333-3333-333333333333'

const REFUSED_KEY = 'learner-events-rejected-v1'
const NOON = Date.parse('2026-11-10T12:00:00.000Z')
const HOUR = 60 * 60 * 1000

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
    outbox.refuse(bad, '400 23514: violates check constraint', NOON)
    expect(outbox.pending(ADA)).toEqual([])
    expect(outbox.refused(ADA)).toEqual([
      {
        event: bad,
        reason: '400 23514: violates check constraint',
        at: '2026-11-10T12:00:00.000Z',
        attempts: 1,
      },
    ])
  })

  it('keeps one entry for an event refused again, with the new reason, the new time and the attempts counted', () => {
    const outbox = createOutbox()
    const bad = eventRow({ id: 'bad' })
    const other = eventRow({ id: 'other' })
    outbox.refuse(bad, '400 23514: violates check constraint', NOON)
    outbox.refuse(other, '413 : too large', NOON)
    outbox.refuse(bad, '403 42501: not allowed', NOON + 13 * HOUR)

    expect(outbox.refused(ADA)).toEqual([
      {
        event: bad,
        reason: '403 42501: not allowed',
        at: '2026-11-11T01:00:00.000Z',
        attempts: 2,
      },
      expect.objectContaining({ event: other, attempts: 1 }),
    ])
  })

  it("lists only the given learner's refused events", () => {
    const outbox = createOutbox()
    outbox.refuse(eventRow({ id: 'ada' }), '400 : bad')
    outbox.refuse(eventRow({ id: 'bob', user_id: BOB }), '400 : bad')
    expect(outbox.refused(ADA).map(({ event }) => event.id)).toEqual(['ada'])
    expect(outbox.refused(BOB).map(({ event }) => event.id)).toEqual(['bob'])
  })

  it('forgets a refused event once the server has accepted it, and no other', () => {
    const outbox = createOutbox()
    outbox.refuse(eventRow({ id: 'saved-now' }), '400 : bad')
    outbox.refuse(eventRow({ id: 'still-refused' }), '400 : bad')
    outbox.refuse(eventRow({ id: 'bob', user_id: BOB }), '400 : bad')

    outbox.forgetRefused('saved-now')
    expect(outbox.refused(ADA).map(({ event }) => event.id)).toEqual([
      'still-refused',
    ])
    expect(outbox.refused(BOB)).toHaveLength(1)
  })

  it('counts one attempt for an event refused before attempts were counted', () => {
    // What a browser holds from before refused events were retried.
    const old = {
      event: eventRow({ id: 'old' }),
      reason: '400 : bad',
      at: '2026-11-09T08:00:00.000Z',
    }
    localStorage.setItem(REFUSED_KEY, JSON.stringify([old]))
    const outbox = createOutbox()
    expect(outbox.refused(ADA)).toEqual([{ ...old, attempts: 1 }])

    outbox.refuse(old.event, '400 : still bad', NOON)
    expect(outbox.refused(ADA)[0]).toMatchObject({ attempts: 2 })
  })

  it('never drops an entry it cannot read while changing the others', () => {
    const damaged = [null, { reason: 'no event here' }]
    localStorage.setItem(REFUSED_KEY, JSON.stringify(damaged))
    const outbox = createOutbox()
    outbox.refuse(eventRow({ id: 'bad' }), '400 : bad')
    outbox.refuse(eventRow({ id: 'saved-now' }), '400 : bad')
    outbox.forgetRefused('saved-now')

    expect(outbox.refused(ADA).map(({ event }) => event.id)).toEqual(['bad'])
    const stored = JSON.parse(localStorage.getItem(REFUSED_KEY)!) as unknown[]
    expect(stored.slice(0, 2)).toEqual(damaged)
    expect(stored).toHaveLength(3)
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
