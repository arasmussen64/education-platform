import { expect, test } from 'vitest'
import {
  type EditorPalette,
  MORNING_TRAIL,
  NIGHT_TRAIL,
  paletteFor,
} from './editorThemes.ts'

/** A hex colour's red, green and blue (0 to 255) and opacity (0 to 1). */
function parse(hex: string) {
  const part = (at: number) => parseInt(hex.slice(at, at + 2), 16)
  return {
    rgb: [part(1), part(3), part(5)] as const,
    alpha: hex.length === 9 ? part(7) / 255 : 1,
  }
}

/** A see-through colour laid over a solid one, as the solid colour seen. */
function over(top: string, under: string): readonly number[] {
  const { rgb, alpha } = parse(top)
  const below = parse(under).rgb
  return rgb.map((value, i) => value * alpha + below[i]! * (1 - alpha))
}

/** How bright a colour looks, from 0 (black) to 1 (white): WCAG's formula. */
function luminance(rgb: readonly number[]): number {
  const [r, g, b] = rgb.map((value) => {
    const c = value / 255
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * r! + 0.7152 * g! + 0.0722 * b!
}

/** WCAG's contrast ratio, from 1 (the same colour) to 21 (black on white). */
function contrast(a: readonly number[], b: readonly number[]): number {
  const [lighter, darker] = [luminance(a), luminance(b)].sort((x, y) => y - x)
  return (lighter! + 0.05) / (darker! + 0.05)
}

const solid = (hex: string) => parse(hex).rgb

test.each([MORNING_TRAIL, NIGHT_TRAIL])(
  '$name: every code colour reads at 4.5 to 1 or better',
  (palette: EditorPalette) => {
    // The cursor's line is tinted, so code must read there too.
    const backgrounds = {
      background: solid(palette.background),
      'active line': over(palette.activeLine, palette.background),
    }
    const colours = { text: palette.text, ...palette.syntax }
    for (const [where, background] of Object.entries(backgrounds)) {
      for (const [what, colour] of Object.entries(colours)) {
        expect(
          contrast(solid(colour), background),
          `${what} on the ${where}`,
        ).toBeGreaterThanOrEqual(4.5)
      }
    }
    // Line numbers, on the gutter and on the gutter's active line.
    expect(
      contrast(solid(palette.gutterText), solid(palette.gutter)),
    ).toBeGreaterThanOrEqual(4.5)
    expect(
      contrast(solid(palette.text), over(palette.activeLine, palette.gutter)),
    ).toBeGreaterThanOrEqual(4.5)
  },
)

test('no editor colour is the lime kept for "forward"', () => {
  for (const palette of [MORNING_TRAIL, NIGHT_TRAIL]) {
    expect(JSON.stringify(palette).toLowerCase()).not.toContain('#a3e635')
  }
})

test('dark mode gets night trail, light mode morning trail', () => {
  expect(paletteFor(true)).toBe(NIGHT_TRAIL)
  expect(paletteFor(false)).toBe(MORNING_TRAIL)
})
