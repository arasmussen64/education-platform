// Pieces shared by the Python exercise view and the lab view.
import { Markdown } from './Markdown.tsx'
import { SECONDARY_BUTTON } from './styles.ts'

/** Hints, one at a time, so the learner takes only as much help as they need. */
export function Hints({
  hints,
  shown,
  onShowMore,
}: {
  hints: string[]
  shown: number
  onShowMore: () => void
}) {
  return (
    <div className="space-y-2">
      {hints.slice(0, shown).map((hint, index) => (
        <div
          // Hints never change order, so their position is a stable key.
          // oxlint-disable-next-line react/no-array-index-key
          key={index}
          className="rounded-md border-l-4 border-amber-400 bg-amber-50 p-3 dark:bg-amber-950/40"
        >
          <p className="text-sm font-semibold">Hint {index + 1}</p>
          <Markdown>{hint}</Markdown>
        </div>
      ))}
      {shown < hints.length && (
        <button type="button" onClick={onShowMore} className={SECONDARY_BUTTON}>
          {shown === 0 ? 'Show a hint' : 'Show another hint'}
        </button>
      )}
    </div>
  )
}

/** Shown only after a pass (v1 spec, F5), so it can't replace the effort. */
export function ReferenceSolution({ code }: { code: string }) {
  return (
    <details className="rounded-md border border-slate-200 dark:border-slate-700">
      <summary className="cursor-pointer px-3 py-2 text-sm font-medium">
        Compare with a reference solution
      </summary>
      <pre className="overflow-x-auto border-t border-slate-200 p-3 font-mono text-sm dark:border-slate-700">
        {code}
      </pre>
    </details>
  )
}
