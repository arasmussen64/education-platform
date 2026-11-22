// Shared Tailwind class lists, so buttons look the same everywhere.
//
// The colours are Momentum's named colours (index.css): paper, card, ink,
// muted, line and so on. Each changes with the colour scheme by itself, so a
// class here needs no `dark:` twin. The one exception is a code box's border,
// which exists only in dark mode, where the box is nearly the page's colour.

export const BUTTON =
  'rounded-lg bg-ink px-4 py-2 text-sm font-semibold text-card shadow-sm hover:bg-ink/85 active:translate-y-px disabled:opacity-50'

/** A page's title: the one big heading at its top. */
export const PAGE_TITLE = 'text-3xl font-bold sm:text-4xl'

/**
 * A small label in capitals above a heading or a number: "Today's session",
 * "Reviews due". Quiet, so the thing it names stands out.
 */
export const EYEBROW =
  'text-xs font-semibold tracking-widest text-muted uppercase'

/** A big number with its label under it: Gabarito, like a heading. */
export const STAT_NUMBER = 'font-display text-3xl leading-none font-bold'

/** A small rounded label: a state, a count, a time. */
export const CHIP =
  'inline-flex items-center gap-1 rounded-full border border-line bg-sunken px-2.5 py-0.5 text-sm font-medium whitespace-nowrap text-ink'

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
  'space-y-3 leading-relaxed [&_table]:block [&_table]:w-fit [&_table]:max-w-full [&_table]:overflow-x-auto [&_table]:rounded-lg [&_table]:border [&_table]:border-line-strong [&_table]:text-[0.95em] [&_th]:border-b [&_th]:border-line-strong [&_th]:bg-sunken [&_th]:px-3 [&_th]:py-1.5 [&_th]:text-left [&_th]:font-semibold [&_td]:border-t [&_td]:border-line [&_td]:px-3 [&_td]:py-1.5 [&_td]:align-top [&_a]:underline [&_code]:rounded [&_code]:bg-line [&_code]:px-1 [&_code]:font-mono [&_code]:text-[0.9em] [&_code]:text-ink [&_:not(pre)>code]:wrap-anywhere [&_pre]:overflow-x-auto [&_pre]:rounded-md [&_pre]:bg-code [&_pre]:p-3 [&_pre]:text-sm [&_pre]:text-on-code dark:[&_pre]:border dark:[&_pre]:border-line-strong [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_pre_code]:text-on-code [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:list-decimal [&_ol]:pl-6'

/**
 * A reading copied in from another site (ADR-0031): the prose styles, plus
 * the things only a reading holds. Its headings stay smaller than the
 * page's own, a wide table or formula scrolls inside its box, and a picture
 * gets a light ground, since most diagrams are drawn for a white page.
 */
export const READING = `${PROSE} [&_h2]:text-lg [&_h2]:font-semibold [&_h3]:font-semibold [&_h4]:font-semibold [&_h5]:font-semibold [&_img]:h-auto [&_img]:max-w-full [&_img]:rounded [&_img]:bg-picture [&_blockquote]:border-l-2 [&_blockquote]:border-line-strong [&_blockquote]:pl-3 [&_dt]:font-semibold [&_dd]:pl-6 [&_math]:max-w-full [&_figcaption]:text-sm [&_figcaption]:text-muted`

/** A bordered box for one practice item or exercise. */
export const CARD =
  'space-y-3 rounded-2xl border border-line bg-card p-4 shadow-card sm:p-5'

/** The same surface without the spacing between children, for a grid tile. */
export const TILE = 'rounded-2xl border border-line bg-card p-4 shadow-card'

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
  'inline-block rounded-xl bg-forward px-6 py-3 font-semibold text-on-forward shadow-sm ring-1 ring-forward-edge/40 ring-inset hover:bg-forward-hover active:translate-y-px disabled:opacity-50'

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

/**
 * A progress fill drawn by the page itself: a rounded track with a lime
 * fill whose width is set inline. For a bar that only repeats a count the
 * words beside it give, so it is hidden from screen readers.
 */
export const BAR_TRACK = 'h-2 overflow-hidden rounded-full bg-line'
export const BAR_FILL = `h-full rounded-full border ${PROGRESS_FILL}`

/** The label of something done: Learned, Mastered, Passed. A progress fill. */
export const DONE_CHIP = `inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-sm font-medium whitespace-nowrap ${PROGRESS_FILL}`

export const SECONDARY_BUTTON =
  'rounded-lg border border-line-strong bg-card px-3 py-1.5 text-sm font-medium text-ink shadow-sm hover:bg-sunken active:translate-y-px disabled:opacity-50'

export const TEXT_INPUT =
  'mt-1 block w-full rounded-lg border border-line-strong bg-card px-3 py-2 text-sm text-ink'
