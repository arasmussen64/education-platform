/**
 * What a question shows after an answer in the placement test (ADR-0021),
 * in place of "Correct!" or the explanation: the test measures, so the
 * learner hears how they did at the end, not question by question.
 */
export function Recorded() {
  return (
    <output className="block rounded-md bg-slate-100 p-3 text-sm text-slate-600 dark:bg-slate-800 dark:text-slate-300">
      Answer recorded.
    </output>
  )
}
