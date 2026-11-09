import { describe, expect, it } from 'vitest'
import {
  getTopic,
  getTrack,
  isOpen,
  loadTrackOf,
  loadTrackTopics,
  mainTrack,
  topicIdsOf,
  trackTopicsLoaded,
} from './content.ts'

// Vitest gives each test file a fresh copy of content.ts, so this file sees
// the app as it first loads: with the main track's outlines bundled in and
// the cloud track's not yet downloaded. Keep these tests in order; each
// builds on the one before.

const CLOUD = 'cloud-solutions-architect'

describe('topic outlines that load on demand', () => {
  it('bundles the main track in, and leaves an outline-only track out', () => {
    expect(trackTopicsLoaded(mainTrack().id)).toBe(true)
    expect(getTopic('py.variables')).toBeDefined()

    const cloud = getTrack(CLOUD)
    if (!cloud) throw new Error('the cloud track should exist')
    expect(trackTopicsLoaded(CLOUD)).toBe(false)
    for (const id of topicIdsOf(cloud)) {
      expect(getTopic(id), id).toBeUndefined()
    }
  })

  it("loads a track's outlines when asked, all of them, once", async () => {
    const first = loadTrackTopics(CLOUD)
    // Asking twice while it loads shares the one download.
    expect(loadTrackTopics(CLOUD)).toBe(first)
    await first

    const cloud = getTrack(CLOUD)
    if (!cloud) throw new Error('the cloud track should exist')
    expect(trackTopicsLoaded(CLOUD)).toBe(true)
    for (const id of topicIdsOf(cloud)) {
      expect(getTopic(id), id).toBeDefined()
    }
    expect(getTopic('csa.linux.shell')).toMatchObject({
      status: 'planned',
      practice: [],
    })
  })

  it("has nothing to do for a track bundled in, or a topic's track", async () => {
    await expect(loadTrackTopics(mainTrack().id)).resolves.toBeUndefined()
    await expect(loadTrackTopics('no-such-track')).resolves.toBeUndefined()
    await expect(loadTrackOf('csa.capstone-1')).resolves.toBeUndefined()
    await expect(loadTrackOf('py.nothing')).resolves.toBeUndefined()
  })

  // The Today page, the follow-ups and the interleaved questions only look at
  // the topics bundled in, so a lazy track must have nothing a learner could
  // open. When the cloud track gets its first ready topic, bundle it in (or
  // teach those pages to load it) and change this test.
  it('keeps every lazy track all outlines, so nothing open is missed', () => {
    const cloud = getTrack(CLOUD)
    if (!cloud) throw new Error('the cloud track should exist')
    for (const id of topicIdsOf(cloud)) {
      const topic = getTopic(id)
      expect(topic && isOpen(topic), id).toBe(false)
      expect(topic?.status, id).toBe('planned')
    }
  })
})
