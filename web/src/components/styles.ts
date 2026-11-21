// Shared Tailwind class lists, so buttons look the same everywhere.
//
// The colours are Momentum's named colours (index.css): paper, card, ink,
// muted, line and so on. Each changes with the colour scheme by itself, so a
// class here needs no `dark:` twin. The one exception is a code box's border,
// which exists only in dark mode, where the box is nearly the page's colour.

export const BUTTON =
  'rounded-md bg-ink px-4 py-2 text-sm font-medium text-card hover:bg-ink/85 disabled:opacity-50'

/**
 * Code inside a line of text (Markdown `like this`), shaded and monospaced.
 * A long one (a CSV header, an IPv6 address) may break anywhere, so it can't
 * make the page wider than a phone's screen. Code blocks scroll instead.
 * The shade is the line colour, which shows on paper, on a card and on a
 * sunken area; the text is always ink, so code inside muted text stays
 * readable on that shade (muted on it would be 3.9 to 1).
 */
export const INLINE_CODE =
  '[&_code]:rounded [&_code]:bg-line [&_code]:px-1 [&_code]:font-mono [&_code]:text-[0.9em] [&_code]:text-ink [&_code]:wrap-anywhere'

/** A box for a program or its output. Darker than a card, even in dark mode. */
export const CODE_BOX =
  'overflow-x-auto rounded-md bg-code p-3 font-mono text-sm text-on-code dark:border dark:border-line-strong'

/** Readable text from Markdown or MDX: paragraphs, lists, inline and block code. */
export const PROSE =
  'space-y-3 leading-relaxed [&_a]:underline [&_code]:rounded [&_code]:bg-line [&_code]:px-1 [&_code]:font-mono [&_code]:text-[0.9em] [&_code]:text-ink [&_:not(pre)>code]:wrap-anywhere [&_pre]:overflow-x-auto [&_pre]:rounded-md [&_pre]:bg-code [&_pre]:p-3 [&_pre]:text-sm [&_pre]:text-on-code dark:[&_pre]:border dark:[&_pre]:border-line-strong [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_pre_code]:text-on-code [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:list-decimal [&_ol]:pl-6'

/** A bordered box for one practice item or exercise. */
export const CARD = 'space-y-3 rounded-lg border border-line bg-card p-4'

/**
 * Momentum's lime means "forward" and nothing else. Its classes are the
 * `forward` colours (index.css). It has three uses, each with its constants
 * here so they can't drift apart: PRIMARY_BUTTON, PROGRESS_FILL and
 * PROGRESS_BAR, and YOU_ARE_HERE. styles.test.ts fails if a `forward` or
 * lime class is written anywhere else.
 *
 * Lime is always a fill with pine ink on top (10.4 to 1, the same in light
 * and dark mode). It is never a text colour: lime on paper is 1.4 to 1.
 */

/**
 * The one "forward" action on a card: the way on, such as starting today's
 * session or the next part. Never two on one card.
 */
export const PRIMARY_BUTTON =
  'inline-block rounded-md bg-forward px-5 py-2.5 font-semibold text-on-forward hover:bg-forward-hover disabled:opacity-50'

/**
 * The filled part of something that shows progress: a week practised, a
 * practice item done. The darker edge keeps the shape visible on paper.
 */
export const PROGRESS_FILL = 'border-forward-edge bg-forward text-on-forward'

/**
 * The same for a <progress> bar, whose filled part the browser draws:
 * accent-color is the one colour it lets a page choose.
 */
export const PROGRESS_BAR = 'accent-forward'

/**
 * "You are here": the current page's tab, the track being shown. The edge
 * shows only where the element has a border.
 */
export const YOU_ARE_HERE =
  'border-forward-edge bg-forward font-medium text-on-forward'

export const SECONDARY_BUTTON =
  'rounded-md border border-line-strong px-3 py-1.5 text-sm font-medium text-ink hover:bg-sunken disabled:opacity-50'

export const TEXT_INPUT =
  'mt-1 block w-full rounded-md border border-line-strong bg-card px-3 py-2 text-sm text-ink'
