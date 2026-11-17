import { getTopic, isOpen } from './content.ts'

/** One entry of a topic's glossary.yaml (ADR-0026). */
export type GlossaryEntry = {
  term: string
  aliases?: string[]
  definition: string
}

// Every topic's glossary. Only the glossary page imports this file, and that
// page loads only when it's visited, so the definitions download with it and
// never with the rest of the app. Lessons carry their own few definitions
// (src/tooling/remarkGlossary.ts).
const glossaryFiles = import.meta.glob<GlossaryEntry[]>(
  '../../../content/topics/*/glossary.yaml',
  { eager: true, import: 'default' },
)

export type ListedTerm = GlossaryEntry & { topicId: string; topicTitle: string }

/**
 * Every term whose topic a learner can open, in alphabetical order. A
 * draft's terms show on the dev server, as drafts do (isOpen).
 */
export function listedTerms(
  files: Record<string, GlossaryEntry[]> = glossaryFiles,
): ListedTerm[] {
  const listed: ListedTerm[] = []
  for (const [path, entries] of Object.entries(files)) {
    const topicId = /\/topics\/([^/]+)\/glossary\.yaml$/.exec(path)?.[1]
    const topic = topicId ? getTopic(topicId) : undefined
    if (!topic || !isOpen(topic)) continue
    for (const entry of entries) {
      listed.push({ ...entry, topicId: topic.id, topicTitle: topic.title })
    }
  }
  return listed.sort((a, b) =>
    a.term.localeCompare(b.term, 'en', { sensitivity: 'base' }),
  )
}
