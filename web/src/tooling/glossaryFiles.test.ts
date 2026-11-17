import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterEach, describe, expect, it } from 'vitest'
import { readGlossary } from './glossaryFiles.ts'

let folder = ''
afterEach(async () => {
  if (folder) await rm(folder, { recursive: true, force: true })
})

async function topic(id: string, status: string, glossary?: string) {
  await mkdir(join(folder, id), { recursive: true })
  await writeFile(
    join(folder, id, 'topic.yaml'),
    `id: ${id}\nstatus: ${status}\ntitle: Title of ${id}\n`,
  )
  if (glossary) await writeFile(join(folder, id, 'glossary.yaml'), glossary)
}

describe("the build's glossary (ADR-0026)", () => {
  it("reads ready topics' terms with their titles, and skips the rest", async () => {
    folder = await mkdtemp(join(tmpdir(), 'glossary-'))
    await topic(
      't.ready',
      'ready',
      '- term: NAT\n  aliases: [SNAT]\n  definition: >\n    Rewriting addresses.\n',
    )
    await topic('t.draft', 'draft', '- term: DNS\n  definition: Names.\n')
    await topic('t.none', 'ready')
    expect(await readGlossary(folder)).toEqual([
      {
        term: 'NAT',
        aliases: ['SNAT'],
        definition: 'Rewriting addresses.',
        topicId: 't.ready',
        topicTitle: 'Title of t.ready',
      },
    ])
  })

  it('reads the real content', async () => {
    // The tests run in web/.
    const topics = join(process.cwd(), '..', 'content', 'topics')
    const terms = await readGlossary(topics)
    expect(terms).toContainEqual(
      expect.objectContaining({ term: 'NAT', topicId: 'csa.net.nat' }),
    )
  })
})
