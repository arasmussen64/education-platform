import { moduleTopicIds } from '../progress/modules.ts'
import {
  getTopic,
  getTrack,
  placeOf,
  topicIdsOf,
  tracks,
  type Place,
} from './content.ts'
import type { Module, Topic, Track } from './types.ts'

// A track can build on another track's topics: Finance and Markets starts
// from Python Foundations' loops and the ML track's exponents. A learner who
// starts there shouldn't have to guess how much of the other track that
// means. These helpers work out exactly which topics, in an order to learn
// them, so the map can list them before the module that needs them and a
// locked topic can say where to start.

/** Where a topic sits across every track, for putting topics in course order. */
function positions(): Map<string, number> {
  const order = new Map<string, number>()
  for (const track of tracks()) {
    for (const id of topicIdsOf(track)) {
      if (!order.has(id)) order.set(id, order.size)
    }
  }
  return order
}

/**
 * Every topic the given ones build on, directly or further down, in an
 * order to learn them: each after its own prerequisites, and otherwise in
 * the order the tracks teach them. The given topics are left out, and so
 * is anything in `leaveOut`; topics behind them are still followed, so a
 * prerequisite of a left-out topic is still listed.
 */
export function prerequisitesInOrder(
  ids: string[],
  leaveOut: ReadonlySet<string> = new Set(),
): Topic[] {
  const found = new Map<string, Topic>()
  const stack = ids.flatMap((id) => getTopic(id)?.prerequisites ?? [])
  while (stack.length > 0) {
    const id = stack.pop()!
    if (found.has(id)) continue
    const topic = getTopic(id)
    if (!topic) continue
    found.set(id, topic)
    stack.push(...topic.prerequisites)
  }
  const given = new Set(ids)
  const wanted = [...found.values()].filter(
    (topic) => !given.has(topic.id) && !leaveOut.has(topic.id),
  )
  return inLearningOrder(wanted)
}

/**
 * Sorts topics so each comes after any of its prerequisites in the list,
 * and otherwise in course order: at each step, the earliest topic whose
 * listed prerequisites are all placed already.
 */
function inLearningOrder(topics: Topic[]): Topic[] {
  const order = positions()
  const at = (topic: Topic) => order.get(topic.id) ?? Number.MAX_SAFE_INTEGER
  const waiting = [...topics].sort((a, b) => at(a) - at(b))
  const inList = new Set(waiting.map((topic) => topic.id))
  const placed = new Set<string>()
  const sorted: Topic[] = []
  while (waiting.length > 0) {
    const index = waiting.findIndex((topic) =>
      topic.prerequisites.every((id) => !inList.has(id) || placed.has(id)),
    )
    // A cycle can't be learned in any order; keep course order for it.
    const [next] = waiting.splice(index === -1 ? 0 : index, 1)
    placed.add(next.id)
    sorted.push(next)
  }
  return sorted
}

/** A module's foundations: the topics from other tracks it builds on. */
export type ModuleFoundations = {
  module: Module
  /** In an order to learn them. Empty when the module needs nothing new. */
  topics: Topic[]
}

/**
 * For each of a track's modules, the other tracks' topics it builds on that
 * no earlier module of the track already listed. Module 1 lists everything
 * the track starts from; a later module lists only what it adds.
 */
export function trackFoundations(track: Track): ModuleFoundations[] {
  const own = new Set(topicIdsOf(track))
  const listed = new Set<string>()
  return track.modules.map((module) => {
    const ids = [
      ...moduleTopicIds(module),
      ...(module.capstone ? [module.capstone] : []),
    ]
    const topics = prerequisitesInOrder(ids, new Set([...own, ...listed]))
    for (const topic of topics) listed.add(topic.id)
    return { module, topics }
  })
}

/** The module of a track whose foundations list a topic, if one does. */
export function foundationsListing(
  track: Track,
  topicId: string,
): ModuleFoundations | undefined {
  return trackFoundations(track).find(({ topics }) =>
    topics.some((topic) => topic.id === topicId),
  )
}

/** A link to a foundation topic that remembers which track sent the learner. */
export function foundationLink(topicId: string, track: Track): string {
  return `/topic/${topicId}?for=${encodeURIComponent(track.id)}`
}

/** One module's foundations list, found by the ids a link carries. */
export type FoundationsScope = ModuleFoundations & {
  track: Track
  /** The module's number in its track, from 1. */
  number: number
}

/**
 * The foundations list of one module of a track, or undefined when there's
 * no such track or module, or the module builds on nothing from other
 * tracks (or its topics haven't been downloaded yet, for an outline track).
 */
export function findFoundations(
  trackId: string,
  moduleId: string,
): FoundationsScope | undefined {
  const track = getTrack(trackId)
  if (!track) return undefined
  const index = track.modules.findIndex((module) => module.id === moduleId)
  const found = trackFoundations(track)[index]
  if (!found || found.topics.length === 0) return undefined
  return { ...found, track, number: index + 1 }
}

/** "Before Module 1 of Finance and Markets": a list's name off the map. */
export function foundationsTitle(scope: FoundationsScope): string {
  return `Before Module ${scope.number} of ${scope.track.title}`
}

/**
 * A link to the placement test for one module's foundations list only
 * (ADR-0021's amendment of 2026-11-21). `for` is the track, as on a
 * foundation topic's link.
 */
export function foundationsPlacementLink(track: Track, module: Module): string {
  return `/placement?for=${encodeURIComponent(track.id)}&module=${encodeURIComponent(module.id)}`
}

/** A link to a module's foundations list on its track's map. */
export function foundationsMapLink(track: Track, module: Module): string {
  return `/map/${track.id}#${foundationsAnchor(module)}`
}

/** The id of a module's foundations list on the map, for links to it. */
export function foundationsAnchor(module: Module): string {
  return `foundations-${module.id}`
}

/** Foundations from one module of another track, as the map groups them. */
export type FoundationGroup = {
  place: Place
  topics: Topic[]
  /** Whether the group is that whole module, checkpoint included. */
  whole: boolean
}

/** Splits a list into runs from the same module, keeping its order. */
export function groupByModule(topics: Topic[]): FoundationGroup[] {
  const groups: FoundationGroup[] = []
  for (const topic of topics) {
    const place = placeOf(topic.id)
    if (!place) continue
    const last = groups.at(-1)
    if (last && last.place.module.id === place.module.id) {
      last.topics.push(topic)
    } else {
      groups.push({ place, topics: [topic], whole: false })
    }
  }
  for (const group of groups) {
    const ids = new Set(group.topics.map((topic) => topic.id))
    group.whole = moduleTopicIds(group.place.module).every((id) => ids.has(id))
  }
  return groups
}

/** "Module 3", "Modules 1 and 2", "Modules 1 to 4". */
function moduleRun(numbers: number[]): string {
  if (numbers.length === 1) return `Module ${numbers[0]}`
  if (numbers.length === 2) return `Modules ${numbers[0]} and ${numbers[1]}`
  return `Modules ${numbers[0]} to ${numbers.at(-1)}`
}

/** "a, b and c". */
function listOf(words: string[]): string {
  if (words.length < 2) return words.join('')
  return `${words.slice(0, -1).join(', ')} and ${words.at(-1)}`
}

/**
 * How much of each other track a list of foundations is, in a phrase per
 * track: "Python Foundations: Modules 1 to 4 in full, and 3 of the 7 topics
 * in Module 5". It answers "do I need the whole track first?" at a glance.
 */
export function describeSources(topics: Topic[]): string[] {
  const byTrack = new Map<string, { track: Track; groups: FoundationGroup[] }>()
  for (const group of groupByModule(topics)) {
    const entry = byTrack.get(group.place.track.id) ?? {
      track: group.place.track,
      groups: [],
    }
    // One entry per module, even if the order split it in two.
    const same = entry.groups.find(
      (each) => each.place.module.id === group.place.module.id,
    )
    if (same) {
      same.topics.push(...group.topics)
      const ids = new Set(same.topics.map((topic) => topic.id))
      same.whole = moduleTopicIds(same.place.module).every((id) => ids.has(id))
    } else {
      entry.groups.push({ ...group, topics: [...group.topics] })
    }
    byTrack.set(group.place.track.id, entry)
  }
  return [...byTrack.values()].map(({ track, groups }) => {
    const sorted = [...groups].sort((a, b) => a.place.number - b.place.number)
    const parts: string[] = []
    let run: number[] = []
    const endRun = () => {
      if (run.length > 0) parts.push(`${moduleRun(run)} in full`)
      run = []
    }
    for (const group of sorted) {
      if (
        group.whole &&
        (run.length === 0 || run.at(-1)! + 1 === group.place.number)
      ) {
        run.push(group.place.number)
        continue
      }
      endRun()
      if (group.whole) {
        run.push(group.place.number)
      } else {
        const size = moduleTopicIds(group.place.module).length
        const count = group.topics.length
        parts.push(
          `${count} of the ${size} topics in Module ${group.place.number}`,
        )
      }
    }
    endRun()
    return `${track.title}: ${listOf(parts)}`
  })
}

/** "about 45 minutes", "about 2 hours", "about 24 hours". */
export function aboutTime(topics: Topic[]): string {
  const minutes = topics.reduce(
    (total, topic) => total + topic.estimated_minutes,
    0,
  )
  if (minutes < 90) return `about ${minutes} minutes`
  return `about ${Math.round(minutes / 60)} hours`
}
