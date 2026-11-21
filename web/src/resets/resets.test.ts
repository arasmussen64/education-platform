import { describe, expect, it } from 'vitest'
import { eventRow } from '../test/fakeEvents.ts'
import {
  afterResets,
  latestResets,
  localResets,
  NO_RESETS,
  toReset,
  trackOfPlacement,
  trackOfTopic,
  trackResetEvent,
  wasReset,
} from './resets.ts'

const at = (hour: number) =>
  `2026-11-21T${String(hour).padStart(2, '0')}:00:00.000Z`

describe('starting a track over', () => {
  it('records one event naming the track, in the topic column', () => {
    expect(trackResetEvent('python-foundations')).toEqual({
      type: 'track_reset',
      topic_id: 'python-foundations',
      context: 'learn',
    })
  })

  it("reads a reset from a server row, with the server's time written the browser's way", () => {
    expect(
      toReset({
        type: 'track_reset',
        topic_id: 'python-foundations',
        occurred_at: '2026-11-21T09:00:00+00:00',
      }),
    ).toEqual({ track: 'python-foundations', occurred_at: at(9) })
    expect(
      toReset({ type: 'answer', topic_id: 'py.variables', occurred_at: at(9) }),
    ).toBeNull()
  })

  it('finds resets among the events this device recorded', () => {
    const rows = [
      eventRow({ type: 'answer', occurred_at: at(8) }),
      eventRow({
        type: 'track_reset',
        topic_id: 'python-foundations',
        item_id: null,
        correct: null,
        occurred_at: at(9),
      }),
    ]
    expect(localResets(rows)).toEqual([
      { track: 'python-foundations', occurred_at: at(9) },
    ])
  })

  it('keeps only the newest reset of each track', () => {
    const latest = latestResets(
      [{ track: 'python-foundations', occurred_at: at(9) }],
      [
        { track: 'python-foundations', occurred_at: at(11) },
        { track: 'python-foundations', occurred_at: at(10) },
        { track: 'cloud-solutions-architect', occurred_at: at(8) },
      ],
    )
    expect(latest).toEqual(
      new Map([
        ['python-foundations', at(11)],
        ['cloud-solutions-architect', at(8)],
      ]),
    )
  })

  it('stops counting what happened on a track before its newest reset, and nothing else', () => {
    const resets = new Map([['python-foundations', at(10)]])
    expect(wasReset('python-foundations', at(9), resets)).toBe(true)
    expect(wasReset('python-foundations', at(10), resets)).toBe(false)
    expect(wasReset('python-foundations', at(11), resets)).toBe(false)
    expect(wasReset('cloud-solutions-architect', at(9), resets)).toBe(false)
    expect(wasReset(undefined, at(9), resets)).toBe(false)
  })

  it("drops a reset track's earlier events and keeps every other one, in order", () => {
    const trackOf = (topicId: string) =>
      topicId.startsWith('py.') ? 'python-foundations' : 'other'
    const events = [
      { id: 'a', topic_id: 'py.variables', occurred_at: at(8) },
      { id: 'b', topic_id: 'csa.intro', occurred_at: at(8) },
      { id: 'c', topic_id: 'py.loops', occurred_at: at(11) },
    ]
    const resets = new Map([['python-foundations', at(10)]])
    expect(
      afterResets(events, resets, trackOf).map((event) => event.id),
    ).toEqual(['b', 'c'])
  })

  it('hands back the very same list when no track was started over', () => {
    const events = [{ topic_id: 'py.variables', occurred_at: at(8) }]
    expect(afterResets(events, NO_RESETS)).toBe(events)
  })

  it("knows a real topic's track from the content", () => {
    expect(trackOfTopic('py.variables')).toBe('python-foundations')
    expect(trackOfTopic('no.such-topic')).toBeUndefined()
  })

  it("clears a track's placements and its modules' foundations lists, never a diagnostic", () => {
    expect(
      trackOfPlacement({ subject: 'python-foundations', kind: 'track' }),
    ).toBe('python-foundations')
    expect(
      trackOfPlacement({
        subject: 'foundations.ml.m1',
        kind: 'foundations',
        list: { track: 'ml-foundations' },
      }),
    ).toBe('ml-foundations')
    expect(
      trackOfPlacement({ subject: 'diagnostic.math', kind: 'diagnostic' }),
    ).toBeUndefined()
  })
})
