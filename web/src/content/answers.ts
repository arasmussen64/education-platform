/**
 * Puts printed output in a standard form before comparing a learner's
 * prediction with the real output: Windows line endings, spaces at the ends
 * of lines and blank lines at the very start or end don't count. Spaces at
 * the start of a line still do.
 */
export function normalizeOutput(text: string): string {
  return text
    .replace(/\r\n?/g, '\n')
    .split('\n')
    .map((line) => line.trimEnd())
    .join('\n')
    .replace(/^\n+|\n+$/g, '')
}
