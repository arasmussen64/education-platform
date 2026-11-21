import { Link } from 'react-router'
import { listedTerms } from '../content/glossary.ts'
import { Markdown } from '../components/Markdown.tsx'

/** /glossary: every term the topics teach, with where each is taught. */
export function GlossaryPage() {
  const terms = listedTerms()
  return (
    <section aria-labelledby="glossary" className="space-y-6">
      <div className="space-y-2">
        <h1 id="glossary" className="text-3xl font-bold">
          Glossary
        </h1>
        <p className="text-muted">
          Every term the topics teach, with the topic that teaches it. In a
          lesson, a word with a dotted underline is one of these: press it to
          see what it means.
        </p>
      </div>
      {terms.length === 0 ? (
        <p>No topic has listed its terms yet.</p>
      ) : (
        <dl className="space-y-4">
          {terms.map((entry) => (
            <div
              key={`${entry.topicId}/${entry.term}`}
              className="space-y-1 border-b border-line pb-4"
            >
              <dt className="font-display text-lg font-semibold">
                {entry.term}
                {entry.aliases && entry.aliases.length > 0 && (
                  <span className="ml-2 text-sm font-normal text-muted">
                    also {entry.aliases.join(', ')}
                  </span>
                )}
              </dt>
              <dd>
                <Markdown inline>{entry.definition}</Markdown>
              </dd>
              <dd className="text-sm text-muted">
                Taught in{' '}
                <Link to={`/topic/${entry.topicId}`} className="underline">
                  {entry.topicTitle}
                </Link>
              </dd>
            </div>
          ))}
        </dl>
      )}
    </section>
  )
}
