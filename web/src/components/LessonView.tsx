import type { MDXComponents } from 'mdx/types'
import {
  Children,
  cloneElement,
  isValidElement,
  type ReactElement,
  type ReactNode,
  useMemo,
} from 'react'
import type { LessonComponent, TopicContent } from '../content/types.ts'
import {
  LESSON_PLACE_PREFIX,
  PLACE_ATTRIBUTE,
} from '../place/useCurrentPlace.ts'
import { GlossaryTerm } from './GlossaryTerm.tsx'
import { PracticeItem } from './PracticeItem.tsx'
import { Puzzle } from './Puzzle.tsx'
import { ResourceView } from './ResourceView.tsx'
import { Story } from './Story.tsx'
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
      // Neutral on purpose: a callout is something to read, not the way
      // forward, so it leaves lime alone (the Momentum design).
      className="space-y-2 rounded-lg border-l-4 border-slate-400 bg-slate-100 p-4 dark:border-slate-500 dark:bg-slate-900"
    >
      <p className="text-sm font-semibold tracking-wide text-slate-600 uppercase dark:text-slate-300">
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

/** The place props LessonView's intro gives each of its parts (withPlaces). */
type PlaceProps = { id?: string; 'data-place'?: string }

/**
 * A topic's lesson (lesson.mdx): the AI-written intro and recap around the
 * main resource (ADR-0004). The MDX file uses <Intro>, <Resource index={0} />
 * and <Recap>, and may use the building blocks of ADR-0026: <Puzzle>,
 * <Check item="…" /> and <Story>, and <Term>, which the build adds where a
 * lesson first uses a glossary term. This supplies what they look like.
 * content/README.md says how to write each one, and the validator checks
 * them, so no other tag reaches this map.
 */
export function LessonView({
  Lesson,
  content,
}: {
  Lesson: LessonComponent
  /** The topic's questions and resources, which the lesson's tags show. */
  content: TopicContent
}) {
  const resources = content.topic.resources
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
      // One of the topic's practice questions, asked in the lesson: graded
      // and saved exactly as in the practice ladder, which leaves it out
      // (lessonChecks.ts).
      Check: ({ item, id }: { item: string } & PlaceProps) => (
        <PracticeItem
          itemId={item}
          content={content}
          context="practice"
          placeId={id}
        />
      ),
      Puzzle,
      Story,
      // Added by the build, never written by hand: the first use of a term
      // another topic's glossary defines (src/tooling/remarkGlossary.ts).
      Term: GlossaryTerm,
    }),
    [resources, content],
  )
  return (
    <div className={PROSE}>
      <Lesson components={components} />
    </div>
  )
}
