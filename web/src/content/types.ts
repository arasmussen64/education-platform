// The shapes of the content files, as the app sees them. They mirror
// tools/content_model.py, which is what checks them in CI.
import type { MDXContent } from 'mdx/types'

export type TopicStatus = 'planned' | 'draft' | 'ready'

export type Module = {
  id: string
  title: string
  topics: string[]
  checkpoint: string
}

export type Track = {
  id: string
  title: string
  summary: string
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
}

export type McqItem = {
  id: string
  type: 'mcq'
  rev: number
  prompt: string
  choices: string[]
  answer: number
  explanation: string
}

export type PredictOutputItem = {
  id: string
  type: 'predict_output'
  rev: number
  prompt: string
  code: string
  expected_output: string
  explanation: string
}

export type RecallItem = McqItem | PredictOutputItem

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
