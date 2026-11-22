/**
 * A step in compiling lesson.mdx (ADR-0026): the first time a lesson uses a
 * term that another topic's glossary.yaml defines, it wraps the word in
 *
 *     <Term term="NAT" definition="…" topicId="csa.net.nat" topicTitle="NAT">NAT</Term>
 *
 * which the app draws as a word with a dotted underline that shows the
 * definition (src/components/GlossaryTerm.tsx). Doing it here, while the app
 * is built, puts in each lesson only the few definitions it uses, so no page
 * downloads the whole glossary.
 *
 * Only the lesson's prose is read: never a heading, a link, code, a
 * <Puzzle> (a definition could give its answer away), a <Check> or a
 * <Resource>. A topic's own terms aren't marked on its own page, where the
 * lesson is what teaches them; they still block a shorter term inside them
 * ("source NAT" on the NAT page isn't marked as "NAT").
 *
 * Pure: no Node APIs. src/tooling/glossaryFiles.ts reads the files.
 */

/** One term, as the build reads it from a ready topic's glossary.yaml. */
export type GlossaryTerm = {
  term: string
  aliases: string[]
  definition: string
  topicId: string
  topicTitle: string
}

/** The little of a syntax tree node this step reads and writes. */
type TreeNode = {
  type: string
  name?: string | null
  value?: string
  children?: TreeNode[]
  attributes?: { type: string; name: string; value: string }[]
}

// Nodes whose text is never marked: what's inside them isn't prose to
// annotate. Code is never a "text" node, so it needs no entry.
const SKIPPED = new Set(['heading', 'link', 'linkReference', 'definition'])
// The only components whose text is read; anything else (<Puzzle>, <Check>,
// <Resource>, a <Term> already placed) is left alone.
const READ_COMPONENTS = new Set(['Intro', 'Recap', 'Story'])
const COMPONENTS = new Set(['mdxJsxFlowElement', 'mdxJsxTextElement'])

/** How a spelling is looked up: its first letter's case doesn't matter. */
function keyOf(word: string): string {
  return word.charAt(0).toLowerCase() + word.slice(1)
}

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/**
 * A word as a pattern: its first letter in either case ("Masquerade" at the
 * start of a sentence), the rest exactly ("NAT", never "nat").
 */
function patternOf(word: string): string {
  const first = word.charAt(0)
  const lower = first.toLowerCase()
  const upper = first.toUpperCase()
  const start = lower === upper ? escapeRegExp(first) : `[${lower}${upper}]`
  return start + escapeRegExp(word.slice(1))
}

export type Matcher = {
  /** Every spelling of every term, longest first; group 1 is the spelling. */
  pattern: RegExp
  /** The term each spelling belongs to, by keyOf. */
  bySpelling: Map<string, GlossaryTerm>
}

export function matcherOf(terms: GlossaryTerm[]): Matcher | null {
  const bySpelling = new Map<string, GlossaryTerm>()
  for (const term of terms) {
    for (const spelling of [term.term, ...term.aliases]) {
      bySpelling.set(keyOf(spelling), term)
    }
  }
  if (bySpelling.size === 0) return null
  const spellings = [...bySpelling.keys()].sort((a, b) => b.length - a.length)
  // A whole word: no letter, digit, underscore or hyphen either side, so
  // "NAT" isn't found in "NATIVE" or "5-tuple" in "15-tuple". A plural with
  // s or es is the same term.
  const pattern = new RegExp(
    `(?<![\\p{L}\\p{N}_-])(${spellings.map(patternOf).join('|')})(?:e?s)?(?![\\p{L}\\p{N}_-])`,
    'gu',
  )
  return { pattern, bySpelling }
}

function termNode(term: GlossaryTerm, text: string): TreeNode {
  const attribute = (name: string, value: string) => ({
    type: 'mdxJsxAttribute',
    name,
    value,
  })
  return {
    type: 'mdxJsxTextElement',
    name: 'Term',
    attributes: [
      attribute('term', term.term),
      attribute('definition', term.definition),
      attribute('topicId', term.topicId),
      attribute('topicTitle', term.topicTitle),
    ],
    children: [{ type: 'text', value: text }],
  }
}

/**
 * Marks the first use of each other topic's term in a lesson's tree, in
 * place. `topicId` is the lesson's own topic.
 */
export function markTerms(
  tree: TreeNode,
  terms: GlossaryTerm[],
  topicId: string,
): void {
  const matcher = matcherOf(terms)
  if (!matcher) return
  const { pattern, bySpelling } = matcher
  // Terms already marked, or met on their own topic's page.
  const seen = new Set<GlossaryTerm>()

  /** A text node, split around the terms it marks. */
  function split(text: string): TreeNode[] {
    const parts: TreeNode[] = []
    let last = 0
    for (const match of text.matchAll(pattern)) {
      const term = bySpelling.get(keyOf(match[1]))
      if (!term || seen.has(term)) continue
      seen.add(term)
      if (term.topicId === topicId) continue
      const at = match.index
      if (at > last) parts.push({ type: 'text', value: text.slice(last, at) })
      parts.push(termNode(term, match[0]))
      last = at + match[0].length
    }
    if (parts.length === 0) return [{ type: 'text', value: text }]
    if (last < text.length)
      parts.push({ type: 'text', value: text.slice(last) })
    return parts
  }

  function visit(node: TreeNode): void {
    if (!node.children) return
    node.children = node.children.flatMap((child) => {
      if (child.type === 'text' && child.value) return split(child.value)
      if (SKIPPED.has(child.type)) return [child]
      if (
        COMPONENTS.has(child.type) &&
        !READ_COMPONENTS.has(child.name ?? '')
      ) {
        return [child]
      }
      visit(child)
      return [child]
    })
  }
  visit(tree)
}

/** The start of a topic's ID, which names its track: "csa", "ml", "fin". */
function trackPrefix(topicId: string): string {
  return topicId.split('.')[0] ?? ''
}

/** The topic a lesson belongs to, from its path: …/topics/<id>/lesson.mdx. */
export function topicOfLesson(path: string): string | null {
  const match = /[\\/]topics[\\/]([^\\/]+)[\\/]lesson\.mdx$/.exec(path)
  return match ? match[1] : null
}

/**
 * The plugin, as MDX's `remarkPlugins` option takes it. `load` gives every
 * ready topic's terms; the build reads them once and shares them.
 */
export function remarkGlossary({
  load,
}: {
  load: () => Promise<GlossaryTerm[]>
}) {
  return async (tree: TreeNode, file: { path?: string }) => {
    const topicId = topicOfLesson(file.path ?? '')
    if (!topicId) return
    // Only terms taught in the lesson's own track: the same word means
    // different things in different subjects. A "frame" is a unit on a
    // network link in the cloud track and a function call's record in the
    // Python ones, and each track should give its own meaning or none.
    const terms = (await load()).filter(
      (term) => trackPrefix(term.topicId) === trackPrefix(topicId),
    )
    markTerms(tree, terms, topicId)
  }
}
