import { describe, expect, it } from 'vitest'
import {
  getTopic,
  isOpen,
  loadTopicContent,
  mainTrack,
  moduleFor,
} from './content.ts'
import type { Topic } from './types.ts'

// These read the real files in content/, through the same Vite plugins the
// app uses.

describe('the content the app loads', () => {
  it('has the Python Foundations track, with every topic in it', () => {
    const track = mainTrack()
    expect(track.id).toBe('python-foundations')
    expect(track.modules).toHaveLength(6)
    const ids = track.modules.flatMap((module) => [
      ...module.topics,
      module.checkpoint,
    ])
    expect(ids).toHaveLength(36)
    for (const id of ids) {
      expect(getTopic(id), id).toBeDefined()
    }
  })

  it('reads topic files', () => {
    expect(getTopic('py.variables')).toMatchObject({
      title: 'Variables',
      prerequisites: ['py.values-and-types'],
    })
  })

  // Whichever topic is still only an outline, so these keep working as
  // topics get written.
  const outline = mainTrack()
    .modules.flatMap((module) => [...module.topics, module.checkpoint])
    .map((id) => getTopic(id))
    .find((topic) => topic?.status === 'planned')

  it('fills in what outlines leave out', () => {
    expect(outline).toMatchObject({
      practice: [],
      prove: {},
      review_pool: [],
      skills: [],
    })
  })

  it('knows which module each topic is in', () => {
    expect(moduleFor('py.variables')).toMatchObject({
      number: 1,
      module: { title: 'First programs' },
    })
    expect(moduleFor('py.m2.checkpoint')?.number).toBe(2)
    expect(moduleFor('py.nothing')).toBeUndefined()
  })

  // Every ready topic and checkpoint, so each new one is checked as soon as
  // it's added.
  const isReady = (id: string) => getTopic(id)?.status === 'ready'
  const readyTopics = mainTrack()
    .modules.flatMap((module) => module.topics)
    .filter(isReady)
  const readyCheckpoints = mainTrack()
    .modules.map((module) => module.checkpoint)
    .filter(isReady)

  it('has at least one ready topic', () => {
    expect(readyTopics.length).toBeGreaterThan(0)
  })

  it.each(readyTopics)(
    'loads everything %s lists: lesson, questions and exercise code',
    async (topicId) => {
      const content = await loadTopicContent(topicId)
      if (!content) throw new Error(`${topicId} should load`)
      // The lesson is MDX compiled into a component.
      expect(content.Lesson).toBeTypeOf('function')

      const { practice, prove, review_pool } = content.topic
      const listed = [...practice, ...review_pool, prove.build, prove.debug]
      for (const id of listed) {
        if (!id) continue
        expect(content.recall[id] ?? content.exercises[id], id).toBeDefined()
      }
      for (const exercise of Object.values(content.exercises)) {
        expect(exercise.solution, exercise.id).not.toBe('')
        expect(exercise.tests, exercise.id).toContain('def test_')
      }
      // Skills, so a missed question can come back as another (ADR-0011).
      expect(content.topic.skills.length).toBeGreaterThan(0)
    },
  )

  it.each(readyCheckpoints)(
    'loads everything %s lists, including its way through',
    async (checkpointId) => {
      const content = await loadTopicContent(checkpointId)
      if (!content) throw new Error(`${checkpointId} should load`)
      // No lesson: a checkpoint brings a module's topics together.
      expect(content.Lesson).toBeNull()

      const { prove, unstuck } = content.topic
      expect(unstuck?.versions.length).toBeGreaterThanOrEqual(2)
      const proofs = [prove.build, prove.debug, ...(unstuck?.versions ?? [])]
      const listed = [unstuck?.example, ...(unstuck?.steps ?? []), ...proofs]
      for (const id of listed) {
        expect(content.exercises[id ?? '']?.solution, id).toBeTruthy()
      }
      // Every proof test names the skills it checks (ADR-0012).
      for (const id of proofs) {
        const tests = content.exercises[id ?? '']?.test_skills ?? {}
        expect(Object.keys(tests).length, id).toBeGreaterThan(0)
      }
    },
  )

  it('loads starter code and skills for exercises and questions', async () => {
    const content = await loadTopicContent('py.programs-and-print')
    expect(content?.exercises['debug-boarding']?.starter).toContain('Print(')
    expect(content?.recall['review-mcq-commas']?.skills).toEqual([
      'print-commas',
    ])
  })

  it('loads a topic with nothing written yet', async () => {
    if (!outline) throw new Error('every topic is written: drop this test')
    const content = await loadTopicContent(outline.id)
    expect(content).toMatchObject({ Lesson: null, recall: {}, exercises: {} })
    expect(await loadTopicContent('py.nothing')).toBeNull()
  })
})

describe('isOpen', () => {
  const topic = (status: Topic['status']) =>
    ({ ...getTopic('py.variables'), status }) as Topic

  it('opens ready topics, and drafts on the dev server', () => {
    expect(isOpen(topic('ready'))).toBe(true)
    // Tests run like the dev server.
    expect(isOpen(topic('draft'))).toBe(import.meta.env.DEV)
    expect(isOpen(topic('planned'))).toBe(false)
  })
})
