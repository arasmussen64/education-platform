// The shapes of the content files, as the app sees them. They mirror
// tools/content_model.py, which is what checks them in CI.
import type { MDXContent } from 'mdx/types'

export type TopicStatus = 'planned' | 'draft' | 'ready'

export type Module = {
  id: string
  title: string
  topics: string[]
  checkpoint: string
  /**
   * A capstone: a bigger checkpoint that ends a stage. It comes after this
   * module's own checkpoint and builds on every module before it.
   */
  capstone?: string
}

export type Track = {
  id: string
  title: string
  summary: string
  /** Where the track comes in the app, lowest first. */
  order: number
  modules: Module[]
}

export type Resource = {
  title: string
  url: string
  type: 'video' | 'reading' | 'interactive'
  use: 'embed' | 'link'
  license: string
  start?: number
  end?: number
}

export type Explain = {
  prompt: string
  rubric: { id: string; required: boolean; description: string }[]
  model_answer: string
}

/** Something a topic teaches. Items name the skills they test (ADR-0011). */
export type Skill = { id: string; description: string }

/** A checkpoint's way through for a learner who's stuck (ADR-0012). */
export type Unstuck = {
  /** A solved project like the build, in a different story. */
  example?: string
  /** The build itself, in 3 or 4 partly written steps, with hints. */
  steps: string[]
  /** Fresh versions of the build: the same skills in different stories. */
  versions: string[]
}

export type Topic = {
  id: string
  kind: 'topic' | 'checkpoint'
  status: TopicStatus
  title: string
  summary: string
  prerequisites: string[]
  estimated_minutes: number
  rev: number
  objectives: string[]
  resources: Resource[]
  practice: string[]
  prove: { build?: string; debug?: string; explain?: Explain }
  review_pool: string[]
  skills: Skill[]
  /** Checkpoints only. */
  unstuck?: Unstuck
}

export type McqItem = {
  id: string
  type: 'mcq'
  rev: number
  prompt: string
  choices: string[]
  answer: number
  explanation: string
  skills: string[]
}

export type PredictOutputItem = {
  id: string
  type: 'predict_output'
  rev: number
  prompt: string
  code: string
  expected_output: string
  explanation: string
  skills: string[]
}

/** Scrambled lines of a program to put back in order (ADR-0016). */
export type ParsonsItem = {
  id: string
  type: 'parsons'
  rev: number
  prompt: string
  /** The program's lines in the right order, each with its indentation. */
  lines: string[]
  /** Lines that don't belong, mixed in with the real ones. */
  distractors: string[]
  explanation: string
  skills: string[]
}

export type RecallItem = McqItem | PredictOutputItem | ParsonsItem

export type Stage =
  'worked_example' | 'fill_in' | 'write' | 'build' | 'debug' | 'review_code'

export type Step = { label: string; lines: string; note: string }

export type Exercise = {
  id: string
  stage: Stage
  rev: number
  title: string
  prompt: string
  time_limit_ms: number
  hints: string[]
  steps: Step[]
  skills: string[]
  /**
   * Checkpoint builds and debugs: the skills each test checks, as
   * "topic/skill", by test name (ADR-0012). Empty for other exercises.
   */
  test_skills: Record<string, string[]>
  /** Empty for exercises that start from a blank file. */
  starter: string
  solution: string
  tests: string
}

/** A compiled lesson.mdx. Pass it the components its tags use. */
export type LessonComponent = MDXContent

/** Everything one topic page needs, loaded only when the page opens. */
export type TopicContent = {
  topic: Topic
  Lesson: LessonComponent | null
  recall: Record<string, RecallItem>
  exercises: Record<string, Exercise>
}
