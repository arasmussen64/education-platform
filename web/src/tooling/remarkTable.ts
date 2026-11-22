/**
 * A step in reading Markdown: it teaches the parser tables, written the
 * usual way,
 *
 *     | line | pages |
 *     | ---- | ----- |
 *     | 1    | 40    |
 *
 * Plain Markdown has no tables, so without this a lesson's table showed as
 * a paragraph of `|` characters. Lessons (vite.config.ts) and the Markdown
 * in content files (components/Markdown.tsx) both use it.
 *
 * Only tables are added, not the rest of "GitHub-flavoured Markdown":
 * that would also turn `~text~` into struck-through text and bare web
 * addresses into links, in lessons written without either in mind.
 *
 * Pure: no Node APIs, so the app can use it in the browser too.
 */
import { gfmTableFromMarkdown } from 'mdast-util-gfm-table'
import { gfmTable } from 'micromark-extension-gfm-table'

/** The lists a Markdown processor keeps its parser's extensions in. */
type ParserData = {
  micromarkExtensions?: unknown[]
  fromMarkdownExtensions?: unknown[]
}

export function remarkTable(this: { data: () => unknown }) {
  const data = this.data() as ParserData
  ;(data.micromarkExtensions ??= []).push(gfmTable())
  ;(data.fromMarkdownExtensions ??= []).push(gfmTableFromMarkdown())
}
