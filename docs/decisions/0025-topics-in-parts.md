# ADR-0025: A topic page in parts

- **Status:** Proposed
- **Date:** 2026-11-16

## Context

A topic's whole page was one long scroll: the lesson, every practice item and the three proof checks. The cloud track's topics are estimated at 220 to 325 minutes, with 20 to 30 quick questions and five labs each, so a learner who sat down for half an hour faced a page of several hours with no natural place to stop. The outline beside the page (2026-11-09) and the "Back to top" button (2026-11-16) helped them find their way around it, not to see it as a few sittings.

Two things from the research bear on this. Work in short, bounded sessions keeps attention and leaves room for the rest that consolidation needs (Dewar et al., 2012, on quiet rest after learning; the spacing literature in [learning science](../learning-science.md)). And an end you can see is motivating: "Part 2 of 5, about 30 minutes" is a goal a learner can plan around in a way "300 minutes" isn't.

## Decision

A regular topic's page shows **one part at a time**:

1. **Learn**, the lesson, is part 1.
2. **The practice ladder** (`practice:` in topic.yaml, in order) is cut into parts of about 30 minutes each, and at most about 40 where the items allow it. A ladder of 40 minutes or less stays one part.
3. **Prove it**, the three proof checks, is the last part.

**How long things take.** Only the topic's total is written down (`estimated_minutes`). The page guesses the rest with the figures authors use to work that total out (content/README.md): a quick question 1.5 minutes; a Python exercise 5 to 12 minutes by its stage; a lab 20 to 50 by its stage; an explanation 15. Where those guesses leave the lesson less than a quarter of the total (short Python topics, whose exercises are quicker), they're scaled down so the lesson keeps that quarter. Either way the parts add up to the total at the top of the page. The figures live in one file, `web/src/parts/estimates.ts`, with the reasons beside them.

**Where the practice is cut.** Among all the ways to cut the ladder into that many parts, keeping its order, the page takes the one whose parts are closest to equal (the smallest sum of squared differences from the average), with a small extra cost for cutting between two quick questions. So a cut falls where the kind of work changes, a run of questions giving way to a lab, when that moves a part only a few minutes from equal.

**What each part shows.** "Part 2 of 5 · about 30 min" above its heading. A practice part's heading says what's in it ("Practice: worked example and 8 questions"); practice items keep their numbers across the whole ladder ("Practice 21 of 28"), as the outline numbers them. Buttons below the part go to the previous and next parts.

**The outline** lists every part with whether it's done, and inside each its places: the lesson's, every practice item with its state, the proof checks. Any link there, or any link to a place on the page (`#place-recap`, `#place-item-…`, `#place-prove-build`, a part's heading), opens the part that holds it and scrolls to it. The address keeps the place after the `#`, so a reload or a shared link opens the same part. An id the page doesn't know comes from the lesson's own text, so it opens the lesson.

**Done, and where the page opens.** Nothing new is stored on the server. A practice part is done once every item in it has been got right, from the saved answers, as the practice items' own marks already are. The proofs are done once all three have passed. The lesson has no answers of its own, so it counts as done once the learner has tried anything in the topic's practice or proofs. The page opens at the part a link points into; otherwise, once the progress is known, at the part last viewed on this device if it isn't done, or else at the first part that isn't done. The last part viewed is kept in the browser's localStorage, as the last place already is, and the page works the same without it. That choice is made once per visit: finishing a part never moves the learner on by itself.

**Unchanged.**

- Parts never gate anything. Any part can be opened at any time, from the outline or the buttons.
- Mastery, the proofs and gating are as [ADR-0002](0002-mastery-and-gating.md) has them. A Locked topic shows its lesson only, so it has one part and no part navigation. "Prove it now" opens the proofs part.
- Checkpoints aren't cut into parts. They have no lesson or practice, only proof checks with their own way through ([ADR-0012](0012-checkpoint-support.md)).
- Items already done when the page opens are still folded away; items in a part that isn't on screen aren't rendered at all.

## Alternatives considered

- **Keep one page, with better navigation.** The outline already does that. It helps a learner find their place, but the page still reads as one sitting of several hours.
- **Hide parts but keep them rendered.** Moving between parts would keep an unanswered question's state, but every exercise's editor would stay loaded, and a playing lesson video would keep playing out of sight. Code and explanations are already kept as drafts on the device, so little is lost by rendering only the part on screen.
- **Write the parts into topic.yaml.** Authors would choose the cuts, but 487 topics would need editing, and every change to a ladder would need the parts redone. Working them out from the ladder needs nothing from content, and the cuts move with it.
- **Count a part done when the learner opens the next.** That would need storing, and it would let a learner tick a part off by clicking past it, which ADR-0002 rules out for anything that looks like progress.
- **Make parts gate.** Requiring each part before the next would slow down a learner who already knows the material, which "Prove it now" exists to avoid.

## Consequences

- A long topic reads as a few sittings of about half an hour, each with an end in sight. The lesson and the proofs can still be long (about 60 to 120 minutes for a cloud topic's lesson with its readings, about 90 for its labs), since the decision keeps each as one part. Each proof check, and each part of the lesson, is a natural place to stop.
- The times are guesses. They're right on average for a topic, because they add up to its total, but a part's own figure can be some minutes out. If a learner's recorded attempt times show the guesses are wrong, the figures in `estimates.ts` are the one place to change.
- A part that isn't on screen isn't rendered, so moving away from an answered multiple-choice question and back shows it fresh, marked Done in its header.
- A later change that places practice questions inside the lesson (a lesson's own `<Check>`) takes those items out of the ladder before it's cut, so they count toward the lesson's part.

## Amendment (2026-11-16): a short break between parts

- **What.** Pressing Next after finishing a part shows a small card above the next part suggesting a five-minute break: rest quietly, eyes closed or looking away from screens, rather than picking up a phone. It has an optional five-minute timer that runs on the page only, and a Skip button. The next part is open underneath the whole time; keyboard focus goes to the card first, so a screen reader reads it; and the card goes away when the learner jumps anywhere else. No browser notifications.
- **When.** Only on moving forward with the Next button from a finished part: the lesson (it has no answers, so going on from it is finishing it), or a practice part whose items are all Done. Not on moving on from an unfinished part, and not on jumping from the outline, which is looking around rather than finishing.
- **Why.** A few minutes of quiet, wakeful rest straight after learning improves how much is remembered a week later, compared with doing another task in those minutes (Dewar, Alber, Butler, Cowan and Della Sala, 2012, "Brief wakeful resting boosts new memories over the long term", _Psychological Science_). The parts give a natural moment to offer it.
- **What it doesn't do.** It records nothing and changes nothing about progress. Time on the timer isn't practice time.

## Amendment (2026-11-16): "Check what you know", before the practice

- **What.** At the top of a topic's first practice part, a signed-in learner who hasn't taken it yet (and whose topic isn't Learned) is offered a quick check: three to five of the topic's own quick questions. When started, it takes the practice's place until the learner goes back. Afterwards, each practice item whose skills were all shown is marked **optional**: folded behind a dashed line saying "Optional: you seem to know this, from your quick check", dashed in the outline, skipped by "Next not done", and not holding its part's tick back. The proofs stay required: nothing about Learned, Mastered or gating changes ([ADR-0002](0002-mastery-and-gating.md)). It sits between doing all the practice and "Prove it now", which skips it all.
- **Which questions.** Only multiple choice, predict the output (Python or shell) and estimates from the topic's `practice`, since they're quick and graded on the spot (Parsons problems take longer). For each of the topic's skills in turn, the first such question that tests it, up to five; if that makes fewer than three, more questions to make three. A topic with fewer than three such questions doesn't offer it. The pick is the same every visit.
- **What counts.** Only each question's first answer in the quick check, as in a review: a second try after seeing the feedback shows less. A right first answer shows every skill the question names. An item is optional when every skill it names was shown; an item with no skills never is. A later wrong answer in the practice doesn't undo it; it opens a follow-up as usual ([ADR-0011](0011-mistakes-come-back.md)).
- **How it's recorded.** Through the existing event machinery, with no new event type and so no database change: each answer is an ordinary `answer` in context `practice`, with `quick_check: true` in its data ([data model](../specs/data-model.md)). It marks its item Done or Tried like any practice answer, which is honest, since it is that item answered. Which skills were shown is worked out from those answers on every visit, like the rest of progress; the history read takes the mark out of the data.
- **Not offered** to a signed-out visitor, whose answers aren't saved, so nothing could be marked; once taken (any answer in it); or on a Learned topic.

## Amendment (2026-11-21): a long lesson in parts, and times at the learner's pace

The owner asked for both ("Start building these things"), from the "Next" list of 2026-11-16.

**A long lesson is cut too.** The decision above kept the lesson as one part, so a cloud topic's first part ran 55 to 125 minutes.

- **Where.** A lesson can only be cut where it asks a question: after a `<Check item="…" />` written directly inside `<Intro>` ([ADR-0026](0026-lesson-building-blocks.md)). A lesson of 40 minutes or less stays one part, "Learn", as before.
- **How long each stretch is.** While a lesson is compiled, a build step (`web/src/tooling/remarkLessonShape.ts`) counts the words between its questions. The page turns words into minutes at 130 words a minute, the speed authors use to work a topic's total out (content/README.md), plus a minute and a half for each question. Whatever is left of the lesson's time belongs to the main resource and the recap.
- **The parts.** The lesson's own text is cut at its questions into parts of about 30 minutes, at most about 40, by the same rule that cuts the practice. The main resource and the recap become a part of their own, "Learn: the reading and the recap", when they take 15 minutes or more and the text before them does too; otherwise they stay with the last section.
- **What it does to today's topics.** Each of the 38 ready cloud topics now has two lesson parts: its own text, 10 to 37 minutes, and the reading with the recap, 32 to 73 minutes. The finance, Python and ML lessons are short and stay one part.
- **What it can't do.** The reading is somebody else's page or video, with no place of ours to cut it, so that part can still run past 40 minutes. It is the one kind of part that does. A test over every written lesson fails if any other part could have been cut and wasn't.
- **Done.** A lesson part that asks questions is done once each has been answered right, or once the topic is proven. One that asks none is done as before, once anything in the practice or proofs has been tried. Still nothing new is stored.
- **Places keep their numbers.** The lesson's blocks are numbered across the whole lesson (`place-lesson-7`), whichever part shows them, so a remembered place or a link opens the right part. The parts' headings are `#learn`, `#learn-2` and so on.

**Times at the learner's pace.** The Today page already stretches a topic's time when the learner's proven topics ran longer than their estimates (`web/src/progress/pace.ts`, 2026-11-16). The topic page now does the same.

- **What.** Once three proven topics can be measured and their median ran over the estimate, every time on the topic page is multiplied by that ratio before the parts are cut. So a learner whose topics take 1.5 times the estimate gets more, shorter parts, each still about half an hour of their own time, and the header says "About 450 minutes for the whole topic at your pace (1.5× the estimate of 300)".
- **Only stretched, never shrunk,** for the reason pace.ts gives: the measure is a floor.
- **Fixed for the visit.** The pace is read once when the page's progress loads, so proving the topic doesn't move the parts while the learner is on the page. Between visits the cuts can move when the pace changes by a tenth; the part last viewed is then looked up by its id, and if that id is gone the page opens at the first part not done.
- **Signed out,** or before three topics are proven, the page shows the estimates as written.
