import { describe, expect, it } from 'vitest'
import { recallPart, rememberPart } from './partMemory.ts'

describe('remembering a part', () => {
  it('recalls what was remembered, per topic', () => {
    rememberPart('csa.net.routing', 'practice-2')
    expect(recallPart('csa.net.routing')).toBe('practice-2')
    expect(recallPart('csa.net.nat')).toBeNull()
  })

  it('copes with storage that is missing or broken', () => {
    expect(recallPart('csa.net.routing', null)).toBeNull()
    const broken = {
      getItem: () => {
        throw new Error('blocked')
      },
      setItem: () => {
        throw new Error('blocked')
      },
    }
    expect(() => rememberPart('csa.net.routing', 'prove', broken)).not.toThrow()
    expect(recallPart('csa.net.routing', broken)).toBeNull()
  })
})
