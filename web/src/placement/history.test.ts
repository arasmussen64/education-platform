import { describe, expect, it } from 'vitest'
import { getDiagnostic } from '../content/content.ts'
import { dayOf } from '../days.ts'
import { eventRow } from '../test/fakeEvents.ts'
import { describeDiagnosticRecord, describeTrackRecord } from './describe.ts'
import {
  diagnosticOfSubject,
  latestBySubject,
  localPlacements,
  mergePlacements,
  type PlacementRecord,
  subjectOfDiagnostic,
  toPlacementRecord,
} from './history.ts'

const FINISHED = {
  id: 'e1',
  type: 'placement',
  topic_id: 'python-foundations',
  occurred_at: '2026-11-09T12:00:00+00:00',
  data: {
    run: 'r1',
    kind: 'track',
    known: ['py.programs-and-print', 'py.values-and-types'],
    next: 'py.variables',
    asked: 6,
    correct: 4,
    probes: [],
  },
}

function record(overrides: Partial<PlacementRecord> = {}): PlacementRecord {
  return {
    id: 'e1',
    run: 'r1',
    subject: 'python-foundations',
    kind: 'track',
    at: '2026-11-09T12:00:00.000Z',
    known: ['py.programs-and-print', 'py.values-and-types'],
    next: 'py.variables',
    asked: 6,
    correct: 4,
    ...overrides,
  }
}

describe('reading a finished placement', () => {
  it('keeps what it found, in one time format', () => {
    expect(toPlacementRecord(FINISHED)).toEqual(record())
  })

  it('reads one with nothing left to learn', () => {
    const data = { ...FINISHED.data, next: null, known: ['a', 'b'] }
    expect(toPlacementRecord({ ...FINISHED, data })?.next).toBeNull()
  })

  it('ignores other events and broken data', () => {
    expect(toPlacementRecord({ ...FINISHED, type: 'answer' })).toBeNull()
    expect(toPlacementRecord({ ...FINISHED, data: null })).toBeNull()
    expect(
      toPlacementRecord({ ...FINISHED, data: { ...FINISHED.data, run: 1 } }),
    ).toBeNull()
    expect(
      toPlacementRecord({ ...FINISHED, data: { ...FINISHED.data, kind: 'x' } }),
    ).toBeNull()
    expect(
      toPlacementRecord({
        ...FINISHED,
        data: { ...FINISHED.data, known: 'py.variables' },
      }),
    ).toBeNull()
  })

  it('finds the ones among events this device recorded', () => {
    const rows = [
      eventRow({ id: 'a1' }),
      eventRow({
        id: 'p1',
        type: 'placement',
        topic_id: 'python-foundations',
        context: 'placement',
        correct: null,
        data: FINISHED.data,
      }),
    ]
    expect(localPlacements(rows).map((each) => each.id)).toEqual(['p1'])
  })
})

describe('the latest placement per subject', () => {
  it('keeps the newest for each track or diagnostic', () => {
    const older = record({ id: 'e0', at: '2026-11-01T12:00:00.000Z' })
    const math = record({
      id: 'e2',
      subject: subjectOfDiagnostic('math'),
      kind: 'diagnostic',
    })
    const latest = latestBySubject([record(), older, math])
    expect(latest.get('python-foundations')?.id).toBe('e1')
    expect(latest.get('diagnostic.math')?.id).toBe('e2')
  })

  it('merges lists without repeating an event, oldest first', () => {
    const older = record({ id: 'e0', at: '2026-11-01T12:00:00.000Z' })
    expect(
      mergePlacements([record()], [older, record()]).map((each) => each.id),
    ).toEqual(['e0', 'e1'])
  })

  it('tells a diagnostic apart from a track', () => {
    expect(diagnosticOfSubject('diagnostic.math')).toBe('math')
    expect(diagnosticOfSubject('python-foundations')).toBeNull()
  })
})

describe('describing a placement in one line', () => {
  const day = dayOf('2026-11-09T12:00:00.000Z')

  it('says where to start in a track and how many topics to prove first', () => {
    expect(describeTrackRecord(record(), () => false)).toBe(
      `Placement on ${day}: start at Variables, with 2 topics to prove first.`,
    )
    // Once one of them is proven, it's no longer to prove.
    expect(
      describeTrackRecord(record(), (id) => id === 'py.programs-and-print'),
    ).toBe(
      `Placement on ${day}: start at Variables, with 1 topic to prove first.`,
    )
    expect(describeTrackRecord(record({ next: null }), () => true)).toBe(
      `Placement on ${day}: everything written so far looked familiar.`,
    )
  })

  it('says how far up the math ladder is solid', () => {
    const math = getDiagnostic('math')
    if (!math) throw new Error('the math diagnostic is bundled')
    const shaky = record({
      subject: 'diagnostic.math',
      kind: 'diagnostic',
      known: ['arithmetic', 'algebra'],
      next: 'functions',
    })
    expect(describeDiagnosticRecord(shaky, math)).toBe(
      `Placement on ${day}: solid through Algebra; refresh from Functions and graphs.`,
    )
    expect(
      describeDiagnosticRecord(
        record({ ...shaky, known: [], next: 'arithmetic' }),
        math,
      ),
    ).toBe(
      `Placement on ${day}: refresh from Arithmetic, fractions and percentages.`,
    )
    expect(
      describeDiagnosticRecord(
        record({ ...shaky, known: math.levels.map((l) => l.id), next: null }),
        math,
      ),
    ).toBe(`Placement on ${day}: every level looked solid.`)
  })
})
