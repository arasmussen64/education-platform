// The grading test set (ADR-0013): sample explanations whose verdicts are
// known, one file per topic in test-set/, read together with each topic's
// explain check from content/.
import { parse } from 'jsr:@std/yaml@^1'
import type { GradeInput } from './grading.ts'

export type Sample = {
  expect: 'pass' | 'needs_work'
  /** Why it should get that verdict, for whoever reviews a miss. */
  why: string
  text: string
}

/** A topic's explain check: everything the grader gets but the explanation. */
export type ExplainCheck = Omit<GradeInput, 'explanation'>

export type TopicSamples = {
  topicId: string
  explain: ExplainCheck
  samples: Sample[]
}

const here = new URL('./', import.meta.url)
const root = new URL('../../../', import.meta.url)

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

function readSamples(file: string, value: unknown): Sample[] {
  if (!Array.isArray(value)) throw new Error(`${file}: expected a list`)
  return value.map((sample, index) => {
    if (
      !isRecord(sample) ||
      (sample.expect !== 'pass' && sample.expect !== 'needs_work') ||
      typeof sample.why !== 'string' ||
      typeof sample.text !== 'string' ||
      sample.text.trim() === ''
    ) {
      throw new Error(`${file}, sample ${index + 1}: needs expect, why and text`)
    }
    return { expect: sample.expect, why: sample.why, text: sample.text }
  })
}

function readExplain(topicId: string, value: unknown): ExplainCheck {
  const explain =
    isRecord(value) && isRecord(value.prove) ? value.prove.explain : undefined
  if (
    !isRecord(explain) ||
    typeof explain.prompt !== 'string' ||
    typeof explain.model_answer !== 'string' ||
    !Array.isArray(explain.rubric)
  ) {
    throw new Error(`${topicId} has no explain check in content/`)
  }
  return {
    prompt: explain.prompt,
    model_answer: explain.model_answer,
    rubric: explain.rubric.map((item) => ({
      id: String(item.id),
      required: item.required === true,
      description: String(item.description),
    })),
  }
}

/** Every topic's samples, in file-name order. */
export async function loadTestSet(): Promise<TopicSamples[]> {
  const files: string[] = []
  for await (const entry of Deno.readDir(new URL('test-set/', here))) {
    if (entry.isFile && entry.name.endsWith('.yaml')) files.push(entry.name)
  }
  files.sort()
  return Promise.all(
    files.map(async (file) => {
      const topicId = file.replace(/\.yaml$/, '')
      const samples = parse(
        await Deno.readTextFile(new URL(`test-set/${file}`, here)),
      )
      const topic = parse(
        await Deno.readTextFile(
          new URL(`content/topics/${topicId}/topic.yaml`, root),
        ),
      )
      return {
        topicId,
        explain: readExplain(topicId, topic),
        samples: readSamples(file, samples),
      }
    }),
  )
}
