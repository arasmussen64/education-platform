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

  it('reads topic files, filling in what outlines leave out', () => {
    const topic = getTopic('py.variables')
    expect(topic).toMatchObject({
      title: 'Variables',
      prerequisites: ['py.values-and-types'],
      practice: [],
      prove: {},
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

  it('loads everything a finished topic lists: lesson, questions and exercise code', async () => {
    const content = await loadTopicContent('py.programs-and-print')
    if (!content) throw new Error('py.programs-and-print should load')
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
    expect(content.exercises['debug-boarding']?.starter).toContain('Print(')
  })

  it('loads a topic with nothing written yet', async () => {
    const content = await loadTopicContent('py.variables')
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
