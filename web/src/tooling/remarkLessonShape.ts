/**
 * A step in compiling lesson.mdx (ADR-0025, amended 2026-11-21): it measures
 * the lesson and adds a line to the compiled module,
 *
 *     export const shape = { sections: [...], recapWords: 120 }
 *
 * so the topic page can cut a long lesson into parts of about half an hour
 * without rendering it first (src/parts/topicParts.ts).
 *
 * A lesson can only be cut where it asks a question: after a
 * `<Check item="…" />` written directly inside `<Intro>`, on a line of its
 * own. So the intro is measured as "sections", each a run of blocks
 * (paragraphs, lists, code blocks, a puzzle, a story) that ends with such a
 * question; the last section is whatever follows the last question.
 *
 * It runs on the Markdown syntax tree ("mdast") that MDX builds, as
 * remarkLessonChecks.ts does, and must run before remarkGlossary.ts, which
 * adds tags of its own around words.
 *
 * Pure: no Node APIs, so the app's type check can read it too.
 */

/** One stretch of the intro, up to and including the question that ends it. */
export type LessonSection = {
  /** How many words it has to read, code included. */
  words: number
  /**
   * How many blocks it holds, the question included. The page numbers the
   * intro's blocks as places ("place-lesson-7"), so this says which section
   * a place is in.
   */
  blocks: number
  /** The item of the <Check> that ends it; null for the last stretch. */
  check: string | null
}

export type LessonShape = {
  /** The intro's sections, in order. Empty when the lesson has no <Intro>. */
  sections: LessonSection[]
  /** How many words the <Recap> has. */
  recapWords: number
  /**
   * The question of the lesson's opening <Puzzle>, as Markdown, when it has
   * one: the page can ask it before the lesson is opened (ADR-0030).
   */
  puzzle?: string
}

/** The little of a syntax tree node this step reads. */
type TreeNode = {
  type: string
  name?: string | null
  attributes?: { type: string; name?: string; value?: unknown }[]
  children?: TreeNode[]
  data?: unknown
  value?: string
}

/**
 * Nodes that put nothing on the page: a `{/* comment *\/}`, a link's
 * definition, an import or export. They aren't blocks and have no words.
 */
const UNSEEN = new Set([
  'mdxFlowExpression',
  'mdxTextExpression',
  'definition',
  'mdxjsEsm',
])

/** Attributes that are ids and addresses, not text a learner reads. */
const NOT_READ = new Set(['item', 'source', 'id', 'index'])

function countWords(text: string): number {
  return text.split(/\s+/).filter((word) => word !== '').length
}

/** The words a learner reads in a node and everything inside it. */
export function wordsIn(node: TreeNode): number {
  if (UNSEEN.has(node.type)) return 0
  let words = typeof node.value === 'string' ? countWords(node.value) : 0
  // A tag's text can be in an attribute: <Puzzle question="…">.
  for (const attribute of node.attributes ?? []) {
    if (
      attribute.type === 'mdxJsxAttribute' &&
      typeof attribute.value === 'string' &&
      !NOT_READ.has(attribute.name ?? '')
    ) {
      words += countWords(attribute.value)
    }
  }
  for (const child of node.children ?? []) words += wordsIn(child)
  return words
}

function isTag(node: TreeNode, name: string): boolean {
  return node.type === 'mdxJsxFlowElement' && node.name === name
}

/** The item of a <Check item="…" />, or null for any other node. */
function checkItem(node: TreeNode): string | null {
  if (!isTag(node, 'Check')) return null
  const item = node.attributes?.find(
    (attribute) =>
      attribute.type === 'mdxJsxAttribute' && attribute.name === 'item',
  )?.value
  return typeof item === 'string' ? item : null
}

/** A lesson's shape, from its syntax tree. */
export function shapeOf(tree: TreeNode): LessonShape {
  const top = tree.children ?? []
  const intro = top.find((node) => isTag(node, 'Intro'))
  const recap = top.find((node) => isTag(node, 'Recap'))
  const sections: LessonSection[] = []
  let open: LessonSection = { words: 0, blocks: 0, check: null }
  for (const block of intro?.children ?? []) {
    if (UNSEEN.has(block.type)) continue
    open.words += wordsIn(block)
    open.blocks += 1
    const item = checkItem(block)
    if (item !== null) {
      sections.push({ ...open, check: item })
      open = { words: 0, blocks: 0, check: null }
    }
  }
  if (open.blocks > 0) sections.push(open)
  const shape: LessonShape = {
    sections,
    recapWords: recap ? wordsIn(recap) : 0,
  }
  const puzzle = puzzleQuestion(intro)
  if (puzzle !== null) shape.puzzle = puzzle
  return shape
}

/** The question of the first <Puzzle question="…"> in the intro, or null. */
function puzzleQuestion(intro: TreeNode | undefined): string | null {
  const puzzle = intro?.children?.find((node) => isTag(node, 'Puzzle'))
  const question = puzzle?.attributes?.find(
    (attribute) =>
      attribute.type === 'mdxJsxAttribute' && attribute.name === 'question',
  )?.value
  return typeof question === 'string' && question.trim() !== ''
    ? question
    : null
}

/** A plain value (numbers, strings, null, lists, objects) as JavaScript. */
function literal(value: unknown): Record<string, unknown> {
  if (Array.isArray(value)) {
    return { type: 'ArrayExpression', elements: value.map(literal) }
  }
  if (value !== null && typeof value === 'object') {
    return {
      type: 'ObjectExpression',
      properties: Object.entries(value).map(([key, each]) => ({
        type: 'Property',
        key: { type: 'Identifier', name: key },
        value: literal(each),
        kind: 'init',
        method: false,
        shorthand: false,
        computed: false,
      })),
    }
  }
  return { type: 'Literal', value, raw: JSON.stringify(value) }
}

/**
 * `export const shape = {...}`, as the JavaScript syntax tree ("estree")
 * MDX expects an export in a lesson to carry.
 */
function exportOf(shape: LessonShape): TreeNode {
  const program = {
    type: 'Program',
    sourceType: 'module',
    body: [
      {
        type: 'ExportNamedDeclaration',
        specifiers: [],
        source: null,
        attributes: [],
        declaration: {
          type: 'VariableDeclaration',
          kind: 'const',
          declarations: [
            {
              type: 'VariableDeclarator',
              id: { type: 'Identifier', name: 'shape' },
              init: literal(shape),
            },
          ],
        },
      },
    ],
  }
  return {
    type: 'mdxjsEsm',
    value: `export const shape = ${JSON.stringify(shape)}`,
    data: { estree: program },
  }
}

/** The plugin itself, as MDX's `remarkPlugins` option takes it. */
export function remarkLessonShape() {
  return (tree: TreeNode) => {
    tree.children = [...(tree.children ?? []), exportOf(shapeOf(tree))]
  }
}
