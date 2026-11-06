import { describe, expect, it } from 'vitest'
import type { Attempt } from '../followups/followUps.ts'
import { chooseVersion } from './versions.ts'

const CHECKPOINT = 'py.m1.checkpoint'
const VERSIONS = ['build-split', 'build-fuel']

/** A Check of `item` at `time`. */
function tried(item: string, time: string, topic = CHECKPOINT): Attempt {
  return {
    id: `${item} ${time}`,
    type: 'code_check',
    topic_id: topic,
    item_id: item,
    correct: false,
    occurred_at: time,
  }
}

describe('chooseVersion', () => {
  it('offers a version never tried, in the order topic.yaml lists them', () => {
    expect(chooseVersion(CHECKPOINT, VERSIONS, [])).toBe('build-split')
    const history = [tried('build-split', '2026-11-06T10:00:00.000Z')]
    expect(chooseVersion(CHECKPOINT, VERSIONS, history)).toBe('build-fuel')
  })

  it('then the one tried longest ago', () => {
    const history = [
      tried('build-fuel', '2026-11-05T10:00:00.000Z'),
      tried('build-split', '2026-11-06T10:00:00.000Z'),
    ]
    expect(chooseVersion(CHECKPOINT, VERSIONS, history)).toBe('build-fuel')
  })

  it('looks only at the checkpoint itself', () => {
    const history = [
      tried('build-split', '2026-11-06T10:00:00.000Z', 'py.other-topic'),
    ]
    expect(chooseVersion(CHECKPOINT, VERSIONS, history)).toBe('build-split')
  })

  it('has nothing to offer without versions', () => {
    expect(chooseVersion(CHECKPOINT, [], [])).toBeNull()
  })
})
