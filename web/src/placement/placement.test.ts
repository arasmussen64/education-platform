import { describe, expect, it } from 'vitest'
import {
  afterProbe,
  chooseProbeItems,
  nextProbe,
  probesNeeded,
  shuffle,
  startWalk,
  summarize,
  verdict,
  type Walk,
} from './placement.ts'

/** Runs a whole walk over `count` items, where the first `known` are known. */
function walkWith(
  count: number,
  known: number,
): { walk: Walk; probes: number[] } {
  let walk = startWalk(count)
  const probes: number[] = []
  for (let index = nextProbe(walk); index !== null; index = nextProbe(walk)) {
    probes.push(index)
    walk = afterProbe(walk, index, index < known)
  }
  return { walk, probes }
}

describe('the walk', () => {
  it('finds where the known prefix ends, whatever its length', () => {
    for (let known = 0; known <= 30; known++) {
      const { walk, probes } = walkWith(30, known)
      expect(walk.lo, `known = ${known}`).toBe(known)
      expect(walk.hi).toBe(known)
      expect(probes.length).toBeLessThanOrEqual(probesNeeded(30))
    }
  })

  it('takes about five probes for thirty topics', () => {
    expect(probesNeeded(30)).toBe(5)
    expect(probesNeeded(1)).toBe(1)
    expect(probesNeeded(0)).toBe(0)
  })

  it('has nothing to probe in an empty order', () => {
    expect(nextProbe(startWalk(0))).toBeNull()
  })

  it('starts in the middle', () => {
    expect(nextProbe(startWalk(30))).toBe(15)
    expect(nextProbe(startWalk(1))).toBe(0)
  })
})

describe('a probe’s verdict', () => {
  it('decides as soon as a majority of the three is in', () => {
    expect(verdict([], 3)).toBe('open')
    expect(verdict([true], 3)).toBe('open')
    expect(verdict([true, true], 3)).toBe('pass')
    expect(verdict([false, false], 3)).toBe('fail')
    expect(verdict([true, false], 3)).toBe('open')
    expect(verdict([true, false, true], 3)).toBe('pass')
    expect(verdict([true, false, false], 3)).toBe('fail')
  })

  it('needs both of two, and the one of one', () => {
    expect(verdict([true], 2)).toBe('open')
    expect(verdict([true, true], 2)).toBe('pass')
    expect(verdict([false], 2)).toBe('fail')
    expect(verdict([true], 1)).toBe('pass')
    expect(verdict([false], 1)).toBe('fail')
  })
})

describe('choosing a probe’s questions', () => {
  const kinds: Record<string, 'choice' | 'other'> = {
    'mcq-1': 'choice',
    'mcq-2': 'choice',
    'mcq-3': 'choice',
    'mcq-4': 'choice',
    'predict-1': 'other',
  }
  const kindOf = (id: string) => kinds[id] ?? 'choice'
  // A "random" that never shuffles: Math.floor(0 * n) = 0 swaps with the first.
  const still = () => 0

  it('asks three, including one that is not multiple choice', () => {
    const chosen = chooseProbeItems(
      ['mcq-1', 'mcq-2', 'mcq-3', 'mcq-4', 'predict-1'],
      kindOf,
      still,
    )
    expect(chosen).toHaveLength(3)
    expect(chosen.some((id) => kindOf(id) === 'other')).toBe(true)
    expect(new Set(chosen).size).toBe(3)
  })

  it('asks the whole pool when it is small', () => {
    expect(chooseProbeItems(['mcq-1', 'mcq-2'], kindOf, still).sort()).toEqual([
      'mcq-1',
      'mcq-2',
    ])
  })

  it('shuffles without losing or repeating anything', () => {
    let seed = 7
    const random = () => {
      seed = (seed * 9301 + 49297) % 233280
      return seed / 233280
    }
    const shuffled = shuffle(['a', 'b', 'c', 'd', 'e'], random)
    expect([...shuffled].sort()).toEqual(['a', 'b', 'c', 'd', 'e'])
  })
})

describe('the result', () => {
  it('names the known prefix and where to start', () => {
    const order = ['a', 'b', 'c', 'd']
    const result = summarize(order, { lo: 2, hi: 2 }, [
      {
        id: 'b',
        passed: true,
        asked: [
          { item: 'q1', correct: true },
          { item: 'q2', correct: true },
        ],
      },
      {
        id: 'c',
        passed: false,
        asked: [
          { item: 'q3', correct: false },
          { item: 'q4', correct: true },
          { item: 'q5', correct: false },
        ],
      },
    ])
    expect(result.known).toEqual(['a', 'b'])
    expect(result.next).toBe('c')
    expect(result.asked).toBe(5)
    expect(result.correct).toBe(3)
  })

  it('says there is nothing left when everything is known', () => {
    const result = summarize(['a', 'b'], { lo: 2, hi: 2 }, [])
    expect(result.known).toEqual(['a', 'b'])
    expect(result.next).toBeNull()
  })

  it('starts at the beginning when nothing is known', () => {
    const result = summarize(['a', 'b'], { lo: 0, hi: 0 }, [])
    expect(result.known).toEqual([])
    expect(result.next).toBe('a')
  })
})
