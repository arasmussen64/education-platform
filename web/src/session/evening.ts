// New material earlier, reviews any time. A new topic takes fresh attention,
// which runs low late in the day, and the sleep that follows a day's
// learning helps it settle. A review is short retrieval practice and suits a
// tired evening. So when the Today page opens late in the learner's evening,
// it says so in one gentle line. It never blocks or hides anything.

/**
 * "Late in the evening" on the learner's own clock: from 21:00 until 04:00.
 * 21:00 is about when evening tiredness sets in for most people; until 04:00
 * covers a night owl's "evening" that runs past midnight, while a learner up
 * early at 05:00 sees nothing.
 */
export const EVENING_STARTS_HOUR = 21
export const EVENING_ENDS_HOUR = 4

/** Whether `now` falls late in the evening on this device's clock. */
export function isLateEvening(now: string | Date): boolean {
  const hour = new Date(now).getHours()
  return hour >= EVENING_STARTS_HOUR || hour < EVENING_ENDS_HOUR
}

export const EVENING_LINE =
  "It's late in your day: a good time for reviews. A new topic takes fresh attention, so it may go better earlier tomorrow, with a night's sleep after it to help it settle."
