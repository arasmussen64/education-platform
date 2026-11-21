import { describe, expect, it } from 'vitest'
import { getTrack, placeOf, topicIdsOf } from './content.ts'
import {
  describeSources,
  findFoundations,
  foundationsListing,
  foundationsMapLink,
  foundationsPlacementLink,
  foundationsTitle,
  groupByModule,
  prerequisitesInOrder,
  trackFoundations,
} from './foundations.ts'

// The real content: Finance and Markets builds on Python Foundations and
// the ML track's math, and Python Foundations builds on nothing.

const finance = getTrack('finance')!
const python = getTrack('python-foundations')!

describe('prerequisitesInOrder', () => {
  it('lists everything a topic builds on, each after its own prerequisites', () => {
    const order = prerequisitesInOrder(['fin.money.compounding'])
    const ids = order.map((topic) => topic.id)
    expect(ids).toContain('py.for-and-range')
    expect(ids).toContain('ml.math.exponents-and-logs')
    expect(ids).toContain('py.programs-and-print')
    expect(ids).not.toContain('fin.money.compounding')
    for (const [index, topic] of order.entries()) {
      for (const prerequisite of topic.prerequisites) {
        expect(ids.indexOf(prerequisite)).toBeLessThan(index)
      }
    }
  })

  it('keeps course order where the prerequisites allow it', () => {
    const ids = prerequisitesInOrder(['fin.money.compounding']).map(
      (topic) => topic.id,
    )
    // Python Foundations comes before the ML track, which builds on it.
    expect(ids[0]).toBe('py.programs-and-print')
    expect(ids.indexOf('py.for-and-range')).toBeLessThan(
      ids.indexOf('ml.math.arithmetic'),
    )
  })
})

describe('trackFoundations', () => {
  it("lists another track's topics above the module that first needs them", () => {
    const [first, ...rest] = trackFoundations(finance)
    const ids = first.topics.map((topic) => topic.id)
    expect(ids).toContain('py.for-and-range')
    expect(ids).toContain('ml.math.exponents-and-logs')
    // Only other tracks' topics, and none listed twice.
    const own = new Set(topicIdsOf(finance))
    expect(ids.some((id) => own.has(id))).toBe(false)
    const later = rest.flatMap((each) => each.topics.map((topic) => topic.id))
    expect(later.some((id) => ids.includes(id))).toBe(false)
  })

  it('lists nothing for a track that builds only on itself', () => {
    expect(
      trackFoundations(python).every((each) => each.topics.length === 0),
    ).toBe(true)
  })

  it('finds the module whose list holds a topic', () => {
    expect(foundationsListing(finance, 'py.variables')?.module.id).toBe(
      finance.modules[0].id,
    )
    expect(foundationsListing(finance, 'fin.money.compounding')).toBeUndefined()
  })
})

describe('one list, found from a link', () => {
  it('finds the list by its track and module, with its number', () => {
    const scope = findFoundations('finance', 'fin.m1')
    expect(scope?.track.id).toBe('finance')
    expect(scope?.number).toBe(1)
    expect(scope?.topics).toEqual(trackFoundations(finance)[0].topics)
    expect(scope && foundationsTitle(scope)).toBe(
      'Before Module 1 of Finance and Markets',
    )
  })

  it('finds nothing for a track, module or list that is not there', () => {
    expect(findFoundations('no-such-track', 'fin.m1')).toBeUndefined()
    expect(findFoundations('finance', 'no-such-module')).toBeUndefined()
    // A module of another track isn't this track's.
    expect(findFoundations('finance', 'ml.m1')).toBeUndefined()
    // Python Foundations builds on nothing else: no list to place in.
    expect(findFoundations(python.id, python.modules[0].id)).toBeUndefined()
  })

  it("links to the list's placement test and to the list on the map", () => {
    const module = finance.modules[0]
    expect(foundationsPlacementLink(finance, module)).toBe(
      '/placement?for=finance&module=fin.m1',
    )
    expect(foundationsMapLink(finance, module)).toBe(
      '/map/finance#foundations-fin.m1',
    )
  })
})

describe('describing the list', () => {
  const topics = trackFoundations(finance)[0].topics

  it('groups it by the module each topic comes from', () => {
    const groups = groupByModule(topics)
    expect(groups[0].place.track.id).toBe('python-foundations')
    expect(groups[0].place.number).toBe(1)
    // Python Foundations' Module 1 is needed whole, checkpoint and all.
    expect(groups[0].whole).toBe(true)
  })

  it('says how much of each track it is', () => {
    const lines = describeSources(topics)
    expect(lines).toHaveLength(2)
    expect(lines[0]).toMatch(/^Python Foundations: Modules 1 to \d in full/)
    expect(lines[1]).toMatch(
      /^Machine Learning Foundations: \d of the \d+ topics in Module 1$/,
    )
  })

  it('names only modules the list really comes from', () => {
    const modules = new Set(topics.map((topic) => placeOf(topic.id)?.module.id))
    expect(modules.has(python.modules.at(-1)!.id)).toBe(false)
  })
})
