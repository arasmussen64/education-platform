# The threat-model lab base

Every threat-modeling lab (the Cloud Solutions Architect track's `csa.sec.threat-modeling`, and part 1 of Checkpoint 4) starts `FROM lab-base-tm`. This folder is that image. `tools/labcheck.py` builds it, tagged `lab-base-tm`, before it builds any lab whose `Dockerfile` says `FROM lab-base-tm`, for `start` and `test` alike ([ADR-0018](../../../docs/decisions/0018-lab-checker-local-mode.md), third amendment).

Read this before writing a threat-model lab. The plan behind it is [docs/plans/cloud-module-4/MODULE-4-BRIEF.md](../../../docs/plans/cloud-module-4/MODULE-4-BRIEF.md), section 4.4, with the threat-modeling topic's brief (section 7, the format) and the checkpoint's (section 3, part 1).

## What's in the image

| Layer | What | Notes |
| --- | --- | --- |
| 1 | Module 3's plain labs' first `RUN`, byte for byte | Shared with every plain lab of Module 3 on, so Docker builds it once. Change it only with all of them. |
| 2 | `/usr/local/bin/tm-check` | The checker: one Python file, standard library only, on Ubuntu 24.04's Python 3.12. |

Nothing is downloaded from outside Ubuntu's archive. It is a plain base: no systemd, no network, no privilege. It ends with `USER learner`, `WORKDIR /home/learner` and `CMD ["sleep", "infinity"]`.

## A lab's folder and Dockerfile

```text
exercises/<lab>/
├── exercise.yaml      runtime: lab, lab: { restart_trial: true }
├── Dockerfile         below
├── design.md          the system, as facts: its parts, its flows, what is in place, the scales
├── checks.yaml        one tm-check part a check, each with the reference
├── solution.sh        writes the reference model
└── wrong/*.sh         each writes a model that is wrong in one way
```

```dockerfile
FROM lab-base-tm
USER root
COPY --chown=learner:learner design.md /home/learner/design.md
RUN install -o learner -g learner -m 644 /dev/null /home/learner/model.tm
USER learner
```

The base ends as the learner, so a lab's own lines run between `USER root` and `USER learner`. `restart_trial: true` passes trivially (the model is a file), and every lab still sets it. `csa.sec.threat-modeling`'s labs are the pattern; its first lab carries the threat-model onboarding.

## The format

A model is a text file, one fact a line, words separated by spaces. A word that starts with `#` begins a comment. **A line can only use names that lines above it define**, so zones come before elements and elements before flows; that is also what lets a learner's one-pass `awk` script read a model (the topic's write lab). `tm-check --help` prints this table in the lab, where there are no manual pages.

| Line | Shape | Rules |
| --- | --- | --- |
| `zone` | `zone NAME words` | A trust zone: one owner, one network. |
| `element` | `element ID external\|process\|store ZONE words` | The zone must exist. |
| `flow` | `flow ID FROM TO words` | Both ends are elements; `FROM` is the side that starts it. |
| `threat` | `threat ID FLOW LETTER L I RISK A/An ... can ...` | One STRIDE letter; likelihood and impact 1 to 3; the risk a whole number (`ranking` checks it is L times I); then a sentence of at least 7 words that starts with `A` or `An` and has `can`. |
| `none` | `none FLOW LETTERS reason` | Reviewed, nothing to record. Letters written together (`TID`); a reason of at least 5 words. |
| `control` | `control ID THREAT KIND words` | `KIND` from the list below. |
| `accept` | `accept THREAT reason` | Only for a risk below 6 (`controls` checks it). |
| `top` | `top THREAT ...` | Once. Every risk of 6 or more, highest first (`ranking`). |
| `attack` | `attack THREAT TECHNIQUE` | An ATT&CK id, `T1110` or `T1110.004`. |
| `scope` | `scope ELEMENT cde\|impacting\|out reason` | PCI DSS scope, once an element, with a reason of at least 5 words. Checkpoint 4 part 1 only: the topic's labs never write one. |
| tree | `goal ID THREAT words`, `node ID PARENT and\|or words`, `leaf ID PARENT COST words`, `cheapest GOAL COST` | A parent is a goal or a node above the line; a cost is a whole number. |
| abuse | `abuse ID THREAT As a/an ..., I ... so that ...`, `test ID ABUSE words` | A test says what the team will try, in at least 4 words. |

**Control kinds**, and the letters each answers: S `authn` `mfa` `mutual-tls` `signing` `access-proxy`; T `signing` `integrity` `input-validation` `mutual-tls` `patch`; R `audit-log` `signing`; I `tls` `encryption` `minimise-data` `authz` `least-privilege` `access-proxy` `secret-store` `patch`; D `rate-limit` `quota` `redundancy`; E `authz` `least-privilege` `sandbox` `allow-list` `separation-of-duties` `input-validation` `patch`. The last three in the list (`secret-store`, `separation-of-duties`, `patch`) were added for the checkpoint.

A file with `___` in a line is refused ("this line still has a gap"), which is what a fill-in lab relies on.

## tm-check

```text
tm-check PART MODEL [REF.json] [--quiet] [--choose] [--only N|rest]
```

It prints `ok`, or **one sentence**, and ends with status 0 either way, so a check is `expect: { equals: ok }` and a learner always sees the reason (Module 1's rule for checks with several steps). Status 2 means the command itself was wrong: an unknown part, or a reference the lab's author got wrong ("the lab's reference is wrong, which is not your doing").

| Part | Needs a reference | What it decides |
| --- | --- | --- |
| `reads` | no | Every line is one of the format's. The only part that names a line: `line 12: the letter is one of S T R I D E, a capital, and this one says "s". A threat line is written: threat ID FLOW ...`. Every other part, on a model that doesn't read, says `the model doesn't read yet: "tm-check reads" on it says where`. |
| `diagram` | yes | The design's elements, of the right kind, and its flows, in the right direction; nothing more. |
| `boundaries` | yes | Two elements share a zone in the model exactly when they do in the reference, whatever the zones are called. |
| `stride` | no | Every flow whose ends are in different zones has all six letters covered by threats and `none` lines; no `none` line covers a letter the flow has a threat for; no two threats read the same once names and punctuation are taken out. |
| `findings` | yes | Each weakness of the design has a threat on its flow under one of its letters, rated as the design's scales give; none is marked `none`. |
| `ranking` | no | Each risk is likelihood times impact (the one sum, so it names the line); `top` lists the risks of 6 or more, once each, highest first. |
| `controls` | no | No risk of 6 or more is accepted or left without a control; every other threat has a control or an `accept`; each controlled threat has a control of a kind that answers its letter. With a reference, a weakness's own `controls` list replaces the letter's. |
| `scope` | yes | Every process and store has a scope line, no external has one, and each is what the reference says. |
| `attack` | yes | Each weakness with an `attack` list carries a technique from it, or a sub-technique of one. |
| `tree` | no | A goal that is one of the highest risks; nothing empty; three leaves or more and an `and` node with two steps; `cheapest` is the cheapest path (`or` takes the least, `and` adds). |
| `abuse` | no | Every risk of 6 or more has an abuse case with a test. |
| `kept` | yes | Every threat the reference lists is still there, on its flow (a debug lab's "fix it, don't delete it"). |

**What a learner can run.** The six parts that need no reference check the format and the sums as the learner goes; say so in the prompt. The other six, run without a reference, say that only the lab's checks hold the design's answers. On an empty model every part says the model is empty.

**What a failure says.** Never the flow, the letter or the right value: "the design describes a weakness the model has no threat for", "a control is of a kind that doesn't answer its threat". Only `reads`, the risk sum and an empty tree node name a line, because those are about the file, not the design. `tools/tests/test_tm_check.py` holds every sentence and checks that none of them names a part of the model.

**`--quiet`**, for debug labs, replaces each part's sentence with one fixed sentence, the end state still missing ("the zones are not yet where trust changes"), so a check never says which kind of fault is left. `reads` still names its line.

**`--choose`**, for any lab whose model is written from a blank file, caps what a model may list: at most three threats on one flow under one letter, and at most two controls and two ATT&CK techniques on one threat. Without it, a model that writes a threat at every rating, or answers a threat with every kind of control, passes `findings`, `controls` and `attack`, because each looks for one right line among many. With it, each of those three parts refuses its own kind of list first ("the model lists where it should choose: a threat has more than two controls"), so a list fails only the check of the skill it dodged. Under `--only N` the cap on controls is that weakness's threat's alone, and under `--only rest` it covers every threat the reference doesn't narrow. Every part takes the flag, so a lab may pass it to every check; the other parts ignore it. A lab that turns it on says the cap in its prompt. The threat-modeling topic's labs check the same cap with an `awk` check of their own and don't pass the flag; Checkpoint 4 part 1 passes it.

**`controls --only N`** checks only the control on the reference's Nth weakness (from 1): its threat exists and has a control of an allowed kind. An `accept` passes only when the weakness, at the design's own ratings, is below 6, so rating a risk down and accepting it fails. **`controls --only rest`** is everything `controls` checks except the kind of control on the weaknesses that have a `controls` list. Checkpoint 4 part 1 uses both: one check a high weakness, so a wrong control brings back one skill, and one for the rest.

## The reference

The general rules are in the image, where a learner can read them. **What is right for one design is not**: it is a JSON object in the lab's `checks.yaml`, handed to `tm-check` on standard input (`-` where the file would be), so it is never a file in the lab:

```yaml
- id: design-weaknesses-found
  description: "Everything the design describes as weak has a threat on its flow, rated by the design's scales."
  command: |
    tm-check findings /home/learner/model.tm - <<'REF'
    {"elements":{"driver":["external","internet"],"app":["process","depot"]},"flows":{"f1":["driver","app"]},"weak":[{"flow":"f1","letters":["S"],"L":3,"I":3,"controls":["mfa"]}]}
    REF
  expect:
    equals: ok
```

| Key | Shape | Meaning |
| --- | --- | --- |
| `elements` | `{id: [kind, zone]}` | The design's parts. The zone names are the reference's own: only who shares a zone with whom is compared. |
| `flows` | `{id: [from, to]}` | The design's flows, from the side that starts each. |
| `weak` | a list, in a fixed order (`--only` counts it) | The weaknesses the design describes. Each has `flow`; `letters` (one or several a fair reader could file it under); `L` and `I`, a number or a list of the ratings the scales allow; optionally `controls` (the kinds that answer it, narrower than the letter's), `attack` (technique ids without sub-techniques: `T1110` accepts `T1110.004`) and `no_none` (the letters a `none` line may not cover: by default the weakness's letter when it has one, and none when it has several). |
| `scope` | `{element: cde\|impacting\|out}` | Every process and store. Needed by the `scope` part only. |
| `either` | a list of pairs of elements | Pairs that may share a zone or not (an app and the cloud's managed database). |
| `kept` | `{threat id: flow}` | The threats a debug lab's model must keep. Needed by the `kept` part only. |

A mistake in the reference (an unknown key, a flow with an end that isn't an element, a control that isn't a kind) stops the check with status 2 and a sentence for the author, instead of passing or failing a learner for the wrong reason.

**How a weakness finds its threat.** Each weakness takes a threat on its flow under one of its letters; when there are several, the one rated as the scales give; no threat stands for two weaknesses. So a learner may record more threats than the design asks for, on any flow, as long as each is rated, answered and unlike the others.

## Rules for labs on the base

- **The design states facts, never "weaknesses".** A careful reader reaches the reference from the design's sentences and its scales. Put the scales in the design and nothing in the prompt that names a flaw.
- **The prompt holds the format table** (or points at `tm-check --help`) and the control kinds; a proof must not make the learner guess the format.
- **One check a part**, each with the same reference, each `expect: { equals: ok }`. Their descriptions state the end state and never a flow or a letter.
- **A wrong model for every part**, each a `wrong/*.sh` that writes the whole model: a company drawn inside the wrong zone, a flow backwards, a letter missing, `none` where the design is weak, a misrating, a wrong sum, an unordered `top`, a control that answers the wrong letter, an accepted high risk, a tree with the wrong cost. `tools/tests/tm_cases.py` has the checkpoint designer's 25 for the shop's checkout.
- **Three stories, not one.** A threat model is judgement, which can't be made up afresh at check time; what keeps a second try from being a memory test is that a topic's build, its debug and the checkpoint's versions are different systems whose answers differ in every part. A model that is right for another story fails `diagram` at once (tested).
- **A check that the design is as it was** (`sha256sum -c`), since the learner owns the file.
- **Edit `tm-check` for Python 3.12.** The lab's Python is older than the repository's. `ruff format` at the repository's own target once rewrote `except (A, B):` in a form 3.12 refuses; format with `--target-version py312`. A test parses every base script as 3.12.

## What the tests hold

`tools/tests/test_tm_check.py`, with the models in `tools/tests/tm_cases.py`: the checkout's 64-line reference model passes all ten parts, and each of its weaknesses alone and the rest; each of 25 wrong models fails exactly the part aimed at it, with its sentence; a wrong control fails only its own weakness's `--only`; a right model for another story fails; 26 kinds of bad line each get their line number and what was expected; every line of both models cut short at every word, and every line removed, never makes a part crash; `--quiet` says one sentence a part; `--choose` lets a model that lists pass without it and fails it with it, in the one part its list slips through (and, under `--only`, only on its own weakness), while three threats under one letter, two controls and two techniques still pass; a wrong reference is refused.

## Size and time

On the owner's PC (Docker Desktop 29.8.2, 2026-11-22): the image is 268 MB as Docker reports it, all but a few kilobytes of it the layer every plain lab shares; the base builds in a second or two once that layer is cached; one `tm-check` run takes about 0.1 s, most of it Python starting; a lab container holds under 1 MiB of memory. The probe lab's contract (pristine, solution, restart trial, eight wrong models: eleven containers) took 47 s, 61 s and 76 s in three runs, with other work on the machine each time. Nothing here has run on a GitHub runner yet: the probe lab is how it will.

## Files here

| File | What |
| --- | --- |
| `Dockerfile` | The two layers. |
| `tm-check` | The checker. Its docstring is what `tm-check --help` prints. |
| `README.md` | This file. |
