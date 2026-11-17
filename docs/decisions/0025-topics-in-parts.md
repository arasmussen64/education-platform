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
