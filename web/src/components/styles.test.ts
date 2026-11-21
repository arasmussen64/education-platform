// @vitest-environment node
// (This test reads the source files themselves, so it needs no browser.)
import { readdirSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { expect, test } from 'vitest'
import {
  PRIMARY_BUTTON,
  PROGRESS_BAR,
  PROGRESS_FILL,
  YOU_ARE_HERE,
} from './styles.ts'

// Lime means only "forward" (the Momentum design, index.css): the one
// primary button on a card, progress fills, and "you are here". Its classes
// are the `forward` colours (`bg-forward`, `text-on-forward` and so on).
// Keeping every one of them in styles.ts is what keeps that true: a new use
// has to be one of those constants, or a deliberate change to this test.
// Tailwind's own lime scale (`lime-400`) stays out of every file.
const FORWARD_CLASS =
  /\blime-\d|\b(?:bg|text|border|accent|ring|outline|decoration|fill|stroke)-(?:on-)?forward\b/

test('forward (lime) classes are written only in styles.ts', () => {
  const src = fileURLToPath(new URL('..', import.meta.url))
  const offenders = readdirSync(src, { recursive: true, encoding: 'utf-8' })
    .map((file) => file.replaceAll('\\', '/'))
    .filter((file) => /\.(ts|tsx|mdx)$/.test(file))
    .filter((file) => !/\.test\.tsx?$/.test(file))
    .filter((file) => file !== 'components/styles.ts')
    .filter((file) => FORWARD_CLASS.test(readFileSync(src + file, 'utf-8')))
  expect(offenders).toEqual([])
})

test('lime is a fill under pine ink, never a text colour', () => {
  const limes = [PRIMARY_BUTTON, PROGRESS_FILL, PROGRESS_BAR, YOU_ARE_HERE]
  for (const classes of limes) {
    expect(classes).not.toMatch(/\btext-forward/)
    expect(classes).not.toMatch(/\blime-\d/)
    // No dark: variant: pine ink on lime reads the same in both modes.
    expect(classes).not.toMatch(/dark:/)
  }
  for (const classes of [PRIMARY_BUTTON, PROGRESS_FILL, YOU_ARE_HERE]) {
    expect(classes).toMatch(/\bbg-forward\b/)
    expect(classes).toMatch(/\btext-on-forward\b/)
  }
})
