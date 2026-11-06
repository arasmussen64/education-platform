import type { MDXComponents } from 'mdx/types'
import { type ReactNode, useMemo } from 'react'
import type { LessonComponent, Resource } from '../content/types.ts'
import { ResourceView } from './ResourceView.tsx'
import { PROSE } from './styles.ts'

function Callout({ title, children }: { title: string; children: ReactNode }) {
  return (
    <aside className="space-y-2 rounded-lg border-l-4 border-lime-500 bg-lime-50 p-4 dark:bg-lime-950/40">
      <p className="text-sm font-semibold tracking-wide text-lime-800 uppercase dark:text-lime-300">
        {title}
      </p>
      {children}
    </aside>
  )
}

/**
 * A topic's lesson (lesson.mdx): the AI-written intro and recap around the
 * main resource (ADR-0004). The MDX file uses <Intro>, <Resource index={0} />
 * and <Recap>; this supplies what they look like.
 */
export function LessonView({
  Lesson,
  resources,
}: {
  Lesson: LessonComponent
  resources: Resource[]
}) {
  const components = useMemo<MDXComponents>(
    () => ({
      Intro: ({ children }: { children?: ReactNode }) => (
        <Callout title="What to watch for">{children}</Callout>
      ),
      Recap: ({ children }: { children?: ReactNode }) => (
        <Callout title="Recap">{children}</Callout>
      ),
      Resource: ({ index }: { index?: number }) => {
        const resource = resources[index ?? 0]
        return resource ? <ResourceView resource={resource} /> : null
      },
    }),
    [resources],
  )
  return (
    <div className={PROSE}>
      <Lesson components={components} />
    </div>
  )
}
