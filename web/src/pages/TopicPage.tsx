import { useParams } from 'react-router'

// One topic: Learn, Practice and Prove it (v1 spec, F3, F5, F7).
// A placeholder that only shows which topic was asked for, read from the
// address (for example /topic/py.variables).
export function TopicPage() {
  const { topicId } = useParams()

  return (
    <section>
      <p className="text-sm text-slate-500 dark:text-slate-400">Topic</p>
      <h1 className="text-2xl font-bold">{topicId}</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-400">
        The lesson, practice and proof checks for this topic will appear here.
      </p>
    </section>
  )
}
