import { getSupabase } from '../supabase/client.ts'

// Sending a problem report (v1 spec, F15): a learner's note that something
// on a lesson, exercise or question is wrong. It's saved in problem_reports
// with the item and its revision, so the content can be fixed.

/** What a report is about: the topic, and the item within it if any. */
export type ReportAbout = {
  topicId: string
  /** An item's ID, or `lesson` or `explain` for the parts that aren't items. */
  itemId?: string
  itemRev?: number
}

/** The longest message the database takes. */
export const MAX_REPORT_CHARS = 2000

export type SendReport = (
  userId: string,
  about: ReportAbout,
  message: string,
) => Promise<'sent' | 'failed'>

/**
 * Saves one report. It never throws: a problem comes back as "failed", so
 * the page can say so and keep the learner's text.
 */
export const sendReport: SendReport = async (userId, about, message) => {
  try {
    const { error } = await getSupabase()
      .from('problem_reports')
      .insert({
        user_id: userId,
        topic_id: about.topicId,
        item_id: about.itemId ?? null,
        item_rev: about.itemRev ?? null,
        message: message.trim().slice(0, MAX_REPORT_CHARS),
      })
    return error ? 'failed' : 'sent'
  } catch {
    return 'failed'
  }
}
