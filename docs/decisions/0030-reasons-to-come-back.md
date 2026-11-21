# ADR-0030: Reasons to come back: an open question, a proof's moment, fading memory, and how hard it's been

- **Status:** Accepted (the owner asked for these four on 2026-11-21: "Build 2, 3, 4, and 7", from a list of what would make learning here habit-forming). The details below were chosen while building; say the word to change any.
- **Date:** 2026-11-21

## Context

The owner asked what would make the app "as addictive as possible". The app already makes starting easy ([learning-science.md, "Habits"](../learning-science.md#habits)): one button for the day's session, a five-minute version, weeks counted instead of a daily streak, a study plan. What it lacked was pull: nothing at the end of a sitting that makes the next one wanted, no moment when a topic is proven, and no view of what is being lost by staying away.

The usual tools for pull are streaks, points, badges and random rewards. [learning-science.md](../learning-science.md#myths-we-avoid) already rules them out, for reasons that still hold: they reward time in the app, not learning, and a streak turns one missed day into a reason to stop. So the question was which kinds of pull can be built from true things about the learner's own work. Four were asked for.

## Decision

Nothing here changes what counts as learned, a review's rating, or any saved event. No migration, no new event type, no service.

### 1. A sitting ends on an open question

People want to get back to a task they left unfinished (Ovsiankina, 1928) and tend to remember it better than a finished one (Zeigarnik, 1927; the memory half has replicated less well than the urge to resume). And a guess made before being taught helps the answer stick, even a wrong guess (Richland, Kornell & Kao, 2009), which is why lessons open with a puzzle ([ADR-0026](0026-lesson-building-blocks.md)).

- **Where.** At the end of the guided session and of its five-minute version, in the moment a topic is proven (below), and on a topic page under "Stopping here for today?", folded until asked.
- **A topic not yet started** is asked about by its lesson's opening puzzle: the question only. The learner types a guess, and the answer stays in the lesson. A lesson with no puzzle asks how the learner would do the topic's first goal today. (49 lessons have a puzzle so far.)
- **A topic in progress** shows its next unanswered question (lesson questions, then practice, then the build and the debug), with the program or command it is about, and no way to answer it there. Answering belongs on the topic page, where it is graded and saved.
- **The guess is kept on this device only**, in `localStorage` (`guess:<topic id>`), like the remembered part of a topic. It is not an event: it is not graded, not sent, and losing it loses nothing that counts. The Today page shows it back ("Your guess is waiting") with a link to the topic. In the lesson, the puzzle opens with the guess filled in, and it is forgotten once the answer shows. A guess about a goal shows at the start of the lesson until the learner puts it away or proves the topic.
- **The build step that measures a lesson** (`remarkLessonShape`) also exports the puzzle's question, so a page can ask it without rendering the lesson.

### 2. Proving a topic gets a moment

People judge an experience by its best moment and by its end (Kahneman, Fredrickson, Schreiber & Redelmeier, 1993). Passing the last proof was marked only by a line of the proof list changing.

When the last proof passes during a visit, the topic page shows a panel above everything else and moves focus to it. It holds only facts from the learner's progress:

- what the proof was (built from a blank editor, fixed unfamiliar code, explained, no hints), and the topic's goals unfolded and ticked;
- the module's progress bar growing from where it stood to where it stands ("7 of 8 topics proven in Module 2"), and "That is the whole module" when it is;
- the topics this one opened: those built directly on it whose other prerequisites were already learned;
- when its first review comes, and what makes a topic Mastered;
- the open question about the topic that is next (section 1).

It appears once, in the visit that earned it, and never on a later visit. The bar is the only movement, runs once, and stays still when the system asks for reduced motion. It is a progress fill, so it is lime under the Momentum rule; the tick is green, as proven things are. No points, badges or confetti, and nothing in the panel can be had without the proof.

### 3. The Today page shows memory fading

People work harder to keep something than to gain it (Kahneman & Tversky, 1979). A streak uses that with an invented loss. The scheduler already holds a real one: its estimate of the chance each learned topic is still remembered ([ADR-0009](0009-reviews.md)), which the map shows per topic.

- **"Your memory"** on the Today page lists the five learned topics remembered least well, weakest first: the estimate now, the estimate a day from now if nothing is done ("at 84% and dropping: 82% by tomorrow"), and either "its review is due: about 2 minutes to keep it" (from the learner's own review times) or when the next review comes. One sentence says how many have faded enough to need a review.
- **The session card** names what its first review is there to keep: "The most faded is DNS, at 84% and dropping: 82% by tomorrow."
- The numbers are the scheduler's, rounded to whole percentages. When a day changes nothing a whole percentage can show, it says "holding for now" instead of inventing a drop. The list is fixed when the page loads, like the sections above it.

### 4. How hard practice has been, against 85%

For a wide class of learners, training goes fastest when about 85% of answers are right (Wilson, Shenhav, Straccia & Cohen, 2019). The result was derived for simple learning systems and yes-or-no questions, so it is used here as a guide with a wide band, and never as a grade.

- **The measure** is the share of quick questions got right on the first try, in lessons and practice. Left out: second tries (easier than the question), Checks of programs (a first Check often fails on a typo), reviews (scheduled to be about 90% right), proofs, the placement test, and "Check what you know".
- **Bands.** 95% and up is "easy", under 70% is "hard", between is "about right". The overall figure looks at the last 40 first tries and says nothing before 20; a topic's needs 8.
- **The Account page** gets "How hard it's been": the figure, what it means, what to do, and the topics furthest from 85%, which is also where the content may want a look.
- **A topic's practice** shows a note only when its own figure is easy or hard: easy points to the proofs, hard points back to the lesson. Both are existing ways through the page ([ADR-0025](0025-topics-in-parts.md)'s "Prove it now" and the lesson's parts); the note only chooses which to suggest. Between the bands, which is most of the time, nothing shows.

## Alternatives considered

- **Daily streaks, points, badges, leaderboards, random rewards.** They do raise time in the app. They are ruled out in [learning-science.md](../learning-science.md#myths-we-avoid), and the four things above get their pull from the learner's real progress instead.
- **Saving the guess as an event.** It would follow the learner across devices and add to the log. But the log is graded work and what the learner did with it; an ungraded guess is neither, and `localStorage` needs no schema. If guesses turn out to be worth studying, a later ADR can add an event.
- **Showing the puzzle's answer at the end of the session** once a guess is typed. That closes the question, which is the opposite of the point.
- **A proof moment with animation beyond the bar** (confetti, a badge). Rejected for the reason [progress/modules.ts](../../web/src/progress/modules.ts) gives: the proof is the reward, and decoration makes it look like the app's gift.
- **Showing the proof moment on every later visit.** It would stop being a moment; the goals stay ticked and the header says when the topic was learned.
- **A memory percentage for the whole track, as one number.** Easier to read, but an average hides the one topic about to be lost, and the action is per topic.
- **Changing which questions are asked to hit 85%** (adaptive difficulty). The items are written and validated one by one ([ADR-0004](0004-content-model.md)); there is no pool of easier and harder versions to choose from. The existing levers are skipping practice and going back to the lesson, so the note points at those.
- **Counting first Checks of exercises in the 85% figure.** A first Check that fails on a missing colon says little about difficulty, and it would pull the figure down for everyone.

## Consequences

- A learner who stops for the day is left with a question, and finds it waiting on the Today page. One who guesses on a phone and returns on a laptop finds no guess there: it is per device.
- Lessons without a puzzle get the weaker goal question. Writing a puzzle for the other ready lessons is content work, and each one improves both the lesson and the session's end.
- A puzzle's question is now also read on its own, before its lesson, so it has to make sense without the lesson around it. [content/README.md](../../content/README.md) says so.
- The proof moment loads the next topic's content to ask its question, one more download at a moment when the learner is reading.
- "Your memory" makes the Today page longer by one section once anything is learned.
- The 85% figure can mislead a learner with few answers or an unusual mix of topics; the minimum counts and the wide band are the guard. The topic list on the Account page is the first view of which topics' questions are too easy or too hard, for one learner. With more learners it should be worked out per question.
- A small fix came with it: the map's memory bar had no stated best value, so browsers coloured a fading topic as the good one and a fresh one as the poor one. It now says 100 is best.
