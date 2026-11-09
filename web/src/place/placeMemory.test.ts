import { describe, expect, it } from 'vitest'
import { recallPlace, rememberPlace } from './placeMemory.ts'

describe('remembering a place', () => {
  it('recalls what was remembered, per topic', () => {
    rememberPlace('py.variables', 'place-item-py.variables-fill-swap')
    expect(recallPlace('py.variables')).toBe(
      'place-item-py.variables-fill-swap',
    )
    expect(recallPlace('py.loops')).toBeNull()
  })

  it('copes with storage that is missing or broken', () => {
    expect(recallPlace('py.variables', null)).toBeNull()
    const broken = {
      getItem: () => {
        throw new Error('blocked')
      },
      setItem: () => {
        throw new Error('blocked')
      },
    }
    expect(() =>
      rememberPlace('py.variables', 'place-recap', broken),
    ).not.toThrow()
    expect(recallPlace('py.variables', broken)).toBeNull()
  })
})
