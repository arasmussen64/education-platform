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

export const SECONDARY_BUTTON =
  'rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'

export const TEXT_INPUT =
  'mt-1 block w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 dark:border-slate-700'
