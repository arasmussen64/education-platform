# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versioning: [Semantic Versioning](https://semver.org/) once there's a release.

## [Unreleased]

### Added (Module 3 content: Loops)

- **Five new topics, all ready:** while loops, for and range, Accumulator patterns, Strings as sequences, and Nested loops. Each has a lesson, a practice ladder, the three proof checks, a review pool and skills, so missed questions come back.
  - Four are built on CS50P Lecture 2 (Loops), embedded in clips whose times come from CS50's own subtitles: while loops (0:28 to 16:13), for and range (to 26:47), `while True` with `break` and `continue` (to 31:34), and the Mario section for nested loops (1:05:56 to 1:19:15). Strings as sequences is built on the Text section of Python's own tutorial, with Python Tutor walking a loop along a string.
  - Accumulator patterns names the three shapes (running total, count, best so far) and makes a point of the starting value: 0 is the wrong start for a smallest-so-far.
  - Off-by-one mistakes get their own attention throughout: `range` stops before its stop value, `word[len(word)]` is one too far, and the last word of a line has no space after it.
- **Checkpoint 3: text statistics.** From a line of text: the number of words and letters, the longest word, and a bar chart of word lengths, using loops and strings only (lists and `split()` come in Module 5); a triangle-drawing program with three bugs, one of them a crash; a module-level explain about the word that ends with the text. The way through for a stuck learner: a week-of-weather sibling (sunny streaks), the build in four steps, and two fresh versions (number statistics, match results). Every test names the skills it checks, across Modules 1 to 3.
- In all: 39 more exercises and 26 more recall items. The validator runs 441 programs over the content with no problems. With this, Milestone C is complete.

### Added (interleaved practice)

- **Each practice ladder now includes one question from an earlier topic** (v1 spec, F5): a recall question from the topic's most recent prerequisite, placed after the topic's own quick checks and labelled with where it's from. It changes each day. Answering it counts for the earlier topic, so it helps keep that topic fresh.

### Added (reviews, timed to how fast you forget)

- **Reviews on the Today page** ([ADR-0009](docs/decisions/0009-reviews.md)). Each Learned topic gets a review card; its first review comes due a few days later, and each review pushes the next one further out when it goes well, or brings it closer when it doesn't. Today lists the topics due, the most forgotten first, up to 20 a day.
- **A review session** asks two items from the topic's review pool, at least one of them code or predict-the-output, choosing the ones answered longest ago. It's rated from the first attempt at each: all right is Good, some is Hard, none is Again. The result is saved as a `review` event, and the page says when the next review is.
- **Three more topic states,** on topic pages and the map: Mastered (a review went well at least a week after learning), Fading (a review is due) and Relearning (the last review went badly). A topic in any of these still unlocks what builds on it.
- **The scheduler is the platform's own code** (`web/src/reviews/fsrs.ts`): the published FSRS-4.5 formulas and default parameters, with a 90% target retention. The ML capstone will fit them to real data.

### Added (Module 2 content: Decisions and debugging)

- **Five new topics, all ready:** Booleans and comparisons, if / elif / else, Logical operators, Tracing code, and Reading errors. Each has a lesson, a practice ladder, the three proof checks, a review pool and skills, so missed questions come back.
  - The first three are built on CS50P Lecture 1 (Conditionals), embedded in three segments whose times come from CS50's own subtitles: comparisons and `if` (0:28 to 9:55), `elif` and `else` (to 18:28), `or` and `and` (to 34:07).
  - Tracing code is built around Python Tutor; Reading errors around Python's own tutorial on errors. Both lessons are the platform's own words.
  - Logical operators makes a point of the `x == 1 or 2` trap, which is always `True`.
  - Several exercises check the code with other starting values (`run_with`), so a trace exercise can't be passed by typing the expected output in.
- **Checkpoint 2: ticket pricing.** A rules-based cinema ticket program (age bands, a weekend extra, a member discount) from a blank editor; a parking-fee program with three bugs to fix; a module-level explain. The way through for a stuck learner: a zoo-ticket sibling, the build in four steps, and two fresh versions (a swimming pool and a train fare). Every test names the skills it checks, across Modules 1 and 2.
- In all: 39 more exercises and 26 more recall items. The validator runs 292 programs over the content with no problems. Milestone B is complete.

### Added (topic states, gating and "Prove it now")

- **Every topic now has a state** for the signed-in learner, shown with an icon and a word on its page and on the map: Locked, Available, In progress, Learned (or Passed, for a checkpoint), with the date it was learned.
- **Gating is on** ([ADR-0002](docs/decisions/0002-mastery-and-gating.md)). A Locked topic, one whose prerequisites aren't learned yet, shows its lesson only, with a note saying which topics open it. Its practice and proof checks wait. A Locked checkpoint shows only what it brings together.
- **"Prove it now"** on an Available topic skips the lesson and practice and goes straight to the three checks, which can be shown again with one click. Passing them marks the topic learned, just the same.
- **"Next up" on the Today page:** the topic in progress, or else the next Available topic in track order, with its time estimate.
- Signed-out visitors see no states and no gating, because nothing of theirs is saved anyway.

### Added (more than one track, and the cloud track on the map)

- **The app shows every track.** The topic map opens on Python Foundations at `/map`, with a switcher to the others, each at `/map/<track id>`. A topic page names its track as well as its module. Tracks carry an `order`, and a module may name a **capstone**: a bigger checkpoint that ends a stage, shown after the module's own checkpoint.
- **The Cloud Solutions Architect track is on the map** as 357 `planned` outlines (324 topics, 30 checkpoints, 3 capstones), generated from its spec by `tools/outline_cloud_track.py`. Each module's topics unlock when the modules it builds on are passed, following the spec's module map. Nothing in it can be opened yet; the map says so.
- The validator checks capstones like checkpoints, and that no two tracks share an `order`. 4 new validator tests, and 4 for the generator, one of which runs the validator over generated content.

### Added (planning: a second track)

- **The Cloud Solutions Architect track is specified** in [docs/specs/cloud-solutions-architect.md](docs/specs/cloud-solutions-architect.md). It isn't built yet.
  - It runs from Linux and networking up to principal-level multi-cloud strategy, on AWS, Azure and Google Cloud.
  - It has 30 modules in 4 stages, about 320 topics, 3 capstones and a choice of specialties.
  - Every topic is proven by doing: build, explain, fix a broken version, and review. The senior stages add design reviews, game days and "Defend it".
  - **Cross-referenced with the owner's *Senior Cloud Architect Knowledge Map & Learning Roadmap*** (2026-11-08), adding everything the map had that the spec lacked and removing nothing:
    - 4 new modules: Virtualization, hardware and Windows; Software engineering literacy; Application architecture and integration; Specialized workloads. 107 new topics, 210 to 317, and many existing topics extended.
    - **The map itself** is kept in `docs/research/senior-cloud-architect-knowledge-map.md`, unchanged.
    - **An example path for an experienced learner:** the map's seven-phase, 24-month plan mapped to the track's modules, with its weekly rhythm, kill criteria and reading list. What a learner skips is decided by proofs, never by their own estimate.
    - **The track assumes nothing about the learner.** It starts from zero and teaches every topic in full, so it can serve absolute beginners. For that reason the map's depth levels (L1 to L3) were left out, at the owner's request.
    - **A 24-item self-assessment,** each item tied to the proof that covers it.
    - More certifications, with a suggested order; 6 more drills; 20 more rows in the three-cloud service table.
    - Module numbers and positional checkpoint IDs shifted because modules were inserted; nothing is built, so nothing refers to them.
- **[ADR-0014](docs/decisions/0014-cloud-labs.md), proposed,** decides how cloud skills are proven:
  - labs run in the learner's own sandboxes;
  - a local, read-only lab checker inspects the results;
  - fault modules provide break-fix exercises and game days;
  - AI grades designs;
  - CI tests the checks against recorded API responses, without touching a cloud.

### Added (explain it back, graded: part 2 of explanation grading)

- **Explain it back** works: each explain card has a box and **Check my explanation**. Claude grades it against the rubric:
  - **Passed**;
  - or **Needs work**, with up to 3 guiding questions, never the model answer;
  - or a plain message when it wasn't graded: paused for the month, unavailable, not switched on for the account, or no connection.
- Every attempt is saved as an `explain_submit` event, graded or not. A pass shows straight away in "Your proof so far", and counts toward the topic being learned.
- **The grader is Claude Haiku 5.5 at low effort.** It got all 30 samples of the test set right in two separate runs, so the bigger models weren't needed. A grading costs about $0.0002, so the $10 monthly cap covers tens of thousands.

### Added (the grading test set, part 3 of explanation grading)

- **30 sample explanations** for Module 1's six explain checks, in `supabase/functions/ai/test-set/`. Each topic has five, each with the verdict it should get:
  - a full answer and a short one, both of which should pass;
  - one missing a required idea, one with a misconception, and one that tries to talk its way to a pass, none of which should.
- **`npm run fn:eval`** runs them against Claude with the same request the proxy sends, and reports every miss and the cost. It costs money, so each run waits for the owner's go-ahead.
- A test checks every topic in the test set has an explain check and both kinds of sample. It doesn't call Claude.

### Added (the AI proxy, part 1 of explanation grading)

- **`ai_calls`**, an append-only log of every call to Claude: who, the model, the tokens and the cost. A learner can read their own rows, and only the proxy can write them. `ai_spend_this_month()` adds up the month's spending for the $10 cap. 11 database tests.
- **The AI proxy**, an Edge Function (`supabase/functions/ai/`), following [ADR-0013](docs/decisions/0013-explain-grading.md):
  - it checks, in order, that the caller is signed in, `allowed`, under the month's cap, and that a key exists;
  - it asks Claude to grade the explanation against the rubric, in a fixed JSON shape;
  - a pass means every required rubric item is met, and guiding questions that repeat the model answer are dropped.
  19 tests, none of which call the real API.
- **Deno** (2.9.6) as a pinned development tool at the repository root, with `npm run fn:test` and `npm run fn:serve`. CI has a new **Edge Functions** job.
- The explanation box (part 2) is what calls it. Both went live on 2026-11-08.

### Changed

- `supabase/README.md` says how to put the AI proxy live. Merging deploys the web app, but the function is deployed by hand.
- The first database test now looks only at its own learners, so it also passes on a local database with accounts of its own.

### Decided

- [ADR-0013](docs/decisions/0013-explain-grading.md), accepted by the owner: grading explanations with Claude, through the AI proxy. It covers the path of one explanation, what a pass means, the $10 monthly cap and its call log, how the cheapest model that passes a test set gets chosen, and what the owner sets up before it goes live.

### Added (progress tracking, part 1)

- **Your proof so far:** each topic and checkpoint page lists its three proof checks, each passed (with the date) or not yet. A Check passed on the page shows straight away.
- **Progress on the map:** for a signed-in learner, each topic they've started says "In progress", and which proof checks they've passed there.
- The rules behind it (`web/src/progress/progress.ts`), with tests for every state change in the data model: when each proof check first passed, and each topic's state. A pass on any fresh version counts as a checkpoint's build.
- Progress is worked out from the event log, so passes from before this existed count too.
- **Not yet:** topic states and gating. No topic can be Learned until explanations are graded, so gating now would lock every topic after the first. They switch on with explanation grading.

### Added (export my data)

- **Export my data** (v1 spec, F16), built early so the learning history can always be backed up. On the new account page (open it from your name in the header), "Download my data" saves everything as one JSON file: the profile and every event.
  - It reads this browser's outbox first, then the server. So an answer that hasn't reached the server yet is in the file too, and none can slip between the two. The page says how many events came from the outbox.
  - It keeps reading pages until one comes back empty, so a server that sends fewer rows than asked for can't cut the file short.
  - The browser makes the file itself: nothing is sent anywhere.
- The file's layout, with a `format` version for scripts that read it, is in the [data model](docs/specs/data-model.md#the-export-file).

### Changed

- The day helpers (`dayOf`, `addDays`) moved from the follow-up rules to `web/src/days.ts`, so a page that only needs a date doesn't load those rules too.

### Added (Checkpoint 1)

- **Checkpoint 1: receipt calculator** (`py.m1.checkpoint`), ready. That completes Module 1.
  - **Prove it:**
    - build: a restaurant receipt from a blank editor (meal, drinks and a tip percentage);
    - debug: cinema tickets, with three bugs: an unconverted input, a missing pair of parentheses, and a `print` with a comma;
    - explain: what each line of a tip calculator does, with the type of every value.
  - **The way through** ([ADR-0012](docs/decisions/0012-checkpoint-support.md)):
    - a solved sibling: a shop receipt with a discount, planned with comments;
    - the receipt in 4 fill-in steps with hints: read, work out, print, then only the plan;
    - 2 fresh versions: splitting a bill, and an electricity bill.
  - Every build and debug test names its skills, and each known-wrong answer fails only the test for its mistake.
- The content checker runs every exercise with hidden tests on an empty program. A crash there is in the tests themselves, and the page would show it.

### Changed

- The "Try it in steps" suggestion now brings the steps to the top of the screen.

### Added (getting unstuck on a checkpoint)

- [ADR-0012](docs/decisions/0012-checkpoint-support.md), accepted: every checkpoint gets four additions, and the content checker won't mark one ready without them.
  - **Find the weak skill:** every test of a checkpoint's builds and debug names the skills it checks (`test_skills`). A failed test brings them back on Today, as questions from their own topics. Like code, a test counts as missed only if no Check passed it that day.
  - **A solved sibling** to study, **the build in 3 or 4 steps** with hints, and **at least 2 fresh versions** of the build.
- The checkpoint page: an "About this checkpoint" section in place of a lesson, the three proof checks, and a "Stuck? Try it in steps" section.
  - The steps open only when asked. After 2 failing Checks on the build, the page suggests them next to it.
  - The fresh version offered is one not yet tried, or else the one tried longest ago.
- The Today page reads which tests each Check failed (`data.failing`), and loads checkpoints and the topics their tests name.
- The content checker's rules for ready checkpoints: every topic in the module ready; a solved sibling, 3 or more steps with hints, and 2 or more fresh versions; every build and debug test naming real skills of this or earlier modules.

### Added (the fifth lesson)

- **Strings and input** (`py.strings-and-input`), ready to learn. That completes Module 1's topics.
  - **Learn:** CS50P Lecture 0 from 43:23 to 45:02, on f-strings. `input()` and `int()` were already in earlier clips, so this clip covers only what's new. The `:.2f` part of the lecture (1:24:34) and the Python tutorial's section on f-strings are linked as more resources.
  - **Practice:** a worked example that asks two questions and does maths with the answers, three questions (one mixes in topic 2's "45" surprise), filling in a rectangle's area, and a price tag with `:.2f`.
  - **Prove it:** kilometres to miles from a blank editor; a shopping line with a conversion crash and a missing `f`; explaining why `age + 1` fails on typed input.
  - **Review pool:** four items. Three skills: `input-text`, `convert` and `fstrings`.

### Added (the fourth lesson)

- **Arithmetic** (`py.arithmetic`), ready to learn:
  - **Learn:** the main resource is a reading, four short sections of the free textbook *Python for Everybody* (CC BY 4.0). CS50P's lecture only lists the operators for about 40 seconds and never covers `//` or `**`. The lecture video on the same chapter and the Python tutorial's "Numbers" section are linked as more resources.
  - **Practice:** a worked example with `/`, `//` and `%`, three questions (one mixes in topic 2's types), filling in operators for egg boxes, and Celsius to Fahrenheit.
  - **Prove it:** a pizza party from a blank editor; a bill-splitting program with a crash and a silent order-of-operations bug; explaining `/`, `//` and `%` with cookies.
  - **Review pool:** three items. Three skills: `operators`, `precedence` and `div-mod`.
- A reading used as a lesson's main resource is credited with its license once, not with its title repeated.

### Added (the third lesson)

- **Variables** (`py.variables`), ready to learn:
  - **Learn:** CS50P Lecture 0 from 15:16 to 19:54: what a variable is, `=` as assignment, and the "quotes around the name" mistake. The intro swaps the video's "container" picture for name tags, the picture that still works when lists arrive. A Python Tutor link shows `b = a`, then `a = 5`, step by step, with names drawn as arrows.
  - **Practice:** a worked example following one name, three questions (one mixes in topics 1 and 2), filling in a swap, and rotating three values.
  - **Prove it:** swap and print from a blank editor, a swap that loses a value plus a typo, and explaining why `b` stays `3`.
  - **Review pool:** four items. Three skills: `assignment`, `trace-values` and `swap`.
- `run_with` in the shared test toolkit (`harness/checks.py`). It reruns the learner's program with other starting values, so retyping the expected values can't pass. 4 unit tests, plus a scenario that both runtimes must agree on.

### Fixed

- The dev server now notices new files in `content/` and `harness/`. Before, a lesson's new questions and exercises showed as "Missing practice item" until a restart. The live site was never affected.

### Changed

- Relearning follows the research the owner asked for: a missed skill must be right on **3 different days**, coming back after 1, 3 and 7 days (successive relearning; Rawson & Dunlosky, 2011).

### Fixed

- One miss can open follow-ups for several skills, and they could all pick the same question, showing it twice on Today. Each skill now gets its own question where possible; a shared one is asked once.

### Added (a guarantee)

- A test over the real content: missing any question or exercise in any ready topic must bring back a different question on each skill it tests. New topics are covered as soon as they're ready.

### Added (mistakes come back)

- **Mistakes to revisit** on the Today page ([ADR-0011](docs/decisions/0011-mistakes-come-back.md), now accepted). The owner asked for this after missing a question in their first lesson:
  - a skill you missed comes back the next day, as a *different* question on the same skill;
  - after a right answer it returns 3 days later, and right answers on 2 different days relearn it;
  - "Coming back later" lists what's due on other days.
- It's worked out from the event log, so misses from before this feature count too.
- Answers on Today are saved as reviews, with hints off.
- Code exercises count as missed only if they never passed that day. Failing Checks while working something out aren't mistakes.
- The Today page now loads only when visited, like the topic pages.

### Added (the second lesson)

- **Values and types** (`py.values-and-types`), ready to learn:
  - **Learn:** CS50P Lecture 0 from 59:32 to 1:07:58: what an integer is, and why a calculator prints "12" for 1 + 2. A float clip and the Python tutorial are linked as more resources.
  - **Practice:** a worked example with `type()`, three questions (one mixes in topic 1: `print` hides quotes), a fill-in and a write exercise.
  - **Prove it:** a type report (its hidden tests also check that `type()` is used), a receipt with one crashing and one silent type bug, and explaining the calculator bug.
  - **Review pool:** three items. Two skills: `identify-types` and `plus-by-type`.
- The loading test now checks every ready topic automatically.

### Added (skills)

- [ADR-0011](docs/decisions/0011-mistakes-come-back.md) (proposed): a missed question will come back as a different question on the same skill, until it's right on 2 different days. The owner asked for it, and chose fresh questions over repeats.
- Topics declare their **skills**, and every question and exercise names the skills it tests. The content checker requires every graded item to name a skill, and every skill to have at least 2 questions that can come back after a miss. Unknown skill names are caught as typos.
- Programs and print is labeled with 4 skills, and has a new review question on printing with commas.

### Fixed

- A video clip looked as long as the whole lecture, because YouTube's player always shows the full video's length (a 9-minute clip read as 1 hour 45 minutes). The page now says above the video which part to watch, how long it is, and that it stops by itself. The topic's time estimate now says it covers the whole topic. Reported by the owner.

### Added (the first lesson)

- **Programs and print** (`py.programs-and-print`), the first real topic, ready to learn:
  - **Learn:** a 9.5-minute segment of CS50P Lecture 0 (CC BY-NC-SA 4.0), with an intro on what to watch for and a recap.
  - **Practice:** a worked example, three questions (one on reading an error), a fill-in exercise and a write exercise.
  - **Prove it:** build a banner from scratch, fix a program with two bugs, and explain why an error happened.
  - **Review pool:** three items for later reviews.
  The checker runs 22 programs for it, including 12 known-wrong answers that must fail.
- A practice-hours tracker idea is on the roadmap (Phase 2).

### Changed

- Multiple-choice answers are Markdown, so they can show code.
- Code and output boxes stand out from their cards in dark mode.
- The content definition of done: while the owner is the only learner, their first pass happens on the live site.

### Added (saving progress)

- Everything a signed-in learner does on a topic page is saved to the append-only event log (F6): lesson views, answers, runs, checks and hints. Each event records the item's revision, how long the attempt took, the hints used, the study session, and the commit the app was built from.
- Events go into an outbox on the device first, then to the server in batches. Retries are always safe, because the server ignores an event it already has. Offline, nothing is lost: the app retries with growing waits and again as soon as the browser is back online.
- An event the server refuses is set aside on the device, so it can't block the others.
- A "Not saved yet" badge in the header while work is waiting on this device.
- Topic pages tell signed-out visitors that their answers won't be saved.

### Added (topic pages)

- The app reads `content/` while it's built: YAML becomes data, lessons are MDX, and exercise code is loaded as text. A topic's lesson and exercises download only when its page opens.
- **Topic pages**, in three parts:
  - **Learn:** objectives, then the lesson's intro, the main resource (a privacy-enhanced YouTube embed, cut to its start and end times, or a link) and the recap, with the source and license. Other resources are listed after it.
  - **Practice**, in order: a worked example with labeled steps to run; multiple-choice and predict-the-output questions with instant feedback; fill-in and write exercises with hints one at a time. The reference solution appears only after a pass.
  - **Prove it:** the build and debug exercises (hidden test details, no hints) and the explain prompt. Grading the explanation, and counting the proof toward mastery, arrive in Milestone B.
- Topics that aren't written yet show their outline and say so. `draft` topics show only on the dev server.
- **The map** lists every module and topic, each marked Ready, Draft or Coming soon, with an icon and a word.
- Exercises can set their own time limit (`time_limit_ms`).
- If a page fails to load, an error page with a Reload button appears inside the layout. The usual cause is the app being updated while it's open.
- The content checker requires a ready lesson to place its main resource (`<Resource index={0} />`), and no other.

### Added (content)

- `content/`: the Python Foundations track and all 36 topics from the approved list as `planned` outlines, with their prerequisites. A `status` field (`planned`, `draft`, `ready`) tracks each topic's progress.
- The content validator (`tools/validate_content.py`). It checks file formats, the topic map (tracks, prerequisites, no cycles), and the definition of done for `ready` topics. It runs every exercise through the shared harness: reference solutions must pass, starters and known-wrong solutions must fail, and predict-the-output items must print what they claim. 14 tests prove it catches each kind of mistake.
- `harness/cli.py`: runs one folder through the harness in a fresh process. Used by the validator and the scenario tests.
- A **Content** CI job.

### Added (sign-in)

- Sign-in with GitHub on the live site, and email links in local development (they land in the local test inbox). The header shows who's signed in, with Sign out.
- The Supabase client, with settings for local and production, and TypeScript types generated from the database (`npm run db:types`).

### Added (deployment)

- Cloudflare deployment config (`web/wrangler.jsonc`): the built app is served as static files, with unknown addresses falling back to the app so its pages work. Wrangler's usage statistics are turned off.
- Setup steps for connecting the repo to Cloudflare and linking the Supabase project.

### Added (database)

- Local Supabase in Docker (`supabase/`), with the Supabase CLI pinned in a root `package.json` and `db:*` scripts.
- The first migration: learner profiles, created automatically at sign-up, and the append-only event log. Row-level security on both. Learners can only add and read their own events and can't grant themselves AI access; the database refuses to edit or delete events, even for admins.
- 18 database tests (pgTAP) and a **Database** CI job that starts a throwaway database, checks the SQL, and runs them.

### Changed

- Run now asks for input like a terminal. When a program calls `input()`, you type the answer right after the prompt and press Enter; there's no separate input box any more. Re-runs use the same random seed, so random choices stay put.

### Fixed

- Cloudflare's pull-request preview builds now deploy: `wrangler preview` needed a `previews` block in `web/wrangler.jsonc`.
- Cloudflare builds no longer spend about 6 minutes installing Python. The Python version is pinned in `pyproject.toml` instead of a `.python-version` file, which Cloudflare's build reacted to.
- No more console warning when the app first opens on a page that loads on demand (it now shows "Loading…").
- Password managers no longer pop up on the program-input field. It's now an editable piece of text (`role="textbox"`) instead of an `<input>`, because NordPass ignored the opt-out markers the first fix relied on.

### Added

- Python in the browser: Pyodide runs learner code in a background Web Worker, with a CodeMirror editor, Run and Check buttons, and a 5-second time limit. A temporary Playground page lets you try it.
- The 14 harness scenarios also run under real Pyodide in the web tests, so the browser and CI are checked to give identical results.
- The Python test harness (`harness/`), shared by the browser and CI. It has 14 scenarios that both runtimes must match, and a Python CI job (uv, ruff, pytest) on Python 3.14.
- ADR-0010: a local Supabase in Docker for development, and one cloud project for real use.
- A setup guide for the owner's computer and accounts (`docs/setup.md`).
- Web app scaffold in `web/`: Vite, React, TypeScript, Tailwind CSS and React Router, with placeholder Today, Map and Topic pages. The product name is kept in a single setting.
- CI on GitHub Actions: formatting, lint, type-check, tests and build on every pull request and every push to `main`.
- v1 spec, data model and Python Foundations track plan, in `docs/specs/`.
- ADR-0008 (append-only event log) and ADR-0009 (per-topic reviews, graded automatically), both accepted.
- Project documentation: vision, learning-science principles, roadmap, competitor research, devlog.
- Decision records ADR-0001 to ADR-0007: decision process, mastery and gating, AI roles, content model, free hosting, working name, tech stack.
- `CLAUDE.md` with the development process and the product rules that constrain code.
- Repository config: `.gitignore`, `.gitattributes` (LF line endings), `.editorconfig`.

### Changed

- Data model: the content validator uses the harness's own test runner instead of pytest.
- Process: Claude merges its own pull requests once CI passes, under standing permission from the owner.
- Roadmap: the "prove it" checks, topic states and gating move from Phase 2 into Phase 1.
