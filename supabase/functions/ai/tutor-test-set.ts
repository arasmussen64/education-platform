// The tutor test set (ADR-0015): conversations on real exercises, with what
// each reply must not contain. One file per exercise in tutor-test-set/,
// read together with the exercise's prompt, hints and solution from content/.
import { parse } from 'jsr:@std/yaml@^1'
import type { HintInput } from './tutor.ts'

export type TutorSample = {
  /** What this conversation tests, for whoever reviews a miss. */
  why: string
  /** True for the samples that try to get the answer out of the tutor. */
  asks_for_answer: boolean
  /** The learner's code at the time; may be empty. */
  code: string
  question: string
  /** Descriptions of the checks that failed on the latest Check, if any. */
  failing: string[]
  /** The tutor's earlier replies on this exercise, which decide the rung. */
  earlier: string[]
  /** Text the reply must not contain, compared without spaces or capitals. */
  must_not_contain: string[]
}

export type ExerciseSamples = {
  topicId: string
  exerciseId: string
  exercise: HintInput['exercise']
  samples: TutorSample[]
}

const here = new URL('./', import.meta.url)
const root = new URL('../../../', import.meta.url)

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

const isStringList = (value: unknown): value is string[] =>
  Array.isArray(value) && value.every((item) => typeof item === 'string')

function readSamples(file: string, value: unknown): TutorSample[] {
  if (!Array.isArray(value)) throw new Error(`${file}: samples must be a list`)
  return value.map((sample, index) => {
    const where = `${file}, sample ${index + 1}`
    if (!isRecord(sample) || typeof sample.why !== 'string') {
      throw new Error(`${where}: needs why`)
    }
    const lists = {
      failing: sample.failing ?? [],
      earlier: sample.earlier ?? [],
      must_not_contain: sample.must_not_contain ?? [],
    }
    for (const [name, list] of Object.entries(lists)) {
      if (!isStringList(list)) throw new Error(`${where}: ${name} must be a list of text`)
    }
    return {
      why: sample.why,
      asks_for_answer: sample.asks_for_answer === true,
      code: typeof sample.code === 'string' ? sample.code : '',
      question: typeof sample.question === 'string' ? sample.question : '',
      failing: lists.failing as string[],
      earlier: lists.earlier as string[],
      must_not_contain: lists.must_not_contain as string[],
    }
  })
}

async function readExercise(
  topicId: string,
  exerciseId: string,
): Promise<HintInput['exercise']> {
  const folder = new URL(
    `content/topics/${topicId}/exercises/${exerciseId}/`,
    root,
  )
  const meta = parse(
    await Deno.readTextFile(new URL('exercise.yaml', folder)),
  )
  if (
    !isRecord(meta) ||
    typeof meta.title !== 'string' ||
    typeof meta.prompt !== 'string'
  ) {
    throw new Error(`${topicId}/${exerciseId} has no title and prompt`)
  }
  return {
    title: meta.title,
    prompt: meta.prompt,
    hints: isStringList(meta.hints) ? meta.hints : [],
    solution: await Deno.readTextFile(new URL('solution.py', folder)),
  }
}

/** Every exercise's samples, in file-name order. */
export async function loadTutorTestSet(): Promise<ExerciseSamples[]> {
  const files: string[] = []
  for await (const entry of Deno.readDir(new URL('tutor-test-set/', here))) {
    if (entry.isFile && entry.name.endsWith('.yaml')) files.push(entry.name)
  }
  files.sort()
  return Promise.all(
    files.map(async (file) => {
      const doc = parse(
        await Deno.readTextFile(new URL(`tutor-test-set/${file}`, here)),
      )
      if (
        !isRecord(doc) ||
        typeof doc.topic !== 'string' ||
        typeof doc.exercise !== 'string'
      ) {
        throw new Error(`${file}: needs topic, exercise and samples`)
      }
      return {
        topicId: doc.topic,
        exerciseId: doc.exercise,
        exercise: await readExercise(doc.topic, doc.exercise),
        samples: readSamples(file, doc.samples),
      }
    }),
  )
}

/** What the proxy would be sent for one sample. */
export function sampleInput(
  set: ExerciseSamples,
  sample: TutorSample,
): HintInput {
  return {
    exercise: set.exercise,
    code: sample.code,
    check:
      sample.failing.length > 0
        ? {
            passed: 0,
            total: sample.failing.length,
            results: sample.failing.map((description) => ({
              description,
              outcome: 'fail' as const,
              message: '',
            })),
          }
        : null,
    question: sample.question,
    earlier: sample.earlier,
  }
}

const compact = (text: string) => text.replace(/\s+/g, '').toLowerCase()

/** The forbidden pieces of text that a reply contains. */
export function forbiddenIn(text: string, forbidden: string[]): string[] {
  const haystack = compact(text)
  return forbidden.filter((piece) => haystack.includes(compact(piece)))
}
