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
// primary button on a card, progress fills, and "you are here". Keeping
// every lime class in styles.ts is what keeps that true: a new use has to
// be one of those constants, or a deliberate change to this test.
test('lime classes are written only in styles.ts', () => {
  const src = fileURLToPath(new URL('..', import.meta.url))
  const offenders = readdirSync(src, { recursive: true, encoding: 'utf-8' })
    .map((file) => file.replaceAll('\\', '/'))
    .filter((file) => /\.(ts|tsx|mdx)$/.test(file))
    .filter((file) => !/\.test\.tsx?$/.test(file))
    .filter((file) => file !== 'components/styles.ts')
    .filter((file) => /\blime-\d/.test(readFileSync(src + file, 'utf-8')))
  expect(offenders).toEqual([])
})

test('lime is a fill under pine ink, never a text colour', () => {
  const limes = [PRIMARY_BUTTON, PROGRESS_FILL, PROGRESS_BAR, YOU_ARE_HERE]
  for (const classes of limes) {
    expect(classes).not.toMatch(/\btext-lime-/)
    // No dark: variant: ink on lime reads the same in both modes.
    expect(classes).not.toMatch(/dark:/)
  }
  for (const classes of [PRIMARY_BUTTON, PROGRESS_FILL, YOU_ARE_HERE]) {
    expect(classes).toMatch(/\bbg-lime-400\b/)
    expect(classes).toMatch(/\btext-slate-900\b/)
  }
})
