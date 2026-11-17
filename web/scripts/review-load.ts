// How many reviews a day a learner going through the Cloud Solutions
// Architect track's Modules 1 to 3 would face, with and without implicit
// repetition (ADR-0009, amended 2026-11-16). A simulation, not a promise:
// it uses the real topic graph and the app's own scheduler, and a simple
// made-up learner.
//
// Usage, from web/:   npm run sim:reviews
//                     npm run sim:reviews -- 120          (minutes a day)
//                     npm run sim:reviews -- 60 31 1500   (and modules, days)
//
// Modules past 3 are outlines (status: planned) with their prerequisites
// and estimated minutes; the simulation gives each topic a build and a
// debug, as every written topic has.
//
// The learner:
// - studies new topics for a fixed number of minutes a day, in track order,
//   each taking its estimated_minutes; finishing one passes its build and
//   debug that day (implicit credit for what it builds on) and makes it
//   Learned; a checkpoint passes its build the same way and has no card;
// - does every review that's due, most forgotten first, up to 20 a day;
// - answers each of a review's two items right with the chance the card
//   predicts (its retrievability), so both right is Good, one Hard, none
//   Again.
//
// Two ways to judge the credit, because nobody yet knows how much using a
// topic inside another really refreshes it:
// - "credit is right": the learner remembers what the credited card says;
// - "credit is worthless": the learner remembers only what the card without
//   credit says, while the schedule follows the credited card. Reviews come
//   later than memory would want, so more of them fail. This is the worst
//   case for the rule.
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parse as parseYaml } from 'yaml'
import type { Topic } from '../src/content/types.ts'
import type { GradedEvent } from '../src/progress/progress.ts'
import {
  type Card,
  type Rating,
  replayCard,
  retrievabilityAt,
  type Review,
} from '../src/reviews/fsrs.ts'
import { creditsFrom, replayWithCredits } from '../src/reviews/implicit.ts'

const ROOT = fileURLToPath(new URL('../../', import.meta.url))
const DAILY_LIMIT = 20
const minutesPerDay = Number(process.argv[2] ?? 60)
const MODULES = Number(process.argv[3] ?? 3)
const DAYS = Number(process.argv[4] ?? 365)
// Fewer runs for a long simulation, which is slow.
const SEEDS = MODULES > 3 ? 3 : 20

type Mode = 'without' | 'credit is right' | 'credit is worthless'

/** The topics of the first MODULES modules, in track order, from content/. */
function loadTopics(): Topic[] {
  const track = parseYaml(
    readFileSync(
      join(ROOT, 'content/tracks/cloud-solutions-architect.yaml'),
      'utf8',
    ),
  ) as { modules: { topics: string[]; checkpoint: string }[] }
  const ids = track.modules
    .slice(0, MODULES)
    .flatMap((module) => [...module.topics, module.checkpoint])
  return ids.map((id) => {
    const topic = parseYaml(
      readFileSync(join(ROOT, 'content/topics', id, 'topic.yaml'), 'utf8'),
    ) as Topic
    // An outline has no proofs yet: give it the build and debug it will have.
    topic.prove ??= {}
    topic.prove.build ??= 'build'
    topic.prove.debug ??= 'debug'
    topic.prerequisites ??= []
    return topic
  })
}

/** A small seeded random number generator, so every run is the same. */
function generator(seed: number): () => number {
  let state = seed
  return () => {
    state = (state * 1_103_515_245 + 12_345) % 2_147_483_648
    return state / 2_147_483_648
  }
}

const dayAt = (day: number) =>
  new Date(Date.UTC(2027, 0, 1, 18) + day * 86_400_000).toISOString()

type Result = { perDay: number[]; again: number }

function simulate(topics: Topic[], mode: Mode, seed: number): Result {
  const random = generator(seed)
  const byId = new Map(topics.map((topic) => [topic.id, topic]))
  const topicOf = (id: string) => byId.get(id)
  const learnedAt = new Map<string, string>()
  const reviews = new Map<string, Review[]>()
  const events: GradedEvent[] = []
  const perDay: number[] = []
  let again = 0
  let next = 0
  let minutesLeft = topics[0]?.estimated_minutes ?? 0

  const cardsOn = (useCredits: boolean): Map<string, Card> => {
    const credits = useCredits ? creditsFrom(events, topicOf) : new Map()
    const cards = new Map<string, Card>()
    for (const [id, at] of learnedAt) {
      const own = reviews.get(id) ?? []
      cards.set(
        id,
        useCredits
          ? replayWithCredits(at, own, credits.get(id)).card
          : replayCard(at, own),
      )
    }
    return cards
  }

  for (let day = 0; day < DAYS; day++) {
    const now = dayAt(day)
    // New study first, in the morning.
    let budget = minutesPerDay
    while (budget > 0 && next < topics.length) {
      const spent = Math.min(budget, minutesLeft)
      budget -= spent
      minutesLeft -= spent
      if (minutesLeft > 0) break
      const topic = topics[next] as Topic
      const at = new Date(Date.parse(now) - 6 * 3_600_000).toISOString()
      for (const item of [topic.prove.build, topic.prove.debug]) {
        if (!item) continue
        events.push({
          type: 'code_check',
          topic_id: topic.id,
          item_id: item,
          correct: true,
          occurred_at: at,
        })
      }
      if (topic.kind === 'topic') learnedAt.set(topic.id, at)
      next += 1
      minutesLeft = topics[next]?.estimated_minutes ?? 0
    }
    // Then the reviews that are due, in the evening.
    const schedule = cardsOn(mode !== 'without')
    const memory = mode === 'credit is worthless' ? cardsOn(false) : schedule
    const due = [...schedule]
      .filter(([, card]) => card.due <= now)
      .map(([id, card]) => ({ id, recall: retrievabilityAt(card, now) }))
      .sort((a, b) => a.recall - b.recall)
      .slice(0, DAILY_LIMIT)
    for (const { id } of due) {
      const remembered = retrievabilityAt(memory.get(id) as Card, now)
      const right = [random(), random()].filter((x) => x < remembered).length
      const rating: Rating =
        right === 2 ? 'good' : right === 1 ? 'hard' : 'again'
      if (rating === 'again') again += 1
      reviews.set(id, [...(reviews.get(id) ?? []), { at: now, rating }])
      events.push({
        type: 'review',
        topic_id: id,
        item_id: 'review',
        correct: rating === 'good',
        rating,
        occurred_at: now,
      })
    }
    perDay.push(due.length)
  }
  return { perDay, again }
}

function summary(topics: Topic[], mode: Mode) {
  const runs = Array.from({ length: SEEDS }, (_, seed) =>
    simulate(topics, mode, seed + 1),
  )
  const mean = (values: number[]) =>
    values.reduce((sum, value) => sum + value, 0) / values.length
  const total = mean(runs.map((run) => run.perDay.reduce((a, b) => a + b, 0)))
  const busiest = mean(runs.map((run) => Math.max(...run.perDay)))
  const lastMonth = mean(runs.map((run) => mean(run.perDay.slice(-30))))
  const again = mean(runs.map((run) => run.again))
  return { mode, total, perDay: total / DAYS, busiest, lastMonth, again }
}

const topics = loadTopics()
const minutes = topics.reduce((sum, topic) => sum + topic.estimated_minutes, 0)
console.log(
  `${topics.length} topics and checkpoints, ${minutes} minutes of study; ` +
    `${minutesPerDay} minutes a day finishes them on day ${Math.ceil(minutes / minutesPerDay)}.`,
)
console.log(
  `Averages over ${SEEDS} runs of ${DAYS} days.\n\n` +
    `| | Reviews in ${DAYS} days | A day, on average | Busiest day | A day, last 30 days | Rated Again |\n` +
    '| --- | --- | --- | --- | --- | --- |',
)
for (const mode of [
  'without',
  'credit is right',
  'credit is worthless',
] as const) {
  const row = summary(topics, mode)
  console.log(
    `| ${row.mode} | ${row.total.toFixed(0)} | ${row.perDay.toFixed(2)} | ${row.busiest.toFixed(1)} | ${row.lastMonth.toFixed(2)} | ${row.again.toFixed(1)} |`,
  )
}
