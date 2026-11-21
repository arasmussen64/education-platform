import { CARD } from '../components/styles.ts'
import type { Day } from '../days.ts'
import { DAILY_REVIEW_LIMIT } from '../reviews/reviews.ts'
import { dayLabel, type WelcomeBack } from './welcomeBack.ts'

// The welcome-back plan on the Today page (session/welcomeBack.ts): after a
// break, or when more reviews are due than a day's limit, the due reviews
// set out over the next few days. Calm, and never a list of what was missed.

function count(n: number, one: string, many: string): string {
  return `${n} ${n === 1 ? one : many}`
}

export function WelcomeBackPlan({
  plan,
  today,
}: {
  plan: WelcomeBack
  today: Day
}) {
  const { breakDays, due, days } = plan
  const topics = count(due, 'topic is', 'topics are')
  let intro: string
  if (breakDays !== null) {
    intro = `It's been ${breakDays} days since you last practised, and that's all right: what you learned is still there, some of it faded.`
    intro +=
      due === 0
        ? ' Nothing has faded far enough to need a review yet, so carry on where you left off.'
        : ` ${topics} due for a review. A review after a longer gap does more for a memory, so this is time well spent.`
  } else {
    intro = `${topics} due for a review, more than the ${DAILY_REVIEW_LIMIT} a day that reviews are kept to. Here they are over the next few days, the most faded first.`
  }

  return (
    <section aria-labelledby="welcome-back" className={CARD}>
      <h2 id="welcome-back" className="text-xl font-semibold">
        {breakDays !== null ? 'Welcome back' : 'A plan for your reviews'}
      </h2>
      <p>{intro}</p>
      {days.length > 0 && (
        <>
          <ol className="space-y-2">
            {days.map(({ day, reviews, minutes }) => (
              <li key={day}>
                <span className="font-medium">{dayLabel(day, today)}:</span>{' '}
                {count(reviews.length, 'review', 'reviews')}, about{' '}
                {count(minutes, 'minute', 'minutes')}
                <details className="text-sm text-muted">
                  <summary className="cursor-pointer">Which topics</summary>
                  <ul className="list-disc pl-6">
                    {reviews.map((review) => (
                      <li key={review.topic.id}>
                        {review.topic.title} (memory about{' '}
                        {Math.round(100 * review.retrievability)}%)
                      </li>
                    ))}
                  </ul>
                </details>
              </li>
            ))}
          </ol>
          <p className="text-sm text-muted">
            Topics that come due meanwhile join in, so take the days as a guide.
            {days[0].day === today &&
              " Today's session below starts with today's share, in this order."}
          </p>
        </>
      )}
    </section>
  )
}
