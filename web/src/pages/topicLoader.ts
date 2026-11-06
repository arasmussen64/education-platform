import type { LoaderFunctionArgs } from 'react-router'
import { getTopic, isOpen, loadTopicContent } from '../content/content.ts'

/**
 * Runs before the topic page shows (React Router calls this a "loader"):
 * finds the topic in the address and, if it's open, downloads its lesson and
 * exercises. The page then reads the result with useLoaderData().
 */
export async function topicLoader({ params }: LoaderFunctionArgs) {
  const topic = getTopic(params.topicId ?? '')
  const content =
    topic && isOpen(topic) ? await loadTopicContent(topic.id) : null
  return { topic, content }
}
