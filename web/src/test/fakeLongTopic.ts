// A long topic, like the cloud track's four- and five-hour ones, for tests
// of a topic in parts (ADR-0025): a worked example lab, 24 quick questions,
// a fill-in and a write lab, one more question, and lab proofs.
import type { TopicContent } from '../content/types.ts'
import { fakeContent, fakeLab, fakeTopic, MCQ } from './fakeContent.tsx'

/** The quick questions' ids: q-1 to q-25. */
export const LONG_QUESTIONS = Array.from(
  { length: 25 },
  (_, index) => `q-${index + 1}`,
)

export function fakeLongContent(): TopicContent {
  const topic = fakeTopic({
    estimated_minutes: 300,
    practice: [
      'example-lab',
      ...LONG_QUESTIONS.slice(0, 24),
      'fill-lab',
      'write-lab',
      LONG_QUESTIONS[24]!,
    ],
    prove: { ...fakeTopic().prove, build: 'build-lab', debug: 'debug-lab' },
  })
  const base = fakeContent(topic)
  const labs = [
    fakeLab({ id: 'example-lab', stage: 'worked_example', title: 'Watch' }),
    fakeLab({ id: 'fill-lab', stage: 'fill_in', title: 'Finish it' }),
    fakeLab({ id: 'write-lab', stage: 'write', title: 'Make it' }),
    fakeLab({ id: 'build-lab', stage: 'build', title: 'Build the lot' }),
    fakeLab({ id: 'debug-lab', stage: 'debug', title: 'Mend it' }),
  ]
  return {
    ...base,
    recall: Object.fromEntries(
      LONG_QUESTIONS.map((id) => [id, { ...MCQ, id, skills: [...MCQ.skills] }]),
    ),
    exercises: Object.fromEntries(labs.map((lab) => [lab.id, lab])),
  }
}
