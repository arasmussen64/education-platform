import { createElement, type ReactNode } from 'react'

/**
 * Turns a reading's stored HTML into React elements (ADR-0031).
 *
 * A reading is a copy of part of somebody else's page, kept as a small,
 * plain subset of HTML. The importer cleans a page down to that subset and
 * the content validator refuses a file with anything else in it
 * (tools/reading_html.py, whose list this one mirrors). This is the third
 * guard: the text is never handed to the browser as HTML. Each allowed tag
 * is rebuilt as an element, with only its allowed attributes, and anything
 * else is left out with all it holds.
 */

/** Each tag a reading may hold, with the attributes it may carry. */
const ALLOWED: Record<string, readonly string[]> = {
  // Blocks.
  p: [],
  h2: [],
  h3: [],
  h4: [],
  h5: [],
  ul: [],
  ol: ['start'],
  li: [],
  dl: [],
  dt: [],
  dd: [],
  pre: [],
  blockquote: [],
  hr: [],
  figure: [],
  figcaption: [],
  table: [],
  caption: [],
  thead: [],
  tbody: [],
  tr: [],
  th: ['colspan', 'rowspan'],
  td: ['colspan', 'rowspan'],
  // Inline.
  a: ['href'],
  img: ['src', 'alt'],
  em: [],
  strong: [],
  i: [],
  b: [],
  code: [],
  kbd: [],
  samp: [],
  var: [],
  sub: [],
  sup: [],
  br: [],
  // Formulas: MathML, which browsers draw themselves.
  math: ['display'],
  mrow: [],
  mi: ['mathvariant'],
  mn: [],
  mo: ['stretchy', 'fence', 'separator', 'lspace', 'rspace'],
  mtext: [],
  mspace: ['width'],
  mfrac: ['linethickness'],
  msup: [],
  msub: [],
  msubsup: [],
  msqrt: [],
  mroot: [],
  munder: [],
  mover: ['accent'],
  munderover: [],
  mtable: ['columnalign'],
  mtr: [],
  mtd: ['columnalign'],
  mstyle: ['displaystyle', 'scriptlevel'],
  mpadded: [],
  menclose: ['notation'],
}

const VOID = new Set(['br', 'hr', 'img', 'mspace'])

/** Tags whose children are only other tags: the spaces between them go. */
const NO_LOOSE_TEXT = new Set([
  'ul',
  'ol',
  'dl',
  'table',
  'thead',
  'tbody',
  'tr',
  'mtable',
  'mtr',
  'mfrac',
  'msup',
  'msub',
  'msubsup',
  'mroot',
  'munder',
  'mover',
  'munderover',
])

/** React's names for the two attributes it spells differently. */
const REACT_NAME: Record<string, string> = {
  colspan: 'colSpan',
  rowspan: 'rowSpan',
}

function convert(node: Node, key: string, parent: string): ReactNode {
  if (node.nodeType === Node.TEXT_NODE) {
    const text = node.textContent ?? ''
    return NO_LOOSE_TEXT.has(parent) && text.trim() === '' ? null : text
  }
  if (node.nodeType !== Node.ELEMENT_NODE) return null
  const element = node as Element
  const tag = element.localName
  const allowed = ALLOWED[tag]
  if (!allowed) return null

  const props: Record<string, string> = { key }
  for (const name of allowed) {
    const value = element.getAttribute(name)
    if (value === null) continue
    // An address must be a full https one: no scripts, no local files.
    if ((name === 'href' || name === 'src') && !value.startsWith('https://')) {
      continue
    }
    props[REACT_NAME[name] ?? name] = value
  }
  if (tag === 'a') {
    // A reading's links lead to other sites: they open beside the lesson.
    props.target = '_blank'
    props.rel = 'noreferrer'
  }
  if (tag === 'img') {
    if (!props.src) return null
    props.alt ??= ''
    // Pictures come from the source's own site, and only when scrolled near.
    props.loading = 'lazy'
    props.referrerPolicy = 'no-referrer'
  }
  if (VOID.has(tag)) return createElement(tag, props)
  return createElement(
    tag,
    props,
    ...Array.from(element.childNodes, (child, index) =>
      convert(child, `${key}.${index}`, tag),
    ),
  )
}

/** The elements of a reading's HTML, safe to place in the page. */
export function readingToReact(html: string): ReactNode[] {
  const page = new DOMParser().parseFromString(html, 'text/html')
  return Array.from(page.body.childNodes, (node, index) =>
    convert(node, String(index), 'body'),
  )
}
