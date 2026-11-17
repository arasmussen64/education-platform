/**
 * Reads the glossary (ADR-0026) for the build: every ready topic's
 * glossary.yaml, with the topic's title, as remarkGlossary.ts needs it.
 *
 * Only ready topics count: a draft's or an outline's page can't be opened
 * on the live site, so a link to it would lead nowhere. The validator checks
 * the files themselves (tools/validate_content.py), so this trusts their
 * shape.
 *
 * Node only (it reads files), so the app's type check leaves it out
 * (tsconfig.app.json) and the build's includes it (tsconfig.node.json).
 */
import { glob, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { parse as parseYaml } from 'yaml'
import { limiter } from './limiter.ts'
import type { GlossaryTerm } from './remarkGlossary.ts'

type GlossaryFile = { term: string; aliases?: string[]; definition: string }[]
type TopicFile = { id: string; title: string; status: string }

export async function readGlossary(
  topicsFolder: string,
): Promise<GlossaryTerm[]> {
  // A few files at a time, like the build's other readers (vite.config.ts).
  const aFewAtATime = limiter(32)
  const read = (path: string) =>
    aFewAtATime(() => readFile(join(topicsFolder, path), 'utf-8'))
  const files: string[] = []
  for await (const file of glob('*/glossary.yaml', { cwd: topicsFolder })) {
    files.push(file)
  }
  const perTopic = await Promise.all(
    files.sort().map(async (file) => {
      // The folder is the topic's ID ("\\" on Windows, "/" elsewhere).
      const [folder = ''] = file.split(/[\\/]/)
      const [glossaryText, topicText] = await Promise.all([
        read(file),
        read(join(folder, 'topic.yaml')),
      ])
      const topic = parseYaml(topicText) as TopicFile
      if (topic.status !== 'ready') return []
      const entries = (parseYaml(glossaryText) ?? []) as GlossaryFile
      return entries.map((entry) => ({
        term: entry.term,
        aliases: entry.aliases ?? [],
        definition: entry.definition.trim(),
        topicId: topic.id,
        topicTitle: topic.title,
      }))
    }),
  )
  return perTopic.flat()
}
