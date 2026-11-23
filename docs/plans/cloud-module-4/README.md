# Plan: Cloud Solutions Architect, Module 4

The writing plan for Module 4, "Security and identity foundations", before any of it is written. It was made in two passes. On 2026-11-12 designers briefed the eleven topics and a payments-server lab base, each without sight of the others' work. On 2026-11-22 two more designers, who could read those briefs, designed the identity-lab base and the checkpoint, and a critic checked the briefs against each other, the house rules, Module 3 as written and a sample of their sources, ran two experiments again, and wrote one plan.

**Start with [MODULE-4-BRIEF.md](MODULE-4-BRIEF.md).** It decides; the designers' briefs hold the detail. Where they disagree, the brief wins. Then read section 0 of [CRITIQUE.md](CRITIQUE.md): the critic did not read every brief in full or re-check as many facts as planned, and it says which.

| File | What it is |
| --- | --- |
| [MODULE-4-BRIEF.md](MODULE-4-BRIEF.md) | The final plan: the topic order (one topic moved), the rules every item follows, how each lesson meets ADR-0025, 0026 and 0031, the five lab bases in their final form, each topic's changes to its designer's brief with its puzzle, incident and reading, Checkpoint 4, the platform work, the writing waves, CI time, decisions for the owner queue, what to look up again, and the replacement text for the spec |
| [CRITIQUE.md](CRITIQUE.md) | What the critic read and didn't, every problem found and what was done about it, the facts and incidents re-checked, the two experiments, and what is still unverified |
| [identity-lab-base.md](identity-lab-base.md) | The identity-lab base (`lab-base-id`): Keycloak on the network base, the realm file as the configuration, the scripted browser, clocks. The brief's section 4.1 decides its fourteen mismatches and adds the earlier image's time model |
| [lab-base-sec.md](lab-base-sec.md) | The payments-server base for audit, vulnerabilities and compliance. **Renamed `pay`** by the plan; the cryptography brief's section 10 designs a different base it also called `lab-base-sec`, now `vault` |
| `csa.sec.*.md` | The eleven designers' briefs, one per topic. They name topics by the spec's old numbers (strong authentication as 41, federation as 44); the plan names topics by id |
| [csa.m4.checkpoint.md](csa.m4.checkpoint.md) | The checkpoint's brief: three parts, the third new and not prototyped |

**The prototypes are not in the repository.** The briefs cite files under `prototypes/` (the identity base and a lab that kept its contract four at a time, the checkpoint's part 1 checker and part 2 lab, the critic's probes). They lived in the design session's scratch folder and become the real lab bases under `content/lab-bases/` as the platform work is done. The prototypes the eleven topic briefs of 2026-11-12 cite (`tm-zt/`, `authn-strong/`, `cps/`, `federation/`, `audit-vuln-compliance/`) no longer exist anywhere; what those briefs call "tried" has to be built and run again.

**This is a plan, not the source of truth.** Once a topic is written, its files under `content/topics/` are what counts. Prices, limits, product versions, licences and standards in these files were true on the dates they give and are checked again when a topic is written (the brief's section 11).
