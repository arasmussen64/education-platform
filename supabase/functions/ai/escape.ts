// Keeping text inside its block (ADR-0013, ADR-0015). The grading and tutor
// prompts mark each part of the message with tags, like <explanation> or
// <learner_code>. Text placed inside a block must never be able to end it
// or start another, or a learner could write their own "rubric" or "model
// answer" after closing their block.

/** Every character that reads as < or >, and how it's written instead. */
const ESCAPES: Record<string, string> = {
  '<': '&lt;',
  '>': '&gt;',
  // The fullwidth and small forms, which Unicode treats as the same
  // characters (NFKC normalization turns them into < and >).
  '＜': '&lt;',
  '＞': '&gt;',
  '﹤': '&lt;',
  '﹥': '&gt;',
}

/**
 * Writes every < and > in `text` as &lt; and &gt;, so the only tags in the
 * message are the prompt's own. This escapes rather than deletes: deleting
 * a tag can join the pieces around it into a new one (take the tag out of
 * "</expl</explanation>anation>" and "</explanation>" is left), while an
 * escaped text has no < left to make a tag with, however it's nested,
 * spaced or cased. Nothing is lost: Claude still reads all of it.
 */
export function escapeAngles(text: string): string {
  return text.replace(/[<>＜＞﹤﹥]/g, (character) => ESCAPES[character])
}

/**
 * Claude's reply, with any &lt; or &gt; it copied out of a block turned back
 * into < and >, so the learner sees `i <= n` and not `i &lt;= n`. The page
 * shows replies as Markdown without raw HTML, so a < can't do any harm there.
 */
export function unescapeAngles(text: string): string {
  return text.replaceAll('&lt;', '<').replaceAll('&gt;', '>')
}
