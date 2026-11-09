# ADR-0016: Parsons problems as a recall item type

- **Status:** Accepted (2026-11-09)
- **Date:** 2026-11-09

## Context

The practice ladder goes from a worked example, through recall questions (multiple choice and predict-the-output), to half-finished code and then a blank editor ([ADR-0004](0004-content-model.md), [learning science](../learning-science.md)). The step from reading code to writing it is the steepest one for a beginner: they know what each line does, but putting lines together into a program that runs is new.

Parsons problems fill that gap: the lines of a short, working program are scrambled, sometimes with a decoy line or two that don't belong, and the learner puts them back in order. Research on novice programmers finds they teach program structure with less mental load than writing from scratch, and faster than fixing broken code, for the same learning (Ericson, Margulieux and Rick, 2017; Parsons and Haden, 2006). The learning-science notes have listed them as "early practice steps" since the start; the v1 spec left them out to ship.

The platform's rules for an item type: it must be machine-checked ([ADR-0004](0004-content-model.md)), it must name the skills it tests so a miss can come back as a different question ([ADR-0011](0011-mistakes-come-back.md)), and the validator must prove every item is right before it's marked ready.

## Decision

1. **A third recall item type, `parsons`.** A file in a topic's `recall/` folder, beside `mcq` and `predict_output` items, with the program's lines in the right order, each with its indentation, and an optional list of distractors. The prompt says what the finished program prints, so there is exactly one right order. The explanation says why.
2. **Checked by order.** The learner's program is correct when its lines are exactly the solution's lines in the solution's order, with no decoy. Lines keep their indentation; the learner orders them, as in the classic one-dimensional Parsons problem. Two-dimensional problems, where the learner also sets the indentation, can come later as an option on the item.
3. **The validator runs the lines in order** through the harness: the program must run without an error and without asking for input, the lines must be distinct and non-blank, and every distractor must differ from every line. So a Parsons item is proven the way a predict-the-output item is.
4. **In the app**, the item shows the scrambled lines in a tray and an empty program. Buttons move each line: add, up, down, remove. Buttons work with a keyboard and on a phone, which drag-and-drop doesn't without a lot more code; dragging can be added on top later. The scramble is fixed per item (seeded by its ID) and never the right order, so an item looks the same each time it comes back.
5. **Everywhere a recall item goes, a Parsons item goes:** the practice ladder (right after the worked example, where the research puts it), the review pool, follow-ups after a miss, interleaved questions, and review sessions, where it counts as "code or predict" rather than a choice. Its answer is an `answer` event whose data holds the program as the learner left it.

## Alternatives considered

- **Keep to multiple choice and predict-the-output.** Cheapest, but neither asks the learner to assemble a program, which is the skill the fill-in exercises assume.
- **Drag-and-drop first.** The expected interaction, but hard to make accessible and to test; buttons give the same ordering with far less code. Dragging is an enhancement, not a requirement.
- **Two-dimensional Parsons from the start.** Setting indentation is a real skill in Python, but it doubles the ways to be wrong and the UI. Start with the one-dimensional kind, which the research shows already carries most of the benefit.
- **Generate Parsons items automatically from exercise solutions.** Tempting, since every solution is a working program, but a good item needs a prompt that fixes the order, lines that aren't interchangeable, and a decoy that teaches something. Authors write them, a few per topic, like the other recall items.

## Consequences

- Beginners get a step between reading code and writing it, in the first topics especially.
- The content model, validator, web types, one component and the docs grow by one item type. The review-pool rule and the "code or predict" rule include it.
- Authors must write prompts that fix the order (say what the program prints) and avoid interchangeable lines; the validator can't catch an ambiguous item, so the content checklist says so.
- Learner events gain a `program` field in `answer` data; the event log stays append-only ([ADR-0008](0008-event-log.md)).
