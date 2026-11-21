# ADR-0026: Lesson building blocks: questions, a puzzle, a real incident, and a glossary

- **Status:** Accepted by the owner on 2026-11-21 ("I accept all the ADR decisions you listed"). It was designed and built on under the owner's delegation of 2026-11-11, and listed in [the owner queue](../owner-queue.md) until then.
- **Date:** 2026-11-16

## Context

A lesson (`lesson.mdx`, [ADR-0004](0004-content-model.md)) is the platform's own intro and recap around the main resource. In the cloud track an intro runs to 2,000 words or more, and until now it was only prose: the learner reads all of it, then meets the first question in the practice ladder below. Four things the research behind the platform ([learning-science.md](../learning-science.md)) says help were missing from the lesson itself:

- **Questions while reading.** Short tests placed between the parts of a lesson cut mind-wandering and improve what's learned from it (Szpunar, Khan & Schacter 2013).
- **Curiosity first.** People remember information better when they wanted to know the answer first (Gruber, Gelman & Ranganath 2014), and guessing an answer before learning it helps even when the guess is wrong (pretesting; Richland, Kornell & Kao 2009).
- **A real story.** The cloud track teaches how real systems fail. A short account of a real public outage the topic explains gives the ideas a reason to matter and a concrete case to remember them by.
- **Words from earlier topics.** A lesson uses terms other topics taught (NAT, page cache, cgroup). A learner who has forgotten one has to leave the page to find it.

Every addition has to keep what makes content safe to write: files in git, checked by `tools/validate_content.py` before a learner can open them, with MDX stopping the whole page at a tag the app doesn't know.

## Decision

Lessons gain four building blocks. Each is written in `lesson.mdx` (or, for the glossary, a file beside it), drawn by the app, and checked by the validator. [content/README.md](../../content/README.md#lesson-building-blocks) says how to write each.

1. **`<Check item="<item id>" />`** asks one of the topic's own practice quick questions inside the lesson. It's drawn by the same component as the practice ladder, so every question type works, including types added later, and it's graded and saved exactly as in practice (an `answer` event, context `practice`). The item stays in `topic.yaml`'s `practice:` list and counts like the rest of the ladder; the page shows it once, in the lesson, and the ladder leaves it out. Compiling a lesson adds `export const checks = [...]` to it (`web/src/tooling/remarkLessonChecks.ts`), so the page knows which items those are without rendering the lesson first. Rules: the item must exist, be a quick question (not an exercise), be listed in `practice:`, and be placed once.
2. **`<Puzzle question="…">answer</Puzzle>`** opens the intro with a puzzling question. The learner types a guess before "Show the answer" reveals it. The guess is **not graded and not saved anywhere**, not even on the device: it lives while the page is open, and is shown beside the answer for comparison. A puzzle is first in `<Intro>`, one per lesson, with a question of at most 50 words and an answer of at most 150.
3. **`<Story title="…" source="https://…" sourceTitle="…" license="…">…</Story>`** tells a real public incident the topic explains, in the platform's own words, with a link to the postmortem or reputable report it's drawn from. The writer must have opened the source, never copies its text (ADR-0004), and records its licence, or `linked, not copied`, in `license`, which the page shows beside the link. The source must be an `https://` link, and the story at most 200 words.
4. **A glossary.** A topic lists the terms it teaches in `content/topics/<id>/glossary.yaml`: `term`, optional `aliases`, and a `definition` of at most 40 words. A term (or alias) may be defined by one topic only, across all content, ignoring case. While the app is built, the first time a lesson uses a term from another ready topic it's marked with a dotted underline; pressing it (or hovering with a mouse) shows the definition and "Taught in: <topic>", linking to that topic. Terms are marked only in lesson prose, never in headings, links, code, a puzzle, or practice questions, where a definition could give an answer away. A topic's own terms aren't marked on its own page. A `/glossary` page lists every term.

Only `Intro`, `Resource`, `Recap`, `Check`, `Puzzle` and `Story` may appear in a lesson; the validator rejects any other component tag (and a hand-written `<Term>`, which only the glossary adds). No new event types: a lesson question records what a practice question records, and the puzzle and glossary record nothing.

## Alternatives considered

- **Questions written straight into the MDX**, with their own answer and explanation. They would have been a second kind of question the validator, the review pool and mistakes coming back (ADR-0011) don't know. Placing an existing practice item keeps one kind.
- **Showing a placed question in both places.** Answering the same question twice in five minutes is rereading, not retrieval, and makes the ladder look longer than it is.
- **Saving the puzzle's guess,** as an event or on the device. An event type for an ungraded guess would add a kind of learner data with no use in progress or reviews, and a guess saved on the device would greet the learner with their old guess, which spoils the second attempt. The benefit comes from making the guess, not from keeping it.
- **Grading the puzzle.** A pretest works because a wrong guess costs nothing; a mark would make it a test, and a learner reluctant to guess wrong.
- **Stories as a resource or a link only.** A link alone sends the learner away to a long postmortem written for engineers who already know the topic. A short retelling, with the link for the curious, keeps the lesson on the page.
- **A glossary marked in the browser, from one index of every term.** Every page would download every definition, and the "first time on the page" rule is hard to keep in React (a component can render twice). Marking at build time puts in each lesson only the few definitions it uses, and loads them with it.
- **Marking terms in practice questions too.** A question that asks what NAT does would carry its own answer one tap away.
- **Linking a term on its own topic's page.** There, the lesson is where the term is taught; a link back to the same page helps no one.

## Consequences

- Writers can interleave questions, open with a puzzle and tell a real incident without touching code, and the validator stops a broken tag before a learner sees it.
- A placed question is still a practice item everywhere else: in reviews, in mistakes coming back and in the skill index. Only the ladder's numbering changes ("Practice 1 of 4" where the topic lists five).
- Stories add a source to keep alive, like resources (ADR-0004): a moved postmortem is a broken link to check for.
- Glossary definitions are copied into each lesson that uses them when the app is built. A changed definition reaches every lesson at the next build; on the dev server, after a restart.
- Each block's word limit is a judgement call to revisit after the owner has read lessons that use them.
