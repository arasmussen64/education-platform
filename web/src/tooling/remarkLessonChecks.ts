/**
 * A step in compiling lesson.mdx (ADR-0026): it finds every
 * `<Check item="…" />` in the lesson and adds a line to the compiled module,
 *
 *     export const checks = ['item-a', 'item-b']
 *
 * so the topic page knows which practice questions the lesson already asks,
 * and can leave them out of the practice ladder without rendering the lesson
 * first (src/content/lessonChecks.ts).
 *
 * It runs on the Markdown syntax tree ("mdast") that MDX builds, before MDX
 * turns it into JavaScript. A `<Check>` inside a code block is code, not a
 * tag, so it never appears in the tree as one. Only a plain string counts
 * (item="x"); tools/validate_content.py rejects any other form.
 *
 * Pure: no Node APIs, so the app's type check can read it too.
 */

/** The little of a syntax tree node this step reads. */
type TreeNode = {
  type: string
  name?: string | null
  attributes?: { type: string; name?: string; value?: unknown }[]
  children?: TreeNode[]
  data?: unknown
  value?: string
}

const JSX_ELEMENTS = new Set(['mdxJsxFlowElement', 'mdxJsxTextElement'])

/** The item ids of every <Check> in a lesson, in the order they appear. */
export function checksIn(tree: TreeNode): string[] {
  const found: string[] = []
  const visit = (node: TreeNode) => {
    if (JSX_ELEMENTS.has(node.type) && node.name === 'Check') {
      const item = node.attributes?.find(
        (attribute) =>
          attribute.type === 'mdxJsxAttribute' && attribute.name === 'item',
      )?.value
      if (typeof item === 'string') found.push(item)
    }
    for (const child of node.children ?? []) visit(child)
  }
  visit(tree)
  return found
}

/**
 * `export const checks = [...]`, as the JavaScript syntax tree ("estree")
 * MDX expects an export in a lesson to carry.
 */
function exportOf(items: string[]): TreeNode {
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
              id: { type: 'Identifier', name: 'checks' },
              init: {
                type: 'ArrayExpression',
                elements: items.map((item) => ({
                  type: 'Literal',
                  value: item,
                  raw: JSON.stringify(item),
                })),
              },
            },
          ],
        },
      },
    ],
  }
  return {
    type: 'mdxjsEsm',
    value: `export const checks = ${JSON.stringify(items)}`,
    data: { estree: program },
  }
}

/** The plugin itself, as MDX's `remarkPlugins` option takes it. */
export function remarkLessonChecks() {
  return (tree: TreeNode) => {
    tree.children = [...(tree.children ?? []), exportOf(checksIn(tree))]
  }
}
