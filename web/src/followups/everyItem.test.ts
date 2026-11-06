import { describe, expect, it } from 'vitest'
import { getTopic, loadTopicContent, mainTrack } from '../content/content.ts'
import { STAGES } from '../content/stages.ts'
import {
  type Attempt,
  chooseQuestion,
  openFollowUps,
  skillsIn,
} from './followUps.ts'

// The promise behind ADR-0011, checked against the real content in
// content/: missing any question or exercise, in any ready topic, brings
// back a different question on every skill it tests. New topics are
// covered as soon as they're marked ready.

const readyTopics = mainTrack()
  .modules.flatMap((module) => [...module.topics, module.checkpoint])
  .filter((id) => getTopic(id)?.status === 'ready')

const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()

describe.each(readyTopics)('%s', (topicId) => {
  it('brings any missed item back as different questions on its skills', async () => {
    const content = await loadTopicContent(topicId)
    if (!content) throw new Error(`${topicId} should load`)
    const contents = new Map([[topicId, content]])
    const graded = [
      ...Object.values(content.recall),
      ...Object.values(content.exercises).filter(
        (exercise) => exercise.stage !== 'worked_example',
      ),
    ]
    expect(graded.length).toBeGreaterThan(0)

    for (const item of graded) {
      const missed: Attempt = {
        id: `missed-${item.id}`,
        type: 'stage' in item ? 'code_check' : 'answer',
        topic_id: topicId,
        item_id: item.id,
        correct: false,
        occurred_at: yesterday,
      }
      const open = openFollowUps([missed], skillsIn(contents))
      expect(
        open.map((followUp) => followUp.skillId).sort(),
        `${item.id} opens a follow-up for each of its skills`,
      ).toEqual([...item.skills].sort())

      for (const followUp of open) {
        const question = chooseQuestion(followUp, content, [missed])
        const where = `${item.id}, skill ${followUp.skillId}`
        expect(question, `${where}: a different question`).not.toBe(item.id)
        const exercise = question ? content.exercises[question] : undefined
        const chosen = question
          ? (content.recall[question] ?? exercise)
          : undefined
        expect(chosen?.skills, `${where}: tests the same skill`).toContain(
          followUp.skillId,
        )
        if (exercise) {
          expect(STAGES[exercise.stage].followUp, `${where}: not a proof`).toBe(
            true,
          )
        }
      }
    }
  })
})
