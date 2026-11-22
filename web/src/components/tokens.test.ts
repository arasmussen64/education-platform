// @vitest-environment node
// (This test reads the source files themselves, so it needs no browser.)
import { readdirSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { expect, test } from 'vitest'
import { MORNING_TRAIL, NIGHT_TRAIL } from './editorThemes.ts'

// Momentum's named colours ("design tokens") are defined once, in index.css:
// a light value in `:root` and, where the colour changes, a dark value inside
// the dark-mode media query. These tests read the real values from that file,
// so a later change to the palette that breaks a rule fails here.

const src = fileURLToPath(new URL('..', import.meta.url))
const css = readFileSync(src + 'index.css', 'utf-8')

/** The `--name: #hex` lines of the one block of index.css a pattern finds. */
function colours(block: RegExp): Record<string, string> {
  const body = css.match(block)?.[1] ?? ''
  const found = body.matchAll(/--([a-z-]+):\s*(#[0-9a-f]{6})\b/g)
  return Object.fromEntries([...found].map(([, name, hex]) => [name, hex]))
}

const light = colours(/\n:root\s*\{([^}]*)\}/)
const darkOnly = colours(
  /@media \(prefers-color-scheme: dark\)\s*\{\s*:root\s*\{([^}]*)\}/,
)
// A colour with no dark value is the same in both themes.
const dark = { ...light, ...darkOnly }

/** How bright a colour looks, from 0 (black) to 1 (white): WCAG's formula. */
function luminance(hex: string): number {
  const [r, g, b] = [1, 3, 5].map((at) => {
    const c = parseInt(hex.slice(at, at + 2), 16) / 255
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * r! + 0.7152 * g! + 0.0722 * b!
}

/** WCAG's contrast ratio, from 1 (the same colour) to 21 (black on white). */
function contrast(a: string, b: string): number {
  const [lighter, darker] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (lighter! + 0.05) / (darker! + 0.05)
}

test('index.css defines every named colour, and Tailwind gets each one', () => {
  expect(Object.keys(light).sort()).toEqual(
    [
      'paper',
      'card',
      'sunken',
      'ink',
      'muted',
      'line',
      'line-strong',
      'forward',
      'forward-hover',
      'forward-edge',
      'on-forward',
      'code',
      'on-code',
      'on-code-muted',
      'picture',
    ].sort(),
  )
  // A dark value only ever replaces a colour that has a light value.
  for (const name of Object.keys(darkOnly)) expect(light).toHaveProperty(name)
  // `--color-ink: var(--ink)` is what makes the class `text-ink` exist.
  for (const name of Object.keys(light)) {
    expect(css).toContain(`--color-${name}: var(--${name});`)
  }
})

// Every pairing of text on a background that the app's classes make.
// (Text on a sunken area is the tightest: muted there is 4.50 to 1 in light.)
const PAIRINGS: [text: string, background: string][] = [
  ['ink', 'paper'],
  ['ink', 'card'],
  ['ink', 'sunken'],
  ['ink', 'line'], // code inside a line of text; a nav link under the pointer
  ['muted', 'paper'],
  ['muted', 'card'],
  ['muted', 'sunken'],
  ['card', 'ink'], // the dark button (BUTTON in styles.ts)
  ['on-forward', 'forward'],
  ['on-forward', 'forward-hover'],
  ['on-code', 'code'],
  ['on-code-muted', 'code'],
]

test.each(PAIRINGS)(
  '%s on %s reads at 4.5 to 1 or better in both themes',
  (text, background) => {
    for (const [theme, palette] of Object.entries({ light, dark })) {
      expect(
        contrast(palette[text]!, palette[background]!),
        `${text} on ${background}, ${theme}`,
      ).toBeGreaterThanOrEqual(4.5)
    }
  },
)

// The code editor is drawn by CodeMirror, which wants plain hex values, so
// editorThemes.ts repeats some of these colours. This keeps the copies equal.
test("the code editor's themes use the named colours", () => {
  const editor = (palette: typeof MORNING_TRAIL) => ({
    background: palette.background,
    text: palette.text,
    gutter: palette.gutter,
    gutterText: palette.gutterText,
    cursor: palette.cursor,
    line: palette.line,
    comment: palette.syntax.comment,
  })
  expect(editor(MORNING_TRAIL)).toEqual({
    background: light.card,
    text: light.ink,
    gutter: light.paper,
    gutterText: light.muted,
    cursor: light.ink,
    line: light.line,
    comment: light.muted,
  })
  // The dark editor sits on the page colour, like a code box, and its lines
  // are the strong line so that they show there.
  expect(editor(NIGHT_TRAIL)).toEqual({
    background: dark.paper,
    text: dark.ink,
    gutter: dark.paper,
    gutterText: dark.muted,
    cursor: dark.ink,
    line: dark['line-strong'],
    comment: dark.muted,
  })
})

// Before the named colours, components used Tailwind's grey `slate` scale
// (and `white`), each with a `dark:` twin, and index.css repainted that scale.
// The repaint is gone, so a slate class would now be Tailwind's own blue-grey
// and would not match anything else on the page.
const OLD_GREYS =
  /\bslate-\d|\b(?:bg|text|border|ring|ring-offset|decoration|outline|divide)-white\b/

test('no source file uses the old slate scale or white', () => {
  const offenders = readdirSync(src, { recursive: true, encoding: 'utf-8' })
    .map((file) => file.replaceAll('\\', '/'))
    .filter((file) => /\.(ts|tsx|mdx|css)$/.test(file))
    .filter((file) => !/\.test\.tsx?$/.test(file))
    .filter((file) => OLD_GREYS.test(readFileSync(src + file, 'utf-8')))
  expect(offenders).toEqual([])
})
