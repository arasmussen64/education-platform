# Decision records

We record significant decisions as short ADRs (Architecture Decision Records), so future us, and future Claude sessions, know _what_ was decided and _why_.

## When to write one

When a choice is hard to reverse, affects many parts of the platform, or would make someone later ask "why did we do it this way?" Product decisions count, not just technical ones.

## How

1. Copy [template.md](template.md) to `NNNN-short-title.md`, using the next number.
2. Set the status to **Proposed** and fill it in.
3. When the owner accepts it, the status becomes **Accepted**.
4. Never delete or rewrite an accepted ADR. To change a decision, write a new ADR and mark the old one **Superseded by ADR-NNNN**.

## Index

| ADR                                     | Title                                                                    | Status   |
| --------------------------------------- | ------------------------------------------------------------------------ | -------- |
| [0001](0001-record-decisions.md)        | Record decisions as ADRs                                                 | Accepted |
| [0002](0002-mastery-and-gating.md)      | Mastery definition and gating                                            | Accepted |
| [0003](0003-ai-roles-and-guardrails.md) | AI roles and guardrails                                                  | Accepted |
| [0004](0004-content-model.md)           | Content model                                                            | Accepted |
| [0005](0005-free-hosting-first.md)      | Free hosting first                                                       | Accepted |
| [0006](0006-working-name.md)            | "Switchback" is a working name                                           | Accepted |
| [0007](0007-tech-stack.md)              | Tech stack                                                               | Accepted |
| [0008](0008-event-log.md)               | Learner data is an append-only event log                                 | Accepted |
| [0009](0009-reviews.md)                 | Reviews are per topic and graded automatically                           | Accepted |
| [0010](0010-environments.md)            | Local Supabase in Docker for development; one cloud project for real use | Accepted |
| [0011](0011-mistakes-come-back.md)      | Mistakes come back as fresh questions until relearned                    | Accepted |
| [0012](0012-checkpoint-support.md)      | Getting unstuck on a checkpoint                                          | Accepted |
| [0013](0013-explain-grading.md)         | Grading explanations with Claude, through the AI proxy                   | Accepted |
| [0014](0014-cloud-labs.md)              | Proving cloud skills with labs in the learner's own clouds               | Accepted |
| [0015](0015-hint-only-tutor.md)         | The hint-only tutor                                                      | Accepted |
| [0016](0016-parsons-problems.md)        | Parsons problems as a recall item type                                   | Accepted |
| [0017](0017-shell-in-the-browser.md)    | Teaching and proving the shell                                           | Accepted |
| [0018](0018-lab-checker-local-mode.md)  | The lab checker's local mode                                             | Accepted |
| [0019](0019-today-across-tracks.md)     | Today shows every track, and counts practice hours per track             | Accepted |
| [0020](0020-automated-backups.md)       | Nightly encrypted backups of the learning data                           | Accepted |
