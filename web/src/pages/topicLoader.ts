import type { LoaderFunctionArgs } from 'react-router'
import {
  getTopic,
  isOpen,
  loadTopicContent,
  loadTrackOf,
} from '../content/content.ts'
import type { Topic } from '../content/types.ts'
import { dayOf } from '../days.ts'
import {
  earlierTopicFor,
  type Interleaved,
  interleavedItem,
} from '../practice/interleave.ts'

/**
 * Runs before the topic page shows (React Router calls this a "loader"):
 * finds the topic in the address and, if it's open, downloads its lesson and
 * exercises, plus one recall question from an earlier topic to mix into the
 * practice (F5). The page then reads the result with useLoaderData().
 */
export async function topicLoader({ params }: LoaderFunctionArgs) {
  const topicId = params.topicId ?? ''
  // A topic of an outline-only track isn't bundled in until asked for.
  await loadTrackOf(topicId)
  const topic = getTopic(topicId)
  const content =
    topic && isOpen(topic) ? await loadTopicContent(topic.id) : null
  const interleaved =
    topic && content && topic.kind === 'topic'
      ? await loadInterleaved(topic)
      : null
  return { topic, content, interleaved }
}

async function loadInterleaved(topic: Topic): Promise<Interleaved | null> {
  const earlier = earlierTopicFor(topic)
  if (!earlier || !isOpen(earlier)) return null
  const content = await loadTopicContent(earlier.id)
  const itemId = content ? interleavedItem(content, dayOf(Date.now())) : null
  return content && itemId ? { content, itemId } : null
}
