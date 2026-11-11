import { describe, expect, it } from 'vitest'
import {
  getTopic,
  getTrack,
  loadTrackOf,
  loadTrackTopics,
  mainTrack,
  topicIdsOf,
  trackTopicsLoaded,
} from './content.ts'

// Vitest gives each test file a fresh copy of content.ts, so this file sees
// the app as it first loads: with the main track's outlines bundled in, the
// cloud track's Module 1 and its checkpoint bundled in too, and the rest of
// the cloud track not yet downloaded. Keep these tests in order; each builds
// on the one before.

const CLOUD = 'cloud-solutions-architect'
/** The cloud track's modules with real content, and their checkpoints, bundled into the app. */
const isBundled = (id: string) =>
  id.startsWith('csa.linux.') ||
  id === 'csa.m1.checkpoint' ||
  id.startsWith('csa.hw.') ||
  id === 'csa.m2.checkpoint'

describe('topic outlines that load on demand', () => {
  it('bundles the main track and the module being written, and leaves the outlines out', () => {
    expect(trackTopicsLoaded(mainTrack().id)).toBe(true)
    expect(getTopic('py.variables')).toBeDefined()

    const cloud = getTrack(CLOUD)
    if (!cloud) throw new Error('the cloud track should exist')
    expect(trackTopicsLoaded(CLOUD)).toBe(false)
    for (const id of topicIdsOf(cloud)) {
      if (isBundled(id)) expect(getTopic(id), id).toBeDefined()
      else expect(getTopic(id), id).toBeUndefined()
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
    // A Module 3 topic: planned for a long while yet.
    expect(getTopic('csa.net.cidr')).toMatchObject({
      status: 'planned',
      practice: [],
    })
    // The bundled module's first topic is ready, with its labs.
    expect(getTopic('csa.linux.shell')?.status).toBe('ready')
  })

  it("has nothing to do for a track bundled in, or a topic's track", async () => {
    await expect(loadTrackTopics(mainTrack().id)).resolves.toBeUndefined()
    await expect(loadTrackTopics('no-such-track')).resolves.toBeUndefined()
    await expect(loadTrackOf('csa.capstone-1')).resolves.toBeUndefined()
    await expect(loadTrackOf('py.nothing')).resolves.toBeUndefined()
  })

  // The Today page, the follow-ups and the interleaved questions only look at
  // the topics bundled in, so a topic that loads on demand must never be
  // ready. When another cloud module gets content, bundle it in too (the
  // bundledCloudFiles glob in content.ts, and its exclusion in outlines/).
  it('keeps every topic that loads on demand unready, so nothing open is missed', () => {
    const cloud = getTrack(CLOUD)
    if (!cloud) throw new Error('the cloud track should exist')
    for (const id of topicIdsOf(cloud)) {
      if (!isBundled(id)) expect(getTopic(id)?.status, id).not.toBe('ready')
    }
  })
})
