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

- **The sources.** The open-spaced-repetition wiki page "The Algorithm" (sections FSRS v4 and FSRS-4.5), and the code of fsrs-optimizer 4.29.0 (FSRS-4.5's training code, the model the default parameters belong to) and fsrs-rs 0.6.4 (the Rust FSRS-4.5 library). Both of those apply two limits the wiki leaves out, and the scheduler now does too: a lapse never makes stability higher than it was, which matters after a long break, and stability stays between 0.01 and 36,500 days.
- **How it's checked.** Tests compare stability, difficulty and the next interval with values computed by py-fsrs 2.5.1, the Python package's last FSRS-4.5 release (its 3.x and later releases are FSRS-5 and FSRS-6), after Good Good Good, Again then Good, Hard Good Easy, a twelve-review run with two lapses, nine Goods to the 365-day limit, and reviews taken early, late and very late. The formulas take Easy so the whole algorithm can be checked; no session is rated Easy in v1.
- **What a learner sees.** Cards are replayed from the review events, so every schedule changes at once and no data changes. Intervals are the same or shorter: none got longer in any of the 3,279 sequences of up to seven ratings taken on their due days. From Learned, Good Good Good gives 4, 15, 49 and 146 days, not 4, 15, 50 and 149; Again then six Goods ends 81 and 190 days, not 85 and 203; three Hards then four Goods ends 142 and 288 days, not 152 and 316. Of the cards with one or two reviews, only Good then Good moves, from 50 days to 49.
- **Not adopted.** Two habits of flashcard schedulers built on FSRS (py-fsrs's and the fsrs4anki script's) that aren't part of the memory model: a random spread ("fuzz") of intervals, and making a Good interval at least a day longer than a Hard one, which keeps their answer buttons apart. There are no buttons here, and the capstone fits the plain model.

## Amendment (2026-11-11): a session left half-way still counts

A review session is rated from the first answer to each of its items given in the review context since the topic fell due, not only from answers given on one visit. Before, the rating lived in the page until every item had an answer. A learner who got the first item wrong and left (to re-read the lesson, say) came back to a fresh session, often with the same question straight after its explanation, and a Good then counted toward Mastered. The wrong answer still opened a follow-up, but the card never saw the lapse. Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".

- **Why.** A wrong answer at review time is the evidence that the topic was fading. Dropping it schedules the next review too late, and asking the same question again right after its explanation measures the explanation, not the memory.
- **How it works.** When a session starts, the items answered since the topic fell due stay in it, marked as answered on an earlier visit, with their first answers; the rest are chosen as before, still including one code or predict-the-output item. Earlier answers never make up a session without one: when the first two are both quick checks, only the first is kept, with a code or prediction answered later if there is one, or else one asked now. If earlier visits answered every item (possible with answers saved before this change, or on two devices), the session is saved as soon as it shows. The review event and its time are unchanged: it's saved when the session is finished.
- **What counts.** Only answers saved with the review context: practice answers on the topic page don't, and nor do older answers saved without a context. The Today page's mistakes-to-revisit questions are saved in the review context too, with hints and the tutor off as in a review, so an answer to one of them counts when its item is in the topic's review pool: the saved answers can't tell the two apart. A review already saved keeps its rating: answers from before a saved review are never reread.

## Amendment (2026-11-11): the daily limit is a calendar day

"At most 20 topic reviews a day" means a calendar day in the learner's own time zone, not a load of the Today page. Before, each load offered up to 20 due topics, whatever had been done that day, so after a break every reload served 20 more. Now the review sessions already finished that day count against the 20, and the topics left over stay due, most forgotten first, for the next day. `reviewsLeftToday` in `web/src/reviews/reviews.ts` works this out, and the Today page uses it as `dueReviews`' limit. Decided under the owner's delegation of 2026-11-11 and recorded in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".

## Amendment (2026-11-16): implicit repetition

- **Status:** Proposed. Designed under the owner's delegation of 2026-11-11 (the best learning experience, then the best memory retention, then free) and built on until the owner rules; it is listed in [the owner queue](../owner-queue.md) under _Decided for you_.

"Later" above named implicit repetition, Math Academy's FIRe: practising an advanced topic gives partial review credit to the topics it builds on. It is built now, in `web/src/reviews/implicit.ts`. The learner's own reviews, their ratings and Mastered are unchanged; what changes is when a topic's next review falls due.

- **What counts as practising a topic.** A review of it rated Good, a review rated Hard, and a passed proof: a Check that passes its build or debug, a fresh version of a checkpoint's build, or a checkpoint's further part. Practice answers don't count: they're given while learning the topic, often with hints and the tutor. Neither do explanations, which don't use the earlier topics' skills, nor anything in the placement test. A review rated Again gives nothing and takes nothing away: the advanced topic's mistakes come back as its own follow-ups ([ADR-0011](0011-mistakes-come-back.md)).
- **Which topics get credit, and how much of a review.** A Good review or a passed proof gives a direct prerequisite half a review (a share of 0.5), a Hard review a quarter (0.25), since it had a wrong answer in it. The prerequisites' own prerequisites get credit too, the share halved at each step down: two steps down a quarter, three steps down an eighth. Shares below 0.1 are dropped, so a Good review or a proof reaches three steps down and a Hard review two. Where two paths reach a topic, the shorter one counts; shares from different paths never add up. _Why further than direct:_ a topic lists only its nearest prerequisites. DNS lists Transport, though its labs use `dig` from Network tools and its reverse zone the octets from CIDR; with direct credit only, almost every topic would credit one other.
- **Checkpoints are crossed out.** They have no card, and credit doesn't pass through them: "Hypervisors builds on Checkpoint 1" means it comes after Module 1, not that it uses every Module 1 topic. A checkpoint's own proofs do credit its direct prerequisites, at the full share, because its tests use those topics' skills.
- **What a share does.** A credit moves the topic's next review date part of the way from where it is toward where a real review rated Good, that day, would have put it: the share of the way, so 0.5 is half way. Because the interval at 90% retention is the stability itself ([fsrs.ts](../../web/src/reviews/fsrs.ts)), this is the stability moving the same share toward a Good review's, plus the share of the days since the last review. Difficulty is left alone: a credit says nothing about how hard the topic is. The last review's time doesn't move, so the map's memory percentage rises and the curve still reaches 90% on the new due date.
- **When it counts.** Only when all of these hold: the topic is Learned and isn't relearning (its last real review wasn't Again); the card is at least half way to due, since a recall soon after a review adds little (FSRS's own growth is near zero when recall is near 100%); it's at least a day since its last review or credit, so a burst of practice counts once (the biggest share at that moment, whatever order the events came in); and fewer than two credits have counted since its last real review. Credit can put a topic's own review off, but not for ever: after two, it waits for a real one.
- **What it can never do.** Make a review come sooner: each credit only moves a date later, and in 20,000 random histories of reviews and credits no due date came out earlier than without them (a test checks 2,000). Count as a review: credits aren't review events, so they can't be the Good review a week on that Mastered needs ([ADR-0002](0002-mastery-and-gating.md)), they don't use up the day's 20, and the card's count of reviews and lapses doesn't change. Credit a topic that isn't Learned yet.
- **Replayed, like everything else.** Credits are worked out from the event log each visit and replayed in time order with the card's own reviews; nothing is stored. The result doesn't depend on the order the events arrive in. Since a topic's card now depends on events in other topics, the topic page reads the whole history, as the map and the Today page already did. That also closes the gap where a follow-up opened by a checkpoint's test could leave the topic page showing a different state from the map ([ADR-0011](0011-mistakes-come-back.md), amendment of 2026-11-11).

**How existing schedules move.** Every card is replayed, so the rule covers past events at once and nothing stored changes. A topic moves only if something built on it was reviewed Good or Hard, or proved, while it was at least half way to due; every other card keeps its date exactly. Nothing moves earlier. Worked examples, for a topic Learned on day 0 whose first review is due on day 4 (stability 3.71 days):

| What happened                                                                                        | Next review, before | Next review, now                   |
| ---------------------------------------------------------------------------------------------------- | ------------------- | ---------------------------------- |
| The next topic's build passed on day 2 (share 0.5; a Good review that day would have meant day 12)  | day 4               | day 8                              |
| The same, and a review of that next topic rated Good on day 6                                        | day 4               | day 18                             |
| A third credit on day 12                                                                             | day 4               | day 18: it waits for a real review |
| One credit on day 3, from one, two or three steps up (shares 0.5, 0.25, 0.125)                       | day 4               | day 9, 7 or 5                      |
| A credit on day 1                                                                                    | day 4               | day 4: not half way yet            |
| Due on day 4 and not reviewed (the day's 20 were used), then used on day 30                          | overdue             | day 44                             |
| Its own review on day 4 rated Again, then a credit on day 6                                          | day 5               | day 5: relearning                  |

After a real review the schedule is plain FSRS-4.5 again, from the state the credits left: in the second row, a review on day 18 rated Good finds recall at the 90% target and grows the stability from there.

**The review load, simulated.** `npm run sim:reviews` (in `web/`) runs a made-up learner through cloud Modules 1 to 3 (38 topics and 3 checkpoints, 11,060 minutes) with the real topic graph and this scheduler: an hour of new study a day, every due review done, each of a review's two items right with the chance the card predicts. Averages of 20 runs over 365 days:

| | Reviews in the year | A day, on average | Busiest day | A day, last 30 days | Rated Again |
| --- | --- | --- | --- | --- | --- |
| Without implicit credit | 167 | 0.46 | 3.3 | 0.20 | 1.4 |
| With it, if credit is right | 114 | 0.31 | 2.6 | 0.09 | 0.7 |
| With it, if credit is worthless | 129 | 0.35 | 3.1 | 0.13 | 4.1 |

"Worthless" is the worst case: the schedule follows the credited card while the learner remembers only what the card without credit says, so reviews come late and more fail (4.1 Agains in the year instead of 1.4). Credit removes about a third of the reviews in Modules 1 to 3. Run over all 31 modules' outlines (376 topics, two hours a day, 1,100 days, 3 runs), it removes about a tenth (1,968 reviews to 1,789; 1.8 a day to 1.6; the busiest day 6.7 either way), because an outline's only prerequisite is usually its module's checkpoint, which credit doesn't cross; written topics list more. Neither run comes near the cap of 20 a day: at 90% retention FSRS's intervals grow fast enough that this learner never has more than about 7 reviews in a day. The rule earns its place by sparing reviews of what the learner keeps using, not by holding the cap.

**Alternatives considered.**

- _Direct prerequisites only._ Simpler, but most topics list one prerequisite, so nearly all credit would go to one topic each.
- _Adding up the shares from every path._ A topic reached by three paths would get more than a direct prerequisite does. The shortest path is the conservative reading.
- _Counting practice answers._ They're given while learning, with hints; a correct one says the hint worked as much as that the earlier topic is remembered.
- _A credit as a review with a weight inside FSRS's formulas_ (a "fractional grade"). FSRS has no such thing, and the result would no longer be FSRS-4.5 between real reviews. Moving the due date part of the way to a Good review's keeps the scheduler exact and the rule easy to state.
- _Moving the last review's time forward too._ That would restart the forgetting curve at the credit, as a real review does, which overstates what using a topic inside another shows.
- _No credit before a topic's first real review._ The first weeks are when the next topics use it most, and Mastered still needs a real review a week on, so holding credit back there would cost the most reviews for no protection.

## Amendment (2026-11-16): a slow right answer makes a review Hard

- **Status:** Proposed. Designed under the owner's delegation of 2026-11-11 (the best learning experience, then the best memory retention, then free) and built on until the owner rules; it is listed in [the owner queue](../owner-queue.md) under _Decided for you_.

Until now a session with every item right was Good, however long it took. Getting a question right after five minutes of digging is not the same as getting it right at once: the memory is there, but fading, and a review that comes a little sooner is the one that strengthens it. Every graded event already carries `duration_ms`, from the learner's first click or focus in the item to the answer ([data-model.md](../specs/data-model.md)). "Later" above named answer time as a way to tell Good from Easy; it is used the other way first, to tell Good from Hard, because Easy isn't used and a slow success is the case that costs retention.

- **The rule.** A session whose items are all right is rated Hard instead of Good when one of those answers took more than **three times** the learner's usual time for that kind of item **and** more than **a minute**. Some right and none right are rated as before; time only ever turns a Good into a Hard. Code `web/src/reviews/answerTime.ts`.
- **The learner's usual time** is the median of their most recent **50** timed right answers of that kind of item, from practice, proofs, reviews and the Today page's follow-ups (not the placement test). A kind is a question's type (multiple choice, predict the output, Parsons, predict the shell, estimate, and any added later) or a Python exercise's stage (fill-in, write, review). Kinds with fewer than **10** timed right answers aren't judged at all. Times over **30 minutes** count as 30, as in the practice-hours tracker. The skill index now carries each question's type and marks labs, so this needs no topic downloads.
- **Not timed:** a missing time (an item answered without a click inside it first), answers carried over from an earlier visit (only this visit's are), and labs, whose time includes building and starting a container and says nothing about memory. Each of those simply can't make a session Hard.
- **Why these numbers.** Three times the median keeps ordinary variation out: response times to questions a learner knows are skewed, and most land within twice the median, while a retrieval that needed working out again is several times longer. The minute keeps careful reading out: a quick check usually takes 10 to 20 seconds, and 45 seconds over that isn't struggle. Ten answers is the least that gives a median steady enough to judge by; fifty recent ones let the usual time follow a learner who gets faster. All are guesses until the learner's own data tests them, which the review log now records for: a review event says which right answers were slow (`data.slow`).
- **What the learner sees.** "Hard: all right, but one took much longer than you usually need. Next review in N days, a little sooner, while it's still there to strengthen." A Hard isn't a failure: it doesn't start Mastered's week over ([ADR-0002](0002-mastery-and-gating.md)), and with every answer right there's no follow-up. It does make this review unable to be the one Mastered needs, since that needs a Good.

**How existing schedules move.** They don't. A review event stores its rating, and cards are replayed from the stored ratings, so every session saved before this change keeps the rating it was given and the schedule it led to. Only sessions finished from now on are rated with time. Re-rating old sessions from their answers' times would change ratings the learner was shown, and the timing data for them (which answers came from which visit) can't be told apart reliably.

**Alternatives considered.**

- _A fixed time per kind, the same for every learner._ Simpler, but a careful reader would get Hards for reading, a quick one never.
- _The learner's time for that very item._ Most items are answered two or three times in all, too few for a usual time.
- _Easy for a fast session_, as "Later" first suggested. Easy lengthens intervals, which a fast lucky guess shouldn't do, and FSRS's Easy bonus is large; it would need its own evidence.
- _Timing labs too._ A lab's time is mostly the container; a slow lab says little about the learner.

## Amendment (2026-11-16): a personal forgetting curve

- **Status:** Proposed. Designed under the owner's delegation of 2026-11-11 (the best learning experience, then the best memory retention, then free) and built on until the owner rules; it is listed in [the owner queue](../owner-queue.md) under _Decided for you_.

"Later" above deferred personal FSRS parameters to the ML capstone. That stays: fitting FSRS's seventeen parameters is the capstone's job. What is built now is the smallest honest step toward it, in `web/src/reviews/personal.ts`: one number, fitted to the learner's own reviews, that says how many times longer (or shorter) their memory lasts than the average curve says.

- **The number.** A stability multiplier between **0.5 and 2**. Every interval becomes the card's stability times it, rounded to whole days as before, and the map's memory percentage uses the same stretched curve, so it still reaches 90% on the due date. The memory state itself stays plain FSRS-4.5, and so do the rules that read it (implicit credit's half way, for one).
- **How it's fitted.** At each real review the replayed card predicted a chance of remembering, from the stability just before it and the days since the last review (implicit credits included). The multiplier is the one under which what actually happened is most likely (maximum likelihood). It is searched over 0.5 to 2 in 400 even steps on a log scale, which for one number needs nothing cleverer and can't fail to converge, then rounded to the nearest 0.05, so one more review doesn't nudge every date.
- **What counts as remembering.** A review rated Good or Hard; Again is forgetting. That is FSRS's own definition (its optimizer counts every grade but Again as a success), and it is what the 90% target means: the scheduler aims for nine reviews in ten not rated Again. Counting only Good as remembering would quietly change the target to "nine in ten with both items right" and pull every learner's multiplier down, since Hard is common with two items.
- **When.** Only from **100** review outcomes; below that the multiplier is 1 and nothing changes. On simulated learners, a few thousand reviews pin it to within 0.15, and a hundred give a first estimate that the 0.5 to 2 clamp keeps from extremes: at most, reviews come twice as often or half as often as the average curve says.
- **It corrects implicit credit too.** The fit compares predictions made with credits in. If credit from practising later topics turns out to be worth less than the share it's given, the reviews after it fail more often than predicted and the multiplier falls, bringing reviews sooner.
- **Where it shows.** The Account page has a section, "Your forgetting curve", in plain words: "You forget a little faster than average: reviews come about 20% sooner", or the number of reviews still to go before it's fitted. Nothing is stored: it's worked out again from the event log on every visit, over every topic's reviews (the progress is now worked out for every bundled topic, not only the page's own).

**How existing schedules move.** Below 100 review outcomes, not at all: the multiplier is 1. From the visit on which the hundredth outcome is in the log, every card's next review moves at once to its last review plus the multiplier times its stability, and nothing stored changes. With a multiplier of 0.8, a card due 15 days after its last review becomes due after 12, one due after 49 days after 39; with 1.25, 15 becomes 19 and 49 becomes 61. Ratings, the rule for Mastered and the daily limit are untouched. The multiplier is fitted again on every visit, so it follows the learner as reviews accumulate.

**Alternatives considered.**

- _Fitting all of FSRS's parameters._ The capstone's job, and it needs far more than 100 reviews to do better than the defaults.
- _A multiplier on the elapsed time, or a different retention target._ Equivalent for one review, but a stability multiplier reads plainly ("your memory lasts 20% less long") and leaves the target, a product decision, alone.
- _Shrinking toward 1 with a prior_ (a Bayesian fit). A gentler start, but one more idea to explain; the threshold and the clamp do the same job here.
- _Storing the fitted number._ Recomputing it is cheap, keeps the event log the only record, and means a change to the rule applies by replay.
