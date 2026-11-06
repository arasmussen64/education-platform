import type {
  Exercise,
  LessonComponent,
  Module,
  RecallItem,
  Topic,
  TopicContent,
  Track,
} from './types.ts'

// Vite finds the content files (../content) while building the app. Topic
// outlines and tracks are small, so they're bundled straight in; lessons,
// questions and exercises load only when their topic page opens.

const topicFiles = import.meta.glob<Partial<Topic>>(
  '../../../content/topics/*/topic.yaml',
  { eager: true, import: 'default' },
)
const trackFiles = import.meta.glob<Track>('../../../content/tracks/*.yaml', {
  eager: true,
  import: 'default',
})
const lessonFiles = import.meta.glob<LessonComponent>(
  '../../../content/topics/*/lesson.mdx',
  { import: 'default' },
)
const recallFiles = import.meta.glob<RecallItem>(
  '../../../content/topics/*/recall/*.yaml',
  { import: 'default' },
)
/** exercise.yaml: the code comes from its own files, and some fields have defaults. */
type Defaulted = 'time_limit_ms' | 'hints' | 'steps' | 'skills'
type ExerciseFile = Omit<
  Exercise,
  'starter' | 'solution' | 'tests' | Defaulted
> &
  Partial<Pick<Exercise, Defaulted>>
const exerciseFiles = import.meta.glob<ExerciseFile>(
  '../../../content/topics/*/exercises/*/exercise.yaml',
  { import: 'default' },
)
const codeFiles = import.meta.glob<string>(
  '../../../content/topics/*/exercises/*/{starter,solution,test_exercise}.py',
  { query: '?raw', import: 'default' },
)

/** Fills in the fields an outline may leave out. */
function withDefaults(raw: Partial<Topic>): Topic {
  return {
    prerequisites: [],
    resources: [],
    practice: [],
    prove: {},
    review_pool: [],
    skills: [],
    ...raw,
  } as Topic
}

const TOPICS = Object.values(topicFiles).map(withDefaults)
const TOPICS_BY_ID = new Map(TOPICS.map((topic) => [topic.id, topic]))
const [MAIN_TRACK] = Object.values(trackFiles)

/** The learning track (v1 has one: Python Foundations). */
export function mainTrack(): Track {
  if (!MAIN_TRACK) throw new Error('There is no track in content/tracks.')
  return MAIN_TRACK
}

/** The module a topic belongs to, and that module's number (1, 2, …). */
export function moduleFor(
  topicId: string,
): { module: Module; number: number } | undefined {
  for (const [index, module] of mainTrack().modules.entries()) {
    if (module.topics.includes(topicId) || module.checkpoint === topicId) {
      return { module, number: index + 1 }
    }
  }
  return undefined
}

export function getTopic(id: string): Topic | undefined {
  return TOPICS_BY_ID.get(id)
}

/**
 * Whether a topic's lesson and exercises can be opened. Learners see ready
 * topics; the dev server also shows drafts (marked as drafts) so they can be
 * tried while being written.
 */
export function isOpen(topic: Topic): boolean {
  return (
    topic.status === 'ready' ||
    (topic.status === 'draft' && Boolean(import.meta.env.DEV))
  )
}

function inTopic(path: string, topicId: string): boolean {
  return path.includes(`/topics/${topicId}/`)
}

/** Loads one topic's lesson, questions and exercises. */
export async function loadTopicContent(
  topicId: string,
): Promise<TopicContent | null> {
  const topic = getTopic(topicId)
  if (!topic) return null

  const lessonLoader = Object.entries(lessonFiles).find(([path]) =>
    inTopic(path, topicId),
  )?.[1]
  const Lesson = lessonLoader ? await lessonLoader() : null

  const recall: Record<string, RecallItem> = {}
  const recallLoads = Object.entries(recallFiles)
    .filter(([path]) => inTopic(path, topicId))
    .map(async ([, load]) => {
      const item = await load()
      recall[item.id] = { ...item, skills: item.skills ?? [] }
    })

  const exercises: Record<string, Exercise> = {}
  const exerciseLoads = Object.entries(exerciseFiles)
    .filter(([path]) => inTopic(path, topicId))
    .map(async ([path, load]) => {
      const folder = path.slice(0, path.lastIndexOf('/') + 1)
      const code = (name: string) =>
        codeFiles[`${folder}${name}`]?.() ?? Promise.resolve('')
      const [file, starter, solution, tests] = await Promise.all([
        load(),
        code('starter.py'),
        code('solution.py'),
        code('test_exercise.py'),
      ])
      exercises[file.id] = {
        time_limit_ms: 5000,
        hints: [],
        steps: [],
        skills: [],
        ...file,
        starter,
        solution,
        tests,
      }
    })

  await Promise.all([...recallLoads, ...exerciseLoads])
  return { topic, Lesson, recall, exercises }
}
