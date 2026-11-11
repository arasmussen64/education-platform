# Plan: Cloud Solutions Architect, Module 2

The writing plan for Module 2, "Virtualization, hardware and Windows", made on 2026-11-10 and 2026-11-11 before any of it was written. Four designers each briefed part of the module, researching and checking their facts and resources and trying the labs on a real machine; a critic then checked the briefs against each other and the house rules and wrote one plan.

**Start with [MODULE-2-BRIEF.md](MODULE-2-BRIEF.md).** It decides; the designers' briefs hold the detail. Where they disagree, the brief wins.

| File | What it is |
| --- | --- |
| [MODULE-2-BRIEF.md](MODULE-2-BRIEF.md) | The final plan: topic order, each topic's skills, practice, proofs and review pool, Checkpoint 2, the platform work, the cost of the optional Azure lab, and what to look up again on the day of writing |
| [CRITIQUE.md](CRITIQUE.md) | Every problem the critic found in the briefs, and what was done about it |
| `csa.hw.*.md`, `csa.m2.checkpoint.md` | The designers' briefs, one per topic (the cores-and-memory brief also covers the disks topic, and the Active Directory brief the domain-join topic, which the plan split out) |
| [estimate-questions.md](estimate-questions.md) | How a number-with-tolerance question should work, and how prices live in content |
| [price-fixture-2026-11.md](price-fixture-2026-11.md), [.csv](price-fixture-2026-11.csv) | List prices read on 2026-11-10 and 2026-11-11, with their sources. Correct them as the plan's section 3.6 says before any is used |
| `ADR-DRAFT-*.md` | Drafts of the decisions the platform work needs. Each becomes an ADR or an amendment when it is built |

The prototypes the designers built (the Samba domain controller labs, the QEMU and cross-compile trials, the capture script and a capture of the owner's laptop with its CPU model masked) are in [`tools/generators/cloud-labs/module-2-prototypes/`](../../../tools/generators/cloud-labs/module-2-prototypes/). They are an archive, like the rest of that folder: nothing runs them in CI, and a lab is only real once it is written under `content/topics/` and passes `tools/labcheck.py test`.

**This is a plan, not the source of truth.** Once a topic is written, its files under `content/topics/` are what counts. Prices, product names and licensing rules in these files were true on the dates they give and must be checked again when a topic is written.
