// The guided session: what "Start today's session" walks through, in order.
// Reviews first, the most faded first (ADR-0009), because a fading memory is
// the one that gains most from being pulled back now. Then the mistakes
// coming back today (ADR-0011). Then the next new topic, last, so the new
// material isn't crowded out by the old.
//
// This only puts things in an order. Which reviews are due, the daily limit
// and how a session is rated all stay in reviews/ and followups/.
import { getTopic, isOpen, topicIdsOf, tracks } from '../content/content.ts'
import type { Topic, Track } from '../content/types.ts'
import { dayOf } from '../days.ts'
import type { Attempt, FollowUp } from '../followups/followUps.ts'
import { reviewItemMinutes } from '../progress/pace.ts'
import { nextUp, type TopicProgress } from '../progress/progress.ts'
import {
  type DueReview,
  dueReviews,
  ITEMS_PER_REVIEW,
  reviewsLeftToday,
} from '../reviews/reviews.ts'

/** The addresses of the guided session and its five-minute version. */
export const SESSION_PATH = '/session'
export const QUICK_SESSION_PATH = '/session?minutes=5'

/** The most reviews the five-minute session asks. */
export const QUICK_REVIEW_COUNT = 3
/** How long the short session aims to take. */
export const QUICK_MINUTES = 5

/** The topic to learn next, and the track it's in. */
export type NextTopic = {
  topic: Topic
  state: 'in-progress' | 'available'
  track: Track
}

export type SessionPlan = {
  /** The reviews due today, most faded first, within the daily limit. */
  reviews: DueReview[]
  /** The mistakes coming back today. */
  followUps: FollowUp[]
  /** The new topic to finish with, if one is open. */
  next: NextTopic | null
}

/**
 * Every topic bundled with the app, in track order. An outline-only track's
 * topics aren't, and don't need to be: nothing in them can be due or next.
 */
export function bundledTopics(): Topic[] {
  return tracks()
    .flatMap(topicIdsOf)
    .map((id) => getTopic(id))
    .filter((topic) => topic !== undefined)
}

/** When the learner last answered anything in each track, by track id. */
function lastActive(
  trackList: Track[],
  attempts: Attempt[],
): Map<string, string> {
  const trackOf = new Map<string, string>()
  for (const track of trackList) {
    for (const id of topicIdsOf(track)) trackOf.set(id, track.id)
  }
  const latest = new Map<string, string>()
  for (const attempt of attempts) {
    // The placement test isn't studying a track (ADR-0021).
    if (attempt.context === 'placement') continue
    const trackId = trackOf.get(attempt.topic_id)
    if (!trackId) continue
    const before = latest.get(trackId)
    if (!before || attempt.occurred_at > before) {
      latest.set(trackId, attempt.occurred_at)
    }
  }
  return latest
}

/**
 * The next new topic: the topic in progress or next Available (nextUp) in
 * the track the learner worked in most recently, so a session carries on
 * where they were. A track they haven't touched comes after, in the app's
 * order; a track with nothing open to do is passed over.
 */
export function nextNewTopic(
  trackList: Track[],
  openTopics: Topic[],
  progress: Map<string, TopicProgress>,
  attempts: Attempt[],
): NextTopic | null {
  const byId = new Map(openTopics.map((topic) => [topic.id, topic]))
  const latest = lastActive(trackList, attempts)
  const ordered = trackList
    .map((track, order) => ({ track, order, at: latest.get(track.id) ?? '' }))
    // Most recent first; untouched tracks ('') last, in the app's order.
    .sort((a, b) => b.at.localeCompare(a.at) || a.order - b.order)
  for (const { track } of ordered) {
    const own = topicIdsOf(track)
      .map((id) => byId.get(id))
      .filter((topic) => topic !== undefined)
    const next = nextUp(own, progress)
    if (next) return { ...next, track }
  }
  return null
}

/** Today's whole session, as of `now` (ISO format). */
export function planSession({
  topics,
  progress,
  attempts,
  followUps,
  now,
  trackList = tracks(),
}: {
  /** Every topic bundled with the app (bundledTopics). */
  topics: Topic[]
  progress: Map<string, TopicProgress>
  attempts: Attempt[]
  /** Every open follow-up; those due by today's date are taken. */
  followUps: FollowUp[]
  now: string
  trackList?: Track[]
}): SessionPlan {
  const open = topics.filter(isOpen)
  const left = reviewsLeftToday(attempts, now)
  const today = dayOf(now)
  return {
    reviews: dueReviews(open, progress, now, left),
    followUps: followUps.filter((followUp) => followUp.due <= today),
    next: nextNewTopic(trackList, open, progress, attempts),
  }
}

/**
 * The five-minute version, for a day with little time or energy: only the
 * most faded reviews, at most `count`. They are ordinary review sessions,
 * saved and rated exactly as any other.
 */
export function quickPlan(
  plan: SessionPlan,
  count = QUICK_REVIEW_COUNT,
): SessionPlan {
  return {
    reviews: plan.reviews.slice(0, count),
    followUps: [],
    next: null,
  }
}

/**
 * How many reviews fit in the five-minute session, from how long the
 * learner's own review questions take (progress/pace.ts): at least one, at
 * most QUICK_REVIEW_COUNT. Two a minute each, say, fit two reviews.
 */
export function quickCount(attempts: Attempt[]): number {
  const perReview = ITEMS_PER_REVIEW * reviewItemMinutes(attempts)
  const fit = Math.floor(QUICK_MINUTES / perReview)
  return Math.max(1, Math.min(QUICK_REVIEW_COUNT, fit))
}

/**
 * About how many minutes a plan's reviews and mistakes coming back take,
 * from the learner's own review times: two questions a review, one a
 * mistake. Rounded up to a whole minute; 0 when there are none.
 */
export function reviewMinutes(plan: SessionPlan, attempts: Attempt[]): number {
  const questions =
    plan.reviews.length * ITEMS_PER_REVIEW + plan.followUps.length
  return Math.ceil(questions * reviewItemMinutes(attempts))
}
