// A small, complete topic for page and component tests. The real content has
// no finished topics yet, and tests shouldn't change when it does.
import type { MDXComponents } from 'mdx/types'
import type { ComponentType, ReactNode } from 'react'
import type {
  Exercise,
  McqItem,
  PredictOutputItem,
  Topic,
  TopicContent,
} from '../content/types.ts'

type Tag = ComponentType<{ children?: ReactNode; index?: number }>

/** Stands in for a compiled lesson.mdx that uses <Intro>, <Resource> and <Recap>. */
function FakeLesson({ components = {} }: { components?: MDXComponents }) {
  const Intro = components.Intro as Tag
  const Resource = components.Resource as Tag
  const Recap = components.Recap as Tag
  return (
    <>
      <Intro>
        <p>Watch how a program prints, one line at a time.</p>
      </Intro>
      <Resource index={0} />
      <Recap>
        <p>print() shows text in the output.</p>
      </Recap>
    </>
  )
}

export function fakeTopic(overrides: Partial<Topic> = {}): Topic {
  return {
    // A real topic ID, so it has a real place in the track (Module 1).
    id: 'py.values-and-types',
    kind: 'topic',
    status: 'ready',
    title: 'Values and types',
    summary: 'Tell ints, floats and strings apart.',
    prerequisites: ['py.programs-and-print'],
    estimated_minutes: 30,
    rev: 1,
    objectives: ['Use `type()` to check a value.'],
    resources: [
      {
        title: 'Python values, explained',
        url: 'https://www.youtube.com/watch?v=abc123',
        type: 'video',
        use: 'embed',
        start: 65,
        end: 190,
        license: 'CC BY 4.0',
      },
      {
        title: 'The Python tutorial: numbers',
        url: 'https://docs.python.org/3/tutorial/introduction.html',
        type: 'reading',
        use: 'link',
        license: 'PSF License',
      },
    ],
    practice: [
      'example-hello',
      'mcq-print',
      'predict-print',
      'fill-hello',
      'write-hello',
    ],
    prove: {
      build: 'build-hello',
      debug: 'debug-hello',
      explain: {
        prompt: 'Why is `"5"` different from `5`?',
        rubric: [
          { id: 'types', required: true, description: 'Different types.' },
        ],
        model_answer: 'SECRET MODEL ANSWER',
      },
    },
    review_pool: ['mcq-print'],
    skills: [{ id: 'print-text', description: 'Show text with print' }],
    ...overrides,
  }
}

export function fakeExercise(
  overrides: Partial<Exercise> & Pick<Exercise, 'id' | 'stage'>,
): Exercise {
  return {
    rev: 1,
    title: 'Say hello',
    prompt: 'Print `Hello!`',
    time_limit_ms: 5000,
    hints: [],
    steps: [],
    skills: ['print-text'],
    test_skills: {},
    starter: '',
    solution: 'print("Hello!")\n',
    tests: 'the tests',
    ...overrides,
  }
}

export const MCQ: McqItem = {
  id: 'mcq-print',
  type: 'mcq',
  rev: 1,
  prompt: 'What does `print("Hi")` show?',
  choices: ['Hi', '"Hi"', 'print'],
  answer: 0,
  explanation: 'print shows the text without quotes.',
  skills: ['print-text'],
}

export const PREDICT: PredictOutputItem = {
  id: 'predict-print',
  type: 'predict_output',
  rev: 1,
  prompt: 'Read the code carefully.',
  code: 'print("a")\nprint("b")\n',
  expected_output: 'a\nb\n',
  explanation: 'Each print starts a new line.',
  skills: ['print-text'],
}

export function fakeContent(topic = fakeTopic()): TopicContent {
  const exercises = [
    fakeExercise({
      id: 'example-hello',
      stage: 'worked_example',
      steps: [{ label: 'Print it', lines: '1', note: 'print shows text.' }],
    }),
    fakeExercise({ id: 'fill-hello', stage: 'fill_in', starter: 'print(...)' }),
    fakeExercise({ id: 'write-hello', stage: 'write' }),
    fakeExercise({ id: 'build-hello', stage: 'build', title: 'Greet' }),
    fakeExercise({
      id: 'debug-hello',
      stage: 'debug',
      title: 'Fix the greeting',
      starter: 'print("Helo!")',
    }),
  ]
  return {
    topic,
    Lesson: FakeLesson,
    // Copies, so a test that changes them can't affect another test.
    recall: {
      [MCQ.id]: { ...MCQ, skills: [...MCQ.skills] },
      [PREDICT.id]: { ...PREDICT, skills: [...PREDICT.skills] },
    },
    exercises: Object.fromEntries(exercises.map((item) => [item.id, item])),
  }
}

/** What each test of the fake checkpoint's builds and debug checks. */
const RECEIPT_TESTS = {
  test_total: ['py.arithmetic/operators'],
  test_format: ['py.strings-and-input/fstrings'],
}

/**
 * A small, complete checkpoint, with its way through for a learner who's
 * stuck (ADR-0012). Its ID is real, so it has a real place in the track.
 */
export function fakeCheckpointContent(): TopicContent {
  const topic = fakeTopic({
    id: 'py.m1.checkpoint',
    kind: 'checkpoint',
    title: 'Checkpoint 1: receipt calculator',
    summary: 'Read prices, then print a receipt.',
    prerequisites: ['py.arithmetic', 'py.strings-and-input'],
    estimated_minutes: 60,
    objectives: ['Print a formatted receipt.'],
    resources: [],
    practice: [],
    prove: {
      build: 'build-receipt',
      debug: 'debug-tickets',
      explain: {
        prompt: 'How does your receipt program work?',
        rubric: [{ id: 'parts', required: true, description: 'Each part.' }],
        model_answer: 'SECRET MODEL ANSWER',
      },
    },
    review_pool: [],
    skills: [],
    unstuck: {
      example: 'example-shop',
      steps: ['step-read', 'step-work', 'step-print'],
      versions: ['build-split', 'build-fuel'],
    },
  })
  const step = (id: string, title: string) =>
    fakeExercise({
      id,
      stage: 'fill_in',
      title,
      skills: [],
      starter: 'total = ...',
      hints: ['Look at the step before.'],
    })
  const build = (id: string, title: string) =>
    fakeExercise({
      id,
      stage: 'build',
      title,
      skills: [],
      test_skills: RECEIPT_TESTS,
    })
  const exercises = [
    build('build-receipt', 'Receipt'),
    fakeExercise({
      id: 'debug-tickets',
      stage: 'debug',
      title: 'Cinema tickets',
      skills: [],
      starter: 'print("Total: $", 7)',
      test_skills: RECEIPT_TESTS,
    }),
    fakeExercise({
      id: 'example-shop',
      stage: 'worked_example',
      title: 'A shop receipt',
      skills: [],
      steps: [{ label: 'Read the inputs', lines: '1', note: 'Ask first.' }],
    }),
    step('step-read', 'Read the inputs'),
    step('step-work', 'Work out the totals'),
    step('step-print', 'Print the receipt'),
    build('build-split', 'Split the bill'),
    build('build-fuel', 'Fuel for a trip'),
  ]
  return {
    topic,
    Lesson: null,
    recall: {},
    exercises: Object.fromEntries(exercises.map((item) => [item.id, item])),
  }
}
