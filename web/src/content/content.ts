import type {
  Exercise,
  LessonComponent,
  Module,
  RecallItem,
  Topic,
  TopicContent,
  Track,
  Unstuck,
} from './types.ts'

// Vite finds the content files (../content) while building the app. Tracks
// and the topic outlines of the main track are small, so they're bundled
// straight in; lessons, questions and exercises load only when their topic
// page opens.
//
// A track that is still all outlines (the cloud track: hundreds of topics
// nobody can open yet) would make the first download heavier for everyone,
// so its outlines are left out here and load as one piece when the map
// shows that track or one of its topics opens (LAZY_TRACKS, below).

const topicFiles = import.meta.glob<Partial<Topic>>(
  [
    '../../../content/topics/*/topic.yaml',
    '!../../../content/topics/csa.*/topic.yaml',
  ],
  { eager: true, import: 'default' },
)

/**
 * Outline-only tracks, by id, each with the module that holds its outlines.
 * To add one: a module like outlines/cloud-solutions-architect.ts, its
 * pattern left out of topicFiles above, and a line here. A lazy track must
 * have no open topic, because the Today page and the follow-ups only look
 * at the topics bundled in (content.lazy.test.ts checks this).
 */
const LAZY_TRACKS: Record<
  string,
  () => Promise<{ default: Partial<Topic>[] }>
> = {
  'cloud-solutions-architect': () =>
    import('./outlines/cloud-solutions-architect.ts'),
}
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
type Defaulted = 'time_limit_ms' | 'hints' | 'steps' | 'skills' | 'test_skills'
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
  const topic = {
    prerequisites: [],
    resources: [],
    practice: [],
    prove: {},
    review_pool: [],
    skills: [],
    ...raw,
  } as Topic
  // A checkpoint being written may leave out parts of its way through.
  const unstuck: Partial<Unstuck> | undefined = raw.unstuck
  if (unstuck) topic.unstuck = { steps: [], versions: [], ...unstuck }
  return topic
}

const TOPICS = Object.values(topicFiles).map(withDefaults)
// The topics bundled in, plus those of any lazy track that has been loaded.
const TOPICS_BY_ID = new Map(TOPICS.map((topic) => [topic.id, topic]))
const TRACKS = Object.values(trackFiles).sort((a, b) => a.order - b.order)

// One download per lazy track, shared by everything that asks for it.
const trackLoads = new Map<string, Promise<void>>()

/**
 * Makes a track's topics available to getTopic. Tracks bundled in are ready
 * at once; a lazy track's outlines download the first time, and a failed
 * download is tried again on the next call.
 */
export function loadTrackTopics(trackId: string): Promise<void> {
  const load = LAZY_TRACKS[trackId]
  if (!load) return Promise.resolve()
  let loading = trackLoads.get(trackId)
  if (!loading) {
    loading = load()
      .then((module) => {
        for (const topic of module.default.map(withDefaults)) {
          TOPICS_BY_ID.set(topic.id, topic)
        }
      })
      .catch((error: unknown) => {
        trackLoads.delete(trackId)
        throw error
      })
    trackLoads.set(trackId, loading)
  }
  return loading
}

/** Whether getTopic can already find a track's topics. */
export function trackTopicsLoaded(trackId: string): boolean {
  if (!LAZY_TRACKS[trackId]) return true
  return topicIdsOf(getTrack(trackId) ?? { modules: [] }).every((id) =>
    TOPICS_BY_ID.has(id),
  )
}

/** Loads the outlines of the track a topic belongs to, if they aren't here yet. */
export async function loadTrackOf(topicId: string): Promise<void> {
  const place = placeOf(topicId)
  if (place) await loadTrackTopics(place.track.id)
}

/** Every learning track, in the order they're shown. */
export function tracks(): Track[] {
  if (TRACKS.length === 0) {
    throw new Error('There is no track in content/tracks.')
  }
  return TRACKS
}

/** The first track, which the map opens on: Python Foundations. */
export function mainTrack(): Track {
  return tracks()[0]
}

export function getTrack(id: string): Track | undefined {
  return TRACKS.find((track) => track.id === id)
}

/** Every topic, checkpoint and capstone in a track, in the track's order. */
export function topicIdsOf(track: Pick<Track, 'modules'>): string[] {
  return track.modules.flatMap((module) => [
    ...module.topics,
    module.checkpoint,
    ...(module.capstone ? [module.capstone] : []),
  ])
}

/** Where a topic sits: its track, its module, and that module's number. */
export type Place = {
  track: Track
  module: Module
  /** 1, 2, … */
  number: number
  /** A capstone comes after its module's own checkpoint. */
  role: 'topic' | 'checkpoint' | 'capstone'
}

/** Finds a topic's place in the given tracks. The app uses placeOf. */
export function placeIn(tracks: Track[], topicId: string): Place | undefined {
  for (const track of tracks) {
    for (const [index, module] of track.modules.entries()) {
      const place = { track, module, number: index + 1 }
      if (module.topics.includes(topicId)) return { ...place, role: 'topic' }
      if (module.checkpoint === topicId) {
        return { ...place, role: 'checkpoint' }
      }
      if (module.capstone === topicId) return { ...place, role: 'capstone' }
    }
  }
  return undefined
}

export function placeOf(topicId: string): Place | undefined {
  return placeIn(tracks(), topicId)
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

/** Fills in the fields a question file may leave out. */
function withRecallDefaults(item: RecallItem): RecallItem {
  const skills = item.skills ?? []
  if (item.type === 'parsons') {
    return { ...item, skills, distractors: item.distractors ?? [] }
  }
  if (item.type === 'predict_shell') {
    return { ...item, skills, files: item.files ?? {} }
  }
  return { ...item, skills }
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
      recall[item.id] = withRecallDefaults(item)
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
        test_skills: {},
        ...file,
        starter,
        solution,
        tests,
      }
    })

  await Promise.all([...recallLoads, ...exerciseLoads])
  return { topic, Lesson, recall, exercises }
}
