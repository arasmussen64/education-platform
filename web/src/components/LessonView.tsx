import type { MDXComponents } from 'mdx/types'
import { Children, type ReactNode, useMemo } from 'react'
import type { LessonComponent, TopicContent } from '../content/types.ts'
import { PLACE_ATTRIBUTE } from '../place/useCurrentPlace.ts'
import { GlossaryTerm } from './GlossaryTerm.tsx'
import { type SectionRange, WHOLE_INTRO, withPlaces } from './lessonSections.ts'
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
      className="space-y-2 rounded-lg border-l-4 border-lime-500 bg-lime-50 p-4 dark:bg-lime-950/40"
    >
      <p className="text-sm font-semibold tracking-wide text-lime-800 uppercase dark:text-lime-300">
        {title}
      </p>
      {children}
    </aside>
  )
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
  sections = WHOLE_INTRO,
  tail = true,
}: {
  Lesson: LessonComponent
  /** The topic's questions and resources, which the lesson's tags show. */
  content: TopicContent
  /** A long lesson in parts: the sections of the intro to show. */
  sections?: SectionRange
  /** Whether to show the main resource and the recap, which end a lesson. */
  tail?: boolean
}) {
  const resources = content.topic.resources
  const { from, to } = sections
  const components = useMemo<MDXComponents>(() => {
    // One of the topic's practice questions, asked in the lesson: graded
    // and saved exactly as in the practice ladder, which leaves it out
    // (lessonChecks.ts).
    const Check = ({ item, id }: { item: string } & PlaceProps) => (
      <PracticeItem
        itemId={item}
        content={content}
        context="practice"
        placeId={id}
      />
    )
    return {
      Intro: ({ children }: { children?: ReactNode }) => {
        const shown = withPlaces(children, (child) => child.type === Check, {
          from,
          to,
        })
        // The part with only the resource and the recap shows no intro.
        if (Children.count(shown) === 0) return null
        return (
          <Callout title={from === 0 ? 'What to watch for' : 'The lesson'}>
            {shown}
          </Callout>
        )
      },
      Recap: ({ children }: { children?: ReactNode }) =>
        tail ? (
          <Callout title="Recap" id="place-recap">
            {children}
          </Callout>
        ) : null,
      Resource: ({ index }: { index?: number }) => {
        const resource = resources[index ?? 0]
        return tail && resource ? (
          <div id="place-resource" {...{ [PLACE_ATTRIBUTE]: 'place-resource' }}>
            <ResourceView resource={resource} />
          </div>
        ) : null
      },
      Check,
      Puzzle,
      Story,
      // Added by the build, never written by hand: the first use of a term
      // another topic's glossary defines (src/tooling/remarkGlossary.ts).
      Term: GlossaryTerm,
    }
  }, [resources, content, from, to, tail])
  return (
    <div className={PROSE}>
      <Lesson components={components} />
    </div>
  )
}
