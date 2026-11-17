# ADR-0027: Typed answers, a command or a term recalled and typed

- **Status:** Proposed. Designed under the owner's delegation of 2026-11-11 (the best learning experience, then memory retention, then free), and built on until the owner rules; listed in [docs/owner-queue.md](../owner-queue.md) under "Decided for you".
- **Date:** 2026-11-16

## Context

Most quick questions on the platform are multiple choice. Picking an answer from a list is recognition: the right answer is on the screen, and the learner only has to know it when they see it. Producing the answer is recall, and recall builds memory better. Kang, McDermott and Roediger (2007) found that short-answer quizzes beat multiple-choice ones on a final test days later, as long as the learner was told the right answer afterwards (_European Journal of Cognitive Psychology_, "Test format and corrective feedback modify the effect of testing on long-term retention").

Three item types already ask for a produced answer, each for one shape of answer: `predict_output` and `predict_shell` for what a program prints ([ADR-0017](0017-shell-in-the-browser.md)), and `estimate` for a number worked out within a tolerance ([ADR-0024](0024-estimate-questions.md)). Nothing takes a command ("which command lists the running containers?"), a term ("what is the Azure name for a private network?"), a value (a port number, a file's path) or a short phrase. The cloud track is full of these, and today they are asked as multiple choice, where the other choices also hint at the answer's shape.

## Decision

Add one recall item type, `typed`: the learner types a short answer from memory, and it's right when, read the item's way, it's one of the item's accepted answers.

```yaml
# content/topics/<topic>/recall/docker-list-running.yaml
id: docker-list-running
type: typed
rev: 1
prompt: |
  Which Docker command lists only the containers that are running right now?
kind: command # command | text
answers: # every answer that counts; the first is the one the page shows
  - docker ps
  - docker container ls
  - docker container list
mistakes: # optional: wrong answers a learner is likely to type
  - id: every-container
    answers: [docker ps -a, docker ps --all]
    why: "`-a` lists every container, stopped ones too. Running ones only is plain `docker ps`."
explanation: "`docker ps` lists the running containers; `docker container ls` is its newer spelling."
skills: [list-containers]
```

1. **Fields.**
   - `kind` is `command` (a shell or PowerShell command) or `text` (a term, a value, a phrase). It sets how the answer is read (below). Required, so a converted item says which it is.
   - `case` is `sensitive` or `insensitive`. Left out, it follows the kind: a command's case matters (`ls` and `LS` are different commands, and so are `-a` and `-A`), a term's doesn't (VNet and vnet are the same word). An item sets it only to say otherwise, such as a case-insensitive PowerShell cmdlet or a case-sensitive environment variable.
   - `answers`: at least one, each a single line of at most 120 characters, written as text. An answer YAML would read as a number or as true (`22`, `yes`, `1.5`) must be quoted, because Python's YAML and the browser's read those differently; unquoted, the validator refuses it.
   - `mistakes`: optional, each with an `id`, `answers` (the ways of typing the same slip) and `why`, the sentence a learner sees when their answer matches.
   - `prompt`, `explanation`, `skills` and `rev`, as on every recall item.
2. **How an answer is read.** The accepted answers, the mistakes and what the learner types all go through the same steps, in `tools/typed_answers.py` for the validator and `web/src/content/typed.ts` for the page. Both are tested against one shared list of cases (`tools/tests/typed_cases.json`), so they can't drift apart:
   1. Unicode's compatibility form (NFKC), so a non-breaking space is a space and full-width letters are ordinary ones.
   2. Curly quotes become straight, and look-alike hyphens and the minus sign become `-`. An en or em dash becomes `--` in a command (a phone's "smart punctuation" turns a typed `--all` into `—all`) and `-` in text.
   3. Any run of spaces, tabs or line breaks is one space, and there are none at either end. An answer whose meaning depends on two spaces in a row can't be a typed item.
   4. For a command: one pair of backticks round it is taken off, then a copied prompt in front, `$ `, `> ` or `PS> ` followed by a space (so `$HOME` and `>file` stay). Quotes inside a command are part of it and stay.
      For text: a full stop at the end, one pair of quotes or backticks round it, and a full stop at the end again, are taken off.
   5. Lower case, when case doesn't matter.
3. **One slip of the fingers, for text only.** A text answer that is an accepted answer with one slip among its letters (one letter changed, added or left out, or two neighbouring letters swapped) counts as right, and the page shows the spelling: "Watch the spelling: it's Kubernetes." The term was remembered, and spelling isn't what's being practised; marking it wrong would teach the learner that they didn't know something they did. A slip involving a digit, a space or a symbol is never one (RAID 5 and RAID 6, TLS 1.2 and 1.3), nor is a letter in the other case, and an answer under five characters is never forgiven one (NFS and NTFS). A known mistake is matched first, so a mistake one letter away from an answer is named, not forgiven. A command is never forgiven a slip, because a shell would refuse it.
4. **What the validator proves**, with no code run, so `--no-run` checks it too:
   - every answer reads as something (`"."` reads as nothing);
   - the accepted answers are all different once read, so a writer sees when `$ docker ps` duplicates `docker ps`;
   - no mistake reads the same as an accepted answer, which would mark that mistake right, and no answer appears in two mistakes, or twice;
   - mistake ids are unique;
   - the prompt doesn't give an accepted answer away: for a command, no inline code or code-block line in the prompt reads as the answer; for text, the answer doesn't appear in the prompt as a whole word or phrase, once both are read, when it's at least four characters long (shorter answers such as `ls` or `A` turn up inside ordinary sentences).
5. **No patterns.** Answers are a list, not regular expressions. A list is readable by a beginner, proves itself (each entry is a real answer the validator can compare), and is read the same way in Python and in the browser, whose regular expressions differ in small ways. A command with many equivalent spellings (flags in any order) lists the common ones, and the rest stay a multiple-choice or `predict_shell` question.
6. **On the page.** A labelled box ("Your command", with a `$` before it and a monospaced font, or "Your answer"), with the phone's auto-capitalise and autocorrect switched off so the answer is the learner's own, and Check, which Enter also presses. One attempt, as for the other types; the come-back question is the second try ([ADR-0011](0011-mistakes-come-back.md)). Afterwards: right or not, the answer (the first accepted one, as code for a command), the spelling after a forgiven slip, the matched mistake's `why`, the other accepted answers ("Also accepted"), and the explanation. In the placement test it has the quiet mode the other types have, with "I don't know this" ([ADR-0021](0021-placement-test.md)).
7. **Where it counts.** It is a recall item everywhere a recall item goes: the practice ladder's recall count, the review pool, follow-ups after a miss ([ADR-0011](0011-mistakes-come-back.md)), interleaved questions, and the placement test's probes, where it isn't a choice. In review sessions and in the validator's review-pool rule it counts as an answer the learner produces ([ADR-0009](0009-reviews.md)), with predict-the-output, Parsons and estimates: that rule exists so every session asks for more than recognition, and a typed answer is recalled.
8. **The event.** An `answer` event like the other recall items ([ADR-0008](0008-event-log.md)), with `correct`, and in `data`: `typed`, what the learner typed (clipped like other text); `mistake`, the matched mistake's id, or null; and `slip`, true when it was right but for a forgiven slip. "I don't know this" saves `dont_know: true` with those three null. No new event type, no migration, and no existing event changes meaning.

## Alternatives considered

- **Multiple choice.** Nothing to build, and still the right type when the skill is telling options apart. It tests recognition, and the choices give away the answer's shape.
- **`predict_shell` for commands.** It asks what a command prints, which is reading a command, not remembering one.
- **Regular expressions for answers.** More compact for answers with many spellings, but a pattern can accept far more than its writer meant (`.*` accepts everything; `docker ps.*` accepts `docker ps -a`), the two runtimes' regular expressions differ, and a beginner can't read one at a glance. A list of answers can be proved entry by entry. If the event log shows learners being marked wrong for spellings nobody listed, patterns can come in with their own ADR and a validator check that a pattern accepts none of the mistakes and rejects a sample of unrelated text.
- **Exact match, no forgiving.** Simplest, but a trailing space, a curly quote or a capital letter would mark a remembered answer wrong, which teaches the wrong thing and makes the platform feel petty.
- **Forgiving slips in commands too.** A shell doesn't forgive `dokcer ps`, and knowing a command includes typing it.
- **Forgiving any small edit, digits included.** It would accept RAID 6 for RAID 5 and port 445 for port 443.
- **`case` required on every item.** One more line on every item for a rule the kind already implies; the default covers almost every item, and the field is there for the exceptions.
- **A free-text answer graded by the AI.** Costs money on every answer, needs the network, and couldn't be proved by the validator ([ADR-0004](0004-content-model.md)). Explanations already have that path ([ADR-0013](0013-explain-grading.md)).

## Consequences

- One new item type in the content model, the validator, the web types, one component and its grading functions, and the shared reading rules in two languages with one set of test cases. No database migration.
- Content writers can turn multiple-choice questions whose answer is a command or a term into typed ones, starting with the cloud track.
- An answer nobody listed is marked wrong. The `typed` text in every answer event shows which answers learners actually give, so a missing spelling can be added (raising the item's `rev`).
- A typed answer can be learned by heart from its prompt. The come-back rule (a different question on the same skill) is the defence, as for every recall item.
