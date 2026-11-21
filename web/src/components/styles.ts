// Shared Tailwind class lists, so buttons look the same everywhere.

export const BUTTON =
  'rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200'

/**
 * Code inside a line of text (Markdown `like this`), shaded and monospaced.
 * A long one (a CSV header, an IPv6 address) may break anywhere, so it can't
 * make the page wider than a phone's screen. Code blocks scroll instead.
 */
export const INLINE_CODE =
  '[&_code]:rounded [&_code]:bg-slate-200 [&_code]:px-1 [&_code]:font-mono [&_code]:text-[0.9em] [&_code]:wrap-anywhere dark:[&_code]:bg-slate-800'

/** A box for a program or its output. Darker than a card, even in dark mode. */
export const CODE_BOX =
  'overflow-x-auto rounded-md bg-slate-900 p-3 font-mono text-sm text-slate-100 dark:border dark:border-slate-700 dark:bg-slate-950'

/** Readable text from Markdown or MDX: paragraphs, lists, inline and block code. */
export const PROSE =
  'space-y-3 leading-relaxed [&_a]:underline [&_code]:rounded [&_code]:bg-slate-200 [&_code]:px-1 [&_code]:font-mono [&_code]:text-[0.9em] [&_:not(pre)>code]:wrap-anywhere dark:[&_code]:bg-slate-800 [&_pre]:overflow-x-auto [&_pre]:rounded-md [&_pre]:bg-slate-900 [&_pre]:p-3 [&_pre]:text-sm [&_pre]:text-slate-100 dark:[&_pre]:border dark:[&_pre]:border-slate-700 dark:[&_pre]:bg-slate-950 [&_pre_code]:bg-transparent [&_pre_code]:p-0 dark:[&_pre_code]:bg-transparent [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:list-decimal [&_ol]:pl-6'

/** A bordered box for one practice item or exercise. */
export const CARD =
  'space-y-3 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900'

/**
 * Momentum's lime (index.css) means "forward" and nothing else. It has three
 * uses, each with its constants here so they can't drift apart:
 * PRIMARY_BUTTON, PROGRESS_FILL and PROGRESS_BAR, and YOU_ARE_HERE.
 * styles.test.ts fails if a lime class is written anywhere else.
 *
 * Lime is always a fill with pine ink on top (10.4 to 1, the same in light
 * and dark mode). It is never a text colour: lime on paper is 1.4 to 1.
 */

/**
 * The one "forward" action on a card: the way on, such as starting today's
 * session or the next part. Never two on one card.
 */
export const PRIMARY_BUTTON =
  'inline-block rounded-md bg-lime-400 px-5 py-2.5 font-semibold text-slate-900 hover:bg-lime-300 disabled:opacity-50'

/**
 * The filled part of something that shows progress: a week practised, a
 * practice item done. The darker edge keeps the shape visible on paper.
 */
export const PROGRESS_FILL = 'border-lime-600 bg-lime-400 text-slate-900'

/**
 * The same for a <progress> bar, whose filled part the browser draws:
 * accent-color is the one colour it lets a page choose.
 */
export const PROGRESS_BAR = 'accent-lime-400'

/**
 * "You are here": the current page's tab, the track being shown. The edge
 * shows only where the element has a border.
 */
export const YOU_ARE_HERE =
  'border-lime-600 bg-lime-400 font-medium text-slate-900'

export const SECONDARY_BUTTON =
  'rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'

export const TEXT_INPUT =
  'mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 dark:border-slate-700'
