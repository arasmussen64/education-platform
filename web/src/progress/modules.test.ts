import { describe, expect, it } from 'vitest'
import type { Module } from '../content/types.ts'
import { countModule, describeModule, moduleTopicIds } from './modules.ts'
import type { TopicProgress } from './progress.ts'

const MODULE: Module = {
  id: 'm2',
  title: 'Linux',
  topics: ['a', 'b', 'c'],
  checkpoint: 'checkpoint',
  capstone: 'capstone',
}

/** A topic's progress, Learned at `learnedAt` or not at all. */
function entry(learnedAt: string | null): TopicProgress {
  return { started: true, passed: {}, learnedAt, reviews: [], card: null }
}

describe('countModule', () => {
  it("counts a module's proven topics and checkpoint, not its capstone", () => {
    expect(moduleTopicIds(MODULE)).toEqual(['a', 'b', 'c', 'checkpoint'])
    const progress = new Map([
      ['a', entry('2026-11-01T12:00:00.000Z')],
      ['b', entry(null)],
      ['capstone', entry('2026-11-02T12:00:00.000Z')],
    ])
    // "c" is still being written.
    expect(countModule(MODULE, progress, (id) => id !== 'c')).toEqual({
      proven: 1,
      open: 3,
      total: 4,
    })
  })
})

describe('describeModule', () => {
  it('counts down to the end of the module', () => {
    expect(describeModule(2, MODULE, { proven: 6, open: 8, total: 8 })).toBe(
      '6 of 8 topics proven in Module 2, Linux: 2 to go.',
    )
  })

  it('marks the start of a new module as a fresh start', () => {
    expect(describeModule(2, MODULE, { proven: 0, open: 8, total: 8 })).toBe(
      'A fresh start: Module 2, Linux, begins here, with 8 topics.',
    )
  })

  it('says how many topics are still being written', () => {
    expect(describeModule(2, MODULE, { proven: 3, open: 4, total: 5 })).toBe(
      '3 of 4 topics proven in Module 2, Linux: 1 to go. 1 more is still being written.',
    )
  })
})
