# ADR-0009: Reviews are per topic and graded automatically

- **Status:** Accepted
- **Date:** 2026-11-05

## Context

Flashcard apps like Anki schedule a card for each fact and ask learners to rate themselves ("Hard", "Good"). That's self-report, which this platform avoids (ADR-0002). And reviewing the same card over and over can mean memorizing answers instead of keeping a skill. Math Academy instead schedules reviews per topic and uses fresh problems.

## Decision

- **One FSRS card per learner per topic.** Checkpoints don't get cards.
- **The card starts when the topic becomes Learned.** That counts as a first review rated Good.
- **A review session** is a short set of items drawn from the topic's review pool. In v1 that's 2 items, at least one of them code or predict-the-output. Pools have at least 3 items, and the app avoids repeating the previous review's items.
- **Ratings come from performance, not self-assessment:**
  - all items correct → Good
  - some correct → Hard
  - none correct → Again

  "Easy" isn't used in v1.
- **Defaults:** standard FSRS parameters, a 90% target retention, and at most 20 topic reviews a day.
- **No tutor during reviews.**

## Later

- **Implicit repetition:** practicing an advanced topic gives partial review credit to the topics it builds on, like Math Academy's FIRe.
- **Personal FSRS parameters** fitted to the owner's own history, as part of the ML capstone.
- **Using answer time** to tell Good from Easy.

## Alternatives considered

- **One card per item, self-rated (Anki-style).** Proven for facts, but it's self-report, and learners can end up memorizing specific answers.
- **Fixed review intervals.** Simpler, but they ignore how fast each learner actually forgets.

## Consequences

- Fewer, more meaningful reviews.
- Every topic needs a review pool, which is more content to write.
- The rating rules are a guess until real data tests them, which is exactly what the capstone is for.

## Amendment (2026-11-11): the scheduler is FSRS-4.5, exactly

"Standard FSRS parameters" means FSRS-4.5's published default parameters, run through FSRS-4.5's own formulas. An audit on 2026-11-11 found that `web/src/reviews/fsrs.ts` pulled difficulty a little toward w4 − w5 (3.93) after every review. FSRS-4.5 pulls it toward D0(3) = w4 (5.16), the difficulty a first Good gives; w4 − w5 is FSRS-5's target worked out with FSRS-4.5's formula. So a Good lowered a fresh topic's difficulty when it should leave it alone, and intervals came out longer than FSRS-4.5's (about 2% after three Goods, about 10% on paths with Hards), with recall at review time a little under the 90% target. Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".

- **The sources.** The open-spaced-repetition wiki page "The Algorithm" (sections FSRS v4 and FSRS-4.5), and the code of fsrs-optimizer 4.29.0 (which fitted the default parameters) and fsrs-rs 0.6.4 (the FSRS-4.5 in Anki). Both of those apply two limits the wiki leaves out, and the scheduler now does too: a lapse never makes stability higher than it was, which matters after a long break, and stability stays between 0.01 and 36,500 days.
- **How it's checked.** Tests compare stability, difficulty and the next interval with values computed by py-fsrs 2.5.1, the Python package's last FSRS-4.5 release (its 3.x and later releases are FSRS-5 and FSRS-6), after Good Good Good, Again then Good, Hard Good Easy, a twelve-review run with two lapses, nine Goods to the 365-day limit, and reviews taken early, late and very late. The formulas take Easy so the whole algorithm can be checked; no session is rated Easy in v1.
- **What a learner sees.** Cards are replayed from the review events, so every schedule changes at once and no data changes. Intervals are the same or shorter: none got longer in any of the 3,279 sequences of up to seven ratings taken on their due days. From Learned, Good Good Good gives 4, 15, 49 and 146 days, not 4, 15, 50 and 149; Again then six Goods ends 81 and 190 days, not 85 and 203; three Hards then four Goods ends 142 and 288 days, not 152 and 316. Of the cards with one or two reviews, only Good then Good moves, from 50 days to 49.
- **Not adopted.** Two habits of Anki's FSRS scheduler that aren't part of the memory model: a random spread ("fuzz") of intervals, and making a Good interval at least a day longer than a Hard one, which keeps Anki's answer buttons apart. There are no buttons here, and the capstone fits the plain model.

## Amendment (2026-11-11): a session left half-way still counts

A review session is rated from the first answer to each of its items given in a review session since the topic fell due, not only from answers given on one visit. Before, the rating lived in the page until every item had an answer. A learner who got the first item wrong and left (to re-read the lesson, say) came back to a fresh session, often with the same question straight after its explanation, and a Good then counted toward Mastered. The wrong answer still opened a follow-up, but the card never saw the lapse. Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".

- **Why.** A wrong answer at review time is the evidence that the topic was fading. Dropping it schedules the next review too late, and asking the same question again right after its explanation measures the explanation, not the memory.
- **How it works.** When a session starts, the items answered since the topic fell due stay in it, marked as answered on an earlier visit, with their first answers; the rest are chosen as before, still including one code or predict-the-output item. If earlier visits answered every item (possible with answers saved before this change, or on two devices), the session is saved as soon as it shows. The review event and its time are unchanged: it's saved when the session is finished.
- **What counts.** Only answers saved with the review context: practice answers on the topic page don't, and nor do older answers saved without a context. A review already saved keeps its rating: answers from before a saved review are never reread.

## Amendment (2026-11-11): the daily limit is a calendar day

"At most 20 topic reviews a day" means a calendar day in the learner's own time zone, not a load of the Today page. Before, each load offered up to 20 due topics, whatever had been done that day, so after a break every reload served 20 more. Now the review sessions already finished that day count against the 20, and the topics left over stay due, most forgotten first, for the next day. `reviewsLeftToday` in `web/src/reviews/reviews.ts` works this out, and the Today page uses it as `dueReviews`' limit. Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".
