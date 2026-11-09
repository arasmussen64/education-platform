import type { MDXComponents } from 'mdx/types'
import {
  Children,
  cloneElement,
  isValidElement,
  type ReactElement,
  type ReactNode,
  useMemo,
} from 'react'
import type { LessonComponent, Resource } from '../content/types.ts'
import {
  LESSON_PLACE_PREFIX,
  PLACE_ATTRIBUTE,
} from '../place/useCurrentPlace.ts'
import { ResourceView } from './ResourceView.tsx'
import { PROSE } from './styles.ts'

function Callout({
  title,
  id,
  children,
}: {
  title: string
  /** A place on the page the outline can point at. */
  id?: string
  children: ReactNode
}) {
  return (
    <aside
      id={id}
      {...(id ? { [PLACE_ATTRIBUTE]: id } : {})}
      className="space-y-2 rounded-lg border-l-4 border-lime-500 bg-lime-50 p-4 dark:bg-lime-950/40"
    >
      <p className="text-sm font-semibold tracking-wide text-lime-800 uppercase dark:text-lime-300">
        {title}
      </p>
      {children}
    </aside>
  )
}

/**
 * Marks each of the intro's paragraphs (and lists, and code blocks) as a
 * place, so the outline can say how far into the lesson the learner is and
 * the next visit can continue there.
 */
function withPlaces(children: ReactNode): ReactNode {
  let part = 0
  return Children.map(children, (child) => {
    if (!isValidElement(child)) return child
    part += 1
    const id = `${LESSON_PLACE_PREFIX}${part}`
    return cloneElement(child as ReactElement<Record<string, unknown>>, {
      id,
      [PLACE_ATTRIBUTE]: id,
    })
  })
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
        <Callout title="What to watch for">{withPlaces(children)}</Callout>
      ),
      Recap: ({ children }: { children?: ReactNode }) => (
        <Callout title="Recap" id="place-recap">
          {children}
        </Callout>
      ),
      Resource: ({ index }: { index?: number }) => {
        const resource = resources[index ?? 0]
        return resource ? (
          <div id="place-resource" {...{ [PLACE_ATTRIBUTE]: 'place-resource' }}>
            <ResourceView resource={resource} />
          </div>
        ) : null
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
