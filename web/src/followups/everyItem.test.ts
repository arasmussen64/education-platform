import { describe, expect, it } from 'vitest'
import {
  getTopic,
  loadTopicContent,
  topicIdsOf,
  tracks,
} from '../content/content.ts'
import { STAGES } from '../content/stages.ts'
import type { TopicContent } from '../content/types.ts'
import {
  type Attempt,
  chooseQuestion,
  openFollowUps,
  skillsIn,
  testSkillsIn,
  topicsNamedByTests,
} from './followUps.ts'

// The promise behind ADR-0011, checked against the real content in
// content/: missing any question or exercise, in any ready topic, brings
// back a different question on every skill it tests. New topics are
// covered as soon as they're marked ready.

const readyTopics = tracks()
  .flatMap(topicIdsOf)
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

// The promise behind ADR-0012: a failed test in a ready checkpoint's builds
// or debug brings back each skill it names, as a question from that skill's
// own topic. New checkpoints are covered as soon as they're marked ready.

const readyCheckpoints = readyTopics.filter(
  (id) => getTopic(id)?.kind === 'checkpoint',
)

describe('ready checkpoints', () => {
  // Loads every ready checkpoint and every topic its tests name, which takes
  // longer than the default 5 s on a busy machine.
  it(
    "bring back each failed test's skills as questions from their topics",
    { timeout: 20_000 },
    async () => {
      for (const checkpointId of readyCheckpoints) {
        const checkpoint = await loadTopicContent(checkpointId)
        if (!checkpoint) throw new Error(`${checkpointId} should load`)
        const contents = new Map<string, TopicContent>([
          [checkpointId, checkpoint],
        ])
        for (const topicId of topicsNamedByTests(contents)) {
          const content = await loadTopicContent(topicId)
          if (content) contents.set(topicId, content)
        }

        const { prove, unstuck } = checkpoint.topic
        for (const itemId of [
          prove.build,
          prove.debug,
          ...(unstuck?.versions ?? []),
        ]) {
          const exercise = itemId ? checkpoint.exercises[itemId] : undefined
          if (!itemId || !exercise)
            throw new Error(`${checkpointId}: ${itemId}`)
          for (const [test, refs] of Object.entries(exercise.test_skills)) {
            const failed: Attempt = {
              id: `failed-${itemId}-${test}`,
              type: 'code_check',
              topic_id: checkpointId,
              item_id: itemId,
              correct: false,
              occurred_at: yesterday,
              failing: [test],
            }
            const where = `${checkpointId} ${itemId} ${test}`
            const open = openFollowUps(
              [failed],
              skillsIn(contents),
              testSkillsIn(contents),
            )
            expect(
              open.map((followUp) => `${followUp.topicId}/${followUp.skillId}`),
              `${where} opens a follow-up for each skill it names`,
            ).toEqual([...refs].sort())

            for (const followUp of open) {
              const content = contents.get(followUp.topicId)
              const question = content
                ? chooseQuestion(followUp, content, [failed])
                : null
              const chosen = question
                ? (content?.recall[question] ?? content?.exercises[question])
                : undefined
              expect(
                chosen?.skills,
                `${where}: a question on the skill`,
              ).toContain(followUp.skillId)
            }
          }
        }
      }
    },
  )
})
