import { describe, expect, it } from 'vitest'
import { loadTopicContent } from '../content/content.ts'
import { fakeLab } from '../test/fakeContent.tsx'
import { runsPrivileged } from './options.ts'

describe('runsPrivileged', () => {
  it('is true only for a lab that boots systemd', () => {
    // A lab with no `lab:` block, then the two values the block can hold.
    const plain = fakeLab({ id: 'build-report', stage: 'build' })
    const alsoPlain = { ...plain, lab: { init: 'none' } }
    const booted = { ...plain, lab: { init: 'systemd' } }
    expect(runsPrivileged(plain)).toBe(false)
    expect(runsPrivileged(alsoPlain)).toBe(false)
    expect(runsPrivileged(booted)).toBe(true)
  })

  // The page only knows what the loader hands it. These are real labs: one
  // topic whose labs boot systemd, one whose labs don't.
  it('reads the option from the real labs, as the page loads them', async () => {
    const services = await loadTopicContent('csa.linux.services')
    const scripting = await loadTopicContent('csa.linux.scripting')
    if (!services || !scripting) throw new Error('the lab topics are missing')
    const booted = Object.values(services.exercises)
    const plain = Object.values(scripting.exercises)
    expect(booted.length).toBeGreaterThan(0)
    expect(plain.length).toBeGreaterThan(0)
    expect(booted.every(runsPrivileged)).toBe(true)
    expect(plain.some(runsPrivileged)).toBe(false)
  })
})
