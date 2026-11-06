# Devlog

A dated log of each working session: what changed, what was decided, what's next. Newest first.

## 2026-11-06: Getting unstuck on a checkpoint (ADR-0012)

**Decided**

The owner accepted [ADR-0012](decisions/0012-checkpoint-support.md) and asked for all four additions on every checkpoint. Settled while building it:

- A checkpoint test counts as missed only if no Check passed it that day, as with code. A program that crashes fails every test, so it points at all their skills until it runs.
- Each step gives the whole program except one part, and the last step only an outline. These are completion problems with fading support. Steps that each build one part on its own transfer worse (4C/ID).
- The page suggests the steps after 2 failing Checks, but never opens them by itself.
- Each checkpoint has at least 2 fresh versions besides the main build. The page offers one not yet tried, or else the one tried longest ago.
- A second debug program waits until learners actually get stuck on debugs.

**Done**

- **Content format:**
  - `unstuck` (`example`, `steps`, `versions`) in a checkpoint's `topic.yaml`;
  - `test_skills` in its builds' and debug's `exercise.yaml`: every test, with the skills it checks, as `topic/skill`.
- **Content checker:** a ready checkpoint needs every topic in its module ready, a solved sibling, 3 or more steps with hints, 2 or more fresh versions, and every build and debug test naming real skills of this or an earlier module. 10 new tests.
- **The checkpoint page:**
  - "About this checkpoint" (what it brings together, with links back to the module's topics) in place of a lesson;
  - the three proof checks, with a suggestion next to the build after 2 failing Checks;
  - "Stuck? Try it in steps": the solved sibling, the steps, then a fresh version, rendered only when opened.
- **Follow-ups from checkpoint tests:**
  - the history query now also reads each Check's status and failing tests (`data->>status`, `data->failing`);
  - the Today page loads the checkpoints a learner worked on, then the topics their tests name.
- **Tests:** 20 new web tests. One is a guarantee over the real content, like the one for topics: once a checkpoint is ready, every test of its builds and debug must bring back a question on each skill it names.
- **Checked** the new history query against the local database, read-only. Checks come back with their status and failing tests; answers with neither. I started the local Supabase for this and stopped it afterwards; it keeps its data.

**Next**

- The Module 1 checkpoint (receipt calculator), with its solved sibling, steps and fresh versions.

## 2026-11-06: The fifth lesson, Strings and input (and a checkpoint question)

**Done**

- `content/topics/py.strings-and-input`, status `ready`, which completes Module 1's topics:
  - **Learn:** CS50P Lecture 0 from 43:23 to 45:02, the f-string part. `input()` (topic 3's clip) and `int()` (topic 2's clip) were already covered. The `:.2f` part (1:24:34 to 1:25:56) and the Python tutorial's "Formatted string literals" are linked as more resources.
  - **Practice:**
    - a worked example that asks a name and an age and does maths with the age;
    - three questions: `input()` always gives a `str`, an f-string prediction, and `"4" + "5"` (the "45" from Values and types);
    - filling in a rectangle's area (one line done as a pattern);
    - a price tag with `:.2f`.
  - **Prove it:**
    - build: kilometres to miles;
    - debug: a shopping line. `quantity` isn't converted, so "can't multiply sequence by non-int" crashes it; then a missing `f` silently prints the braces;
    - explain: why `age + 1` fails on typed input.
  - **Review pool:** four items. Skills: `input-text` (3 follow-up candidates), `convert` (4) and `fstrings` (6).
- **Design fix:** the first draft of the fill-in used `...(input())`. Python prints a `SyntaxWarning` into the output before running that code, which would confuse a beginner. Blanks now stand only where a value goes.
- **Checked:**
  - every output and error message, with typed input, on Python 3.14;
  - the feedback for starters and mistakes. Forgetting to convert in the area exercise prints `Area: 444` (`3 * "4"`), which the recap explains;
  - the page on the owner's restarted dev server. All the new files showed up without a restart, so the watcher fix works there too.

**The owner asked:** what if someone really struggles with the checkpoint? Today, nothing special happens. [ADR-0012](decisions/0012-checkpoint-support.md) (proposed) answers with mastery-learning and worked-example research:
- failed checkpoint tests point to the skill behind them, which opens a follow-up;
- a solved sibling project to study;
- a "try it in steps" version with hints, offered after 2 failing Checks;
- proof on a fresh parallel version.

**Next**

- The Module 1 checkpoint (receipt calculator), built to ADR-0012 once the owner accepts it.

## 2026-11-06: The fourth lesson, Arithmetic

**Decided:** the main resource is a reading, not CS50P.
- The lecture gives arithmetic about 40 seconds: a list of `+ - * / %` at 1:00:05, plus a division-and-rounding demo at 1:22:52. It never covers `//`, `**` or the order of operations.
- *Python for Everybody* (Charles R. Severance, CC BY 4.0 per py4e.com) covers exactly that, in four short sections of chapter 2: operators and operands, expressions, order of operations, and the modulus operator.
- Its lecture video for the chapter is linked as an extra but not embedded. YouTube refused its captions (a 404 on the timed-text API), so I couldn't check timestamps, and I won't embed a stretch I can't check.
- The intro tells the learner to skip the Python 2 asides, and corrects one gloss: `6 + 4 / 2` prints `8.0`, not `8`.

**Done**

- `content/topics/py.arithmetic`, status `ready`:
  - **Practice:**
    - a worked example (135 seconds with `/`, `//` and `%`);
    - three questions: which line prints `3`, a precedence prediction, and `6 / 3` giving `2.0` (mixing in topic 2's types);
    - filling in operators for egg boxes (it's a syntax error until every gap is filled, and the prompt says so);
    - Celsius to Fahrenheit.
  - **Prove it:**
    - build: a pizza party with `//`, `%` and `/`;
    - debug: splitting a bill, with a `TypeError` from `"Total: " + total` and a silent `food + drinks / people`;
    - explain: `/`, `//` and `%` with 17 cookies.
  - **Review pool:** three items. Skills: `operators`, `precedence` and `div-mod` (3 follow-up candidates each).
  - Every exercise that could be passed by typing in the output has a `run_with` check and a "typed-in" known-wrong solution.
- Checked: every output and error message on Python 3.14; the feedback for starters and mistakes; the page on a self-stopping dev server.
- Fixed while looking: a reading as the main resource showed its title twice (on the link card and in the credit line). The credit line now shows just the license.
- CLAUDE.md now says how to run a dev server for checking that stops itself.

**Next**

- Topic 5: Strings and input. Then the Module 1 checkpoint, the receipt calculator.

## 2026-11-06: The third lesson, Variables

**Done**

- `content/topics/py.variables`, status `ready`, following the data model's sketch for this topic:
  - **Learn:** CS50P Lecture 0 from 15:16 to 19:54. It covers why a program keeps values, `=` as assignment from right to left, choosing names, and `print(name)` versus `print("name")`. The intro replaces David's "container" picture with name tags: for numbers and text they agree, but only name tags survive lists (Module 5).
  - **More resources:** a Python Tutor link with `a = 3; b = a; a = 5` preloaded and "show numbers as objects" on, so names are drawn as arrows. I checked in a browser that it opens on Python 3.11 with the arrows drawn. Python Tutor is free to use under its terms (© Philip Guo); we only link to it.
  - **Practice:**
    - a worked example following `city` through reassignment and `home = city`;
    - three questions: what `b` refers to after `a = 5`, a trace, and `print("name")` (mixing in topics 1 and 2);
    - filling in a swap with `temp`;
    - rotating three values.
  - **Prove it:**
    - build: swap and print from a blank editor;
    - debug: a lost value from `left = right; right = left`, hidden behind a `rigth` typo;
    - explain: why `b` stays `3`.
  - **Review pool:** four items. Skills: `assignment` (2 follow-up candidates), `trace-values` (4) and `swap` (4).
- **`run_with` in `harness/checks.py`:** reruns the program with other starting values for named variables. Five exercises use it, so retyping `5 3` can't pass. Each also has a "typed-in" known-wrong solution that the checker proves fails. It has 4 unit tests and a new scenario (`check-run-with`). CPython and Pyodide agree, and no existing scenario result changed.
- **The dev server now watches `content/` and `harness/`.** Viewing topic 3 on the owner's dev server showed "Missing practice item" for everything: Vite only watches `web/` for new files, so the glob list of exercises was stale. A small plugin adds the two folders to the watcher. I tested it on a temporary server that shut itself down: a file added under `content/` appeared within 3 seconds, and disappeared when removed.
- The content tests no longer assume a particular topic is unwritten; they pick whichever is still an outline.

**Next**

- Topic 4: Arithmetic.

## 2026-11-06: Mistakes come back, for everything (and the research's timing)

**The owner asked** whether mistakes coming back works for everything, not just the comma question. Yes: any question or code exercise, in practice, proof checks or reviews, in every ready topic. Explain-it-back will join once it's graded (Milestone B).

**Found while checking that:** one miss can open follow-ups for several skills, and they could all pick the same "never answered" question. Missing the recipe card in topic 1 would have shown the shopping-list exercise twice. Fixed with `planCards`: each skill gets its own question where possible, and a shared one is asked once, for both, with per-skill results.

**Decided (the owner):**
- **Timing:** "whatever the science says will make it stick". Successive relearning recommends at least 3 relearning sessions with growing gaps (Rawson & Dunlosky, 2011; Rawson, Dunlosky & Sciartelli, 2013; Cepeda et al., 2008). So: right on 3 different days, coming back after 1, 3 and 7 days. Recorded in ADR-0011 with the references.
- **Code exercises:** "good as is". Missed only if no Check passed that day.

**Also:**
- `everyItem.test.ts` checks every graded item of every ready topic against the real content: a miss must bring back a different question on each of its skills, and never a proof check.
- A test helper changed shared sample data, which made a later test fail. The sample topic now hands out copies.

**Possible later:** the "first session" half of successive relearning, getting it right about 3 times on the day of the miss. The research finds its benefit mostly fades once the later sessions happen.

## 2026-11-06: Mistakes come back (ADR-0011, built)

**Decided**

- ADR-0011 is now Accepted. The owner kept the defaults: right on 2 different days relearns a skill.
- Two refinements, recorded in the ADR and told to the owner:
  - **Timing:** the earlier message said "next day, about 3 days, then a week", but with 2 correct days the week is never reached. It's now: due the next day, then 3 days after a correct day. Correct answers on the day of the miss don't count.
  - **Code:** failing Checks while working something out are part of solving, so a code exercise counts as missed only if no Check passed that day. Questions count on any wrong answer that day.

**Done**

- `web/src/followups/`:
  - **`followUps.ts`:** pure functions for the day-by-day state of each skill and the choice of question (never answered first, then the one answered longest ago; the missed one only if nothing else is left). 20 tests.
  - **`history.ts`:** reads graded attempts from Supabase, 1,000 rows per request. Times are normalized: the server writes `+00:00`, the browser `Z`.
  - **`useFollowUps.ts`:** combines the server history with the events on this device.
- The event log now exposes `getLocalRows()`: what's still in the outbox, plus everything recorded since the page opened. It keeps them after they're sent, so an answer can never vanish between the outbox and the server.
- **Today:**
  - "Mistakes to revisit" with one card per due skill. The question is chosen once per visit, so the card doesn't change while it's being answered, and it shows the result: relearned, back in 3 days, or back tomorrow.
  - "Coming back later" lists what's due on other days.
  - Signed-out, loading and failed states, with "Try again".
  - Today now loads only when visited (it can include code editors).
- Practice items know the `review` context, with no hints.
- Tests: 157 web tests in all (32 new). They cover the rules, paging, the Today page's states and a full answer.

**Tried end to end** on the dev server against the local Supabase, with the local test account:
- a "missed yesterday" answer was put straight into the local database;
- Today showed the comma skill with a *different* question (the new review question);
- a correct answer said "Right! It comes back on Mon, Nov 9";
- the review event landed in `public.events`;
- after a reload, Today showed "Nothing to revisit today" and the skill under "Coming back later".

**Found while building it:** the Today page checked "are the questions chosen?" before "did loading fail?", so a failed load would have shown "Loading…" forever. A test caught it.

**Note:** a dev server records the commit it was *started* on as `content_build` (Vite's `define` runs once at startup). Live builds always record their own commit.

**Next**

- The owner's comma mistake comes back on the live Today page tomorrow, Nov 7.
- Topic 3: Variables.

## 2026-11-06: The second lesson, Values and types

**Done**

- `content/topics/py.values-and-types`, status `ready`:
  - **Learn:** CS50P Lecture 0 from 59:32 (integers) to 1:07:58 (the fixed calculator). The lecture has no stretch dedicated to types and never uses `type()`. But this one shows *why* types matter: typed input is text, so `1` and `2` make `12`. The intro says that `x = 1` and `input()` come in later topics, and that the Run button replaces the `>>>` prompt. Floats (1:14:31) and the Python tutorial's "Numbers" section (PSF License Version 2) are linked as more resources.
  - **Practice:**
    - a worked example, `type()` on four values, explaining the `<class 'str'>` format;
    - three questions: which type is `7.0`, why `print(5)` and `print("5")` look the same (mixing in topic 1), and what `+` does with numbers and with text;
    - a fill-in exercise (one value of each type);
    - a write exercise (add, join, check a type).
  - **Prove it:**
    - build: a type report. Its hidden tests also check that the source uses `type()` three times, so typing the answers out by hand fails.
    - debug: a receipt with a `TypeError` crash on line 4 and a silent `"3" + "2"` on line 3. Fixing the crash reveals the wrong total.
    - explain: the calculator that prints `12`.
  - **Review pool:** three items. Skills: `identify-types` (7 follow-up candidates) and `plus-by-type` (3).
- Checked: every quoted output and error message (Python 3.14, through the harness); the tutorial's anchor and license; the feedback for each starter and wrong answer; the page on the dev server.
- The content loading test now runs for every ready topic.

**Next**

- The owner finishes Programs and print, then Values and types.
- Build ADR-0011: mistakes come back as fresh questions.

## 2026-11-06: Skills, so mistakes can come back (ADR-0011)

**Why:** the owner missed a predict-the-output question about `print` with commas and asked for wrong answers to be remembered and re-tested until they get them right. The miss is already saved in the event log, but nothing brought it back.

**Decided** (the owner chose the order and the approach):

- Write [ADR-0011](decisions/0011-mistakes-come-back.md), proposed. A miss opens a follow-up for each skill the item tests. It comes back as a *different* question on that skill: the next day, then after about 3 days, then a week. It's closed once the skill is answered correctly on 2 different days. A topic can't be Mastered with open follow-ups. It's derived from the event log, so today's miss will be included.
- Build order: topic 2 (Values and types) first, then the feature. Skills go into the content format now, so topic 2 is written ready for it.

**Done**

- Content format:
  - topics declare `skills` (an ID and a description);
  - recall items and exercises list `skills`;
  - the checker requires skills on every graded item of a ready topic, at least 2 follow-up candidates per skill (recall items, fill-in, write, `review_code`), and declared names only. 4 new checker tests.
- The app's content types and loader carry skills, though nothing shows them yet.
- Programs and print:
  - its 4 skills are `print-text`, `print-commas`, `blank-lines` and `read-errors`;
  - a new review question on commas gives the owner's miss two fresh questions to come back as.
  Labeling items doesn't change what they ask, so no `rev` bumps.

**Next**

- Topic 2: Values and types.
- Then the follow-up function and the Today list (ADR-0011).

## 2026-11-06: Fix: video clips looked as long as the whole lecture

**Found by the owner** on their first lesson. The page said "about 40 minutes", but the embedded video showed 1 hour 45 minutes. YouTube's player always displays the full video's length, even when `start` and `end` limit what plays, and nothing on the page said so.

**Done**

- Above an embedded clip, the page now says: "This clip: 0:24 to 9:51 (about 9 minutes). The player shows the length of the whole video, but it stops by itself at 9:51." The video is linked to that note for screen readers.
- The topic header now reads "About 40 minutes for the whole topic".
- The lesson's intro no longer gives its own length, so the clip note is the one place that states it.
- Tests cover the note, for the sample topic and the real one.

**Lesson:** check the page the way a learner sees it, including what third-party widgets (like YouTube's player) show on their own.

## 2026-11-06: The first lesson, Programs and print

**Done**

- `content/topics/py.programs-and-print`, status `ready`:
  - **Learn:** a 9.5-minute segment of CS50P Lecture 0, from 0:24 (after the opening music) to 9:51 (the fixed program running again). It covers the first program, the interpreter reading top to bottom, functions, arguments and side effects, then a deliberate missing `)` and its syntax error. Before it, an intro on what to watch for, which notes that the Run button replaces VS Code and the terminal. After it, a recap in our own words.
  - **Practice:**
    - a worked example (a text line, a blank line, and two pieces joined by a comma);
    - a question on what quotes do;
    - a predict-the-output question;
    - a question on reading a `NameError`;
    - a fill-in exercise (shopping list);
    - a write exercise (recipe card).
  - **Prove it:**
    - build: a banner, with hidden tests;
    - debug: a syntax error that hides a `NameError`, so the learner fixes one error, runs again, and reads the next;
    - explain: why earlier lines still print, what the error says, and how to fix it.
  - **Review pool:** a syntax-error question, a predict-the-output question, and a postcard exercise.
- Checked:
  - the video ID and its embeddability through YouTube's oEmbed;
  - the timestamps, from CS50's published subtitles (used only to find times, never copied);
  - every quoted error message, by running it through the harness on Python 3.14;
  - the feedback for each starter and wrong answer, by running them through `harness/cli.py check`.
- App fixes found by looking at the real topic:
  - quiz answer choices now render Markdown (they showed raw backticks);
  - code boxes had the same color as cards in dark mode.
- Tests: the real topic loads through the actual build pipeline (lesson, questions, exercise code) and its page renders.

**Decided**

- While the owner is the only learner, a topic goes straight to `ready`. Their first pass on the live site is the review, and follow-up fixes bump the `rev` of any item whose meaning changes. Recorded in the v1 spec and the content README.
- Vary where the right answer sits in multiple-choice questions. Shuffling the choices on screen would help reviews; it's planned for when reviews arrive (Milestone C).
- The owner's idea of a practice-hours tracker, counting deliberate practice toward 10,000 hours, is on the roadmap for Phase 2.

**Next**

- The owner learns Programs and print on the live site and reports anything confusing.
- Write the next topic: Values and types.

## 2026-11-06: Saving progress (the event log, F6)

**Done**

- `web/src/events/`:
  - the **event log** turns what a page reports into a complete row: a browser-made ID, the learner, the study session, the time, and the commit;
  - the **outbox** in `localStorage` keeps events until the server confirms them;
  - **sync** sends batches as an upsert that ignores duplicates, so retries are safe.
- When saving fails:
  - retries wait 5 s, 10 s, 20 s… up to 5 minutes;
  - the app tries again at once when the browser comes back online or the tab is shown again;
  - an event the server refuses is set aside so it can't block the rest.
- Recorded on topic pages:
  - `lesson_view`;
  - `answer` (multiple choice, predict the output);
  - `code_run`, `code_check` and `hint` (exercises);
  - the context is `practice` or `prove`.
  Attempt time runs from the first click or focus inside an item. The exact `data` per event type is now in the data model.
- `vite.config.ts` writes the git commit into the build as `content_build`.
- A "Not saved yet" badge in the header. Topic pages tell signed-out visitors their answers won't be saved.
- Tests: 41 new web tests (120 in total). They cover the outbox (including two tabs), batching, retries with fake timers, setting aside a refused event, signed-out and still-loading sign-in, sessions, and what each page records.

**Tried end to end** against the local Supabase in Docker, signed in by email link through Mailpit, with the sample topic copied in temporarily:
- a lesson view, a correct answer (2.4 s) and a failed check (with its code) appeared in `public.events` within 70 ms, with the right user, revision and commit;
- with the API container stopped, an answer showed "Not saved yet";
- after restarting it, the answer arrived 7 s later on its own, keeping its original time. It was received 15 s after it happened.

**Lessons**

- On this Windows machine, stopping a background shell task doesn't stop the Vite server it started. Two test servers (ports 5174 and 5175) were left running, and ending processes needs the owner's permission. Next time, start at most one test server per session and plan how it will be closed.
- The shared test setup now clears `localStorage` after each test, but only where it exists: the Pyodide tests run in plain Node.

**Next**

- Write the first real topic, `py.programs-and-print`, then the rest of Module 1.

## 2026-11-06: Content pipeline, part 2 (topic pages)

**Done**

- The app reads `content/` at build time:
  - a small Vite plugin turns YAML into data;
  - `@mdx-js/rollup` compiles lessons;
  - Python files are loaded with `?raw`;
  - `content/content.ts` finds everything with `import.meta.glob`.
  Outlines are bundled into the app, and each topic's lesson and exercises download when its page opens.
- Topic pages:
  - **Learn:** objectives, intro, a privacy-enhanced YouTube embed with start and end times, recap, and more resources.
  - **Practice:** worked example, multiple choice, predict the output, fill in, and write. Hints come one at a time, and the reference solution appears after a pass.
  - **Prove it:** build and debug, plus the explain prompt. Its rubric and model answer are never sent to the screen.
- The map now lists all 36 topics by module.
- Small additions:
  - per-exercise time limits;
  - an error page with Reload (stale chunks after a deploy);
  - the current page fades while the next one loads.
- The checker now enforces the convention the page relies on: a lesson places only its main resource, `<Resource index={0} />`.
- Tests:
  - 29 new web tests (79 in total);
  - shared test helpers: a fake Python runner, a plain-textbox editor, a sample topic;
  - 2 new checker tests (41 Python tests).

**Found by trying it end to end.** I copied the checker's sample topic into `content/` temporarily, then built the app and clicked through it in the browser on a separate dev server (port 5174). The production build failed: a compiled lesson imports React, but lessons live outside `web/`, so module lookup never reached `web/node_modules`. The fix is `resolve.dedupe: ['react', 'react-dom']` in `vite.config.ts`. After that:
- the lesson, the embed, and every practice item rendered;
- the fill-in starter failed in real Pyodide;
- a correct answer passed and revealed the reference solution;
- the prediction check worked;
- there were no console errors.
The sample topic was removed afterwards. The unit tests couldn't have caught this, because the repo has no lesson files yet.

**Decided**

- The main bundle was already over Vite's 500 kB warning before this change (542 kB, mostly React, React Router and supabase-js). This change adds about 22 kB, mostly the 36 topic outlines. Splitting the bundle is a later job.
- Each content file becomes its own small download (about 20 per topic, fetched in parallel). Grouping them per topic needs Rolldown's chunk groups, which by default pull a grouped file's dependencies (React) in with it. That's risky, so it's left alone until it matters.

**Next**

- Save answers and lesson views to the event log (F6), with a local outbox and sync.
- Write the first real topic, `py.programs-and-print`, then the rest of Module 1.

## 2026-11-06: Content pipeline, part 1 (format and validator)

**Checked first:** the owner's restarted dev server is healthy (fresh process; styles compile; the harness and Supabase modules load).

**Done**

- `content/`: the Python Foundations track and all 36 topics from the approved list, as `planned` outlines with the exact prerequisite graph from the spec. A new `status` field (`planned`, `draft`, `ready`) lets the map be complete before the lessons are written.
- `tools/content_model.py`: pydantic models for every content file. They reject unknown fields, so typos are caught.
- `tools/validate_content.py` checks:
  - file formats, and that IDs match their folders;
  - tracks and modules, prerequisites, and no cycles;
  - the definition of done for `ready` topics;
  - by running them through the harness in a fresh process: reference solutions pass, starters and known-wrong solutions fail, predict-the-output items print what they claim, and code that never stops is reported.
- `harness/cli.py`: a command-line entry the validator and the scenario tests share.
- 14 validator tests, built on a tiny complete topic, each breaking one thing. 39 Python tests in total. A new **Content** CI job runs the validator.

**Next**

- Part 2: the app loads content (YAML and MDX through Vite), with topic pages for lessons and exercises.
- Then saving answers to the event log, and writing Module 1.

## 2026-11-06: First real sign-in; sign-ups closed

- The owner signed in with GitHub on the live site. Supabase shows one user, created through GitHub at 10:25.
- At the owner's request, I used the browser to switch off **"Allow new users to sign up"** in the Supabase dashboard. First I checked the owner's account existed, so they couldn't be locked out.
- Verified independently through the public auth settings endpoint: `disable_signup: true`, with GitHub and email providers enabled. Email sign-in only works for existing accounts now.
- Milestone A remaining: the content pipeline, topic pages and saving answers, and Module 1 content.

## 2026-11-06: Sign-in

**Owner's setup:** a GitHub OAuth app (`education-platform`), the GitHub provider turned on in Supabase, and the Site URL and redirect URLs set to the live address. The OAuth app's GitHub form calls the callback field "redirect URI".

**Done**

- Added supabase-js 2.119, with the PKCE flow. That isn't its default, and it also makes supabase-js remove the one-time `?code=` from the address bar. Settings for local and production live in `src/supabase/config.ts`; the keys are publishable, so public by design.
- `AuthProvider` and `useAuth` track who's signed in; the header shows the name and Sign out; there's a `/sign-in` page.
  - **Live site:** "Sign in with GitHub".
  - **Dev server:** an email-link form instead, since the local Supabase has no GitHub app; the email lands in Mailpit.
- Database types are generated from the schema (`npm run db:types`).
- 6 new tests with a fake sign-in service; 50 web tests in total.
- **End to end against the local Supabase, in a real browser:** I requested a link, fetched the email from Mailpit's API, and opened the link. That signed me in, removed the code from the address, and showed the email in the header. The trigger created the profile (no name, `allowed = false`), and Sign out worked.

**Notes**

- Supabase accepts a sign-in redirect to any port on the Site URL's host name. So a second dev server on `localhost:5174` works without config changes.
- The owner's dev server from yesterday was still running on port 5173 (IPv6 only, so Windows' port check missed it). I left it alone; it needs a restart.

**Next**

- The owner tries GitHub sign-in on the live site; then we close sign-ups.
- The content pipeline, topic pages and saving answers.

## 2026-11-06: The real database has its tables

- The owner logged in to the Supabase CLI and linked the `education-platform` project. The CLI didn't need the database password; it uses the login.
- Applied the first migration to production with `npx supabase db push --remote --yes`, after a `--dry-run` that listed exactly that one migration. `migration list --remote` shows the local and production histories match.
- Note: Supabase CLI 3 targets the local database unless `--remote` is given. The docs now say so.
- Next: sign-in with GitHub (the owner sets up a GitHub OAuth app and the Supabase provider) and sending events from the app.

## 2026-11-06: Live on Cloudflare; NordPass fix

**Done**

- The owner connected the repo in Cloudflare and switched on the workers.dev address. The app is live at https://education-platform.arasmussen64.workers.dev, and deep links like `/topic/py.variables` work.
  - `web/wrangler.jsonc` now sets `workers_dev` and `preview_urls`, so a deploy can't switch them off.
  - The setup guide now matches Cloudflare's real screen: "Path" under Advanced settings, and no production-branch field.
- Merging to `main` triggered a production build, which succeeded, so automatic deploys work.
- The program-input field is now an editable `<span role="textbox">`. NordPass still popped up on the earlier `<input>`: it has no opt-out attribute for pages, and it read the prompt "What's your name?" as a contact form. Password managers only look at real form fields. A test now checks it stays a span.

**Preview builds: found and fixed** (by reading the build log in the dashboard, at the owner's request)

- The builds didn't fail instantly. GitHub only receives the result at the end, so the start and finish times matched. The builds ran for about 6 minutes, and only the last step failed.
- Cloudflare's default deploy command for pull requests is now `npx wrangler preview` (open beta). It refuses to run without a `previews` block in the Wrangler config. Added `"previews": {}`.
- 6 of those minutes went to installing Python 3.14 that the web build never uses. Cloudflare's build spots a `.python-version` file and installs that Python, on production builds too. The Python version is now pinned with `requires-python = "==3.14.*"` in `pyproject.toml`, and the file is gone. uv still uses 3.14.

**Lesson**

- `cmd | tail` hides `cmd`'s exit code, which made a lint failure look like success locally. CI caught nothing wrong because I fixed it before pushing. Check exit codes directly.

## 2026-11-05: Local Supabase and the first tables

**Owner's setup:** Docker Desktop is installed (engine 29.8, 8 CPUs and 16 GB for Docker), a Supabase project exists, and a Cloudflare account exists.

**Done**

- Added the Supabase CLI (3.0) as a pinned dev dependency in a new root `package.json`, with `db:*` scripts.
- Set up `supabase/`. The local copy skips realtime, file storage and log analytics, which aren't used, to save memory.
- Wrote the first migration:
  - **`profiles`:** created automatically at sign-up. A learner can read their own row and change only `display_name` and `settings`, never `allowed`.
  - **`events`:** append-only. Learners can insert and read only their own rows. `received_at` is always set by the server. A trigger blocks update, delete and truncate even for admins, except for a deliberate whole-account deletion.
- Wrote 18 pgTAP tests for those rules, and a **Database** CI job (throwaway database, `db lint`, `db test`).

- First local start: Postgres 17 came up, the migration applied, lint was clean, and 18/18 tests passed. They also passed in CI (PR #7).
- Added the Cloudflare config (`web/wrangler.jsonc`) for static assets with single-page-app fallback. Wrangler 4.158 is pinned and its telemetry is off. A dry-run deploy succeeded.

**Next**

- One-time steps by the owner ([setup](setup.md)): connect the repo in Cloudflare, which gives the first deploy, then `npx supabase login` and `link`.
- Push the first migration to the cloud project once it's linked.
- Sign-in (needs a GitHub OAuth app) and sending events from the app.

## 2026-11-05: Playground fixes after the owner's first try

**What the owner saw**

- The input box was invisible.
- The greeting didn't print "Hello, Alex!".

**What was wrong**

- **The invisible box:** the owner's dev server had been running since before I changed `vite.config.ts` and installed packages. It got stuck half-updated, serving Tailwind's raw source instead of compiled CSS, so every element lost its styling. A fresh server was fine; the fix is a restart. `CLAUDE.md` and `web/README.md` now say to restart after config or package changes.
- **No "Hello, Alex!":** on the unstyled page, the invisible input boxes sit away from their labels, so the name most likely went into the wrong box. The design was the deeper problem: filling in a box *before* pressing Run isn't how anyone expects Python to work.

**Done**

- Run now behaves like a terminal. When the program calls `input()`, a text field appears right after the prompt with the cursor in it, and Enter sends the line.
  - The harness stops at an unanswered `input()` and reports `waiting_for_input`, instead of raising `EOFError`.
  - The app re-runs the program from the start with every line typed so far.
  - Re-runs use a fixed random seed, so random choices repeat.
  - The stop signal is a `BaseException`, so a learner's `except Exception:` can't swallow it.
- Added 3 scenarios: waiting for a second input, a seeded random program, and `except Exception` around `input()`. All 17 scenarios match between CPython and Pyodide.
- Found while testing in Pyodide: JavaScript `null` arrives in Python as a special "JS null", not `None`, so the app now passes `undefined` instead.
- Testing in a real browser:
  - The full flow worked: Run, type "Alex", Enter, and "Hello, Alex!" appeared.
  - The owner's autofill extension then offered to save "Alex" as contact info. The field no longer uses a `<form>` and carries the usual "ignore me" markers for password managers.
  - After that change, the extension's overlay blocked my browser tools, so the final check is left to the owner.
- Added a "Loading…" screen while on-demand pages load, which fixes a React Router console warning.

**Next**

- The owner restarts their dev server and tries the Playground.
- The content pipeline and validator, then Module 1 content.

## 2026-11-05: Python runs in the browser

**Done**

- Built the browser side of the Python runner:
  - Pyodide 314.0.7 runs in a Web Worker, loaded from the jsDelivr CDN.
  - `PythonRunner` queues requests and replaces the worker when code runs past 5 seconds.
  - A CodeMirror editor with Run and Check, on a temporary Playground page.
- The 14 harness scenarios now also run under real Pyodide (in Node) in the web tests. They match CPython exactly, tracebacks included.
- Checked the production build in a real browser:
  - Pyodide loaded in the background.
  - Run echoed input like a terminal.
  - Check failed, then passed after fixing the code.
  - An infinite loop was stopped after 5.1 seconds while the page stayed responsive.
  - The next run worked 0.1 seconds later.
  - No console errors.
- Made the Playground load on demand: the main bundle dropped from 786 KB to 320 KB.

**Fixed along the way**

- The status message now uses an `<output>` element, as the accessibility lint rule suggested.
- The summary now reads naturally for a single check ("The check passed!" instead of "All 1 checks passed!").
- Tests get their own TypeScript settings with Node types, so app code can't use Node APIs by accident.

**Next**

- The content pipeline and validator, then Module 1 content.
- Local Supabase once Docker Desktop is installed ([setup](setup.md)).

## 2026-11-05: Python test harness

**Done**

- Wrote the shared Python harness (`harness/`): `checks.run()` for tests, the Run and Check logic, and beginner-friendly error messages that only show the learner's own file.
- Added 14 scenarios with expected results I reviewed by hand, plus unit tests. A new CI job runs them with uv, pytest and ruff.
- Installed uv for this user, and Python 3.14 through it.

**Decided**

- Pyodide has a new version scheme (314.0.7 bundles Python 3.14), so the Python tooling targets 3.14.
- The content validator will use the harness's own test runner, not pytest. pytest rewrites `assert` statements in files named `test_*.py`, which changed the messages. Two scenarios that failed only under pytest exposed this.

**Next**

- The browser side: Pyodide in a Web Worker, the editor, Run and Check, and the same scenarios under Pyodide.

## 2026-11-05: Process and environment decisions

**Decided**

- The owner gave standing permission for Claude to merge its own pull requests once CI passes. Explain-it-back questions continue, but they never block merging.
- Supabase's second free project slot is already in use, so the platform gets one cloud project, for real learning only. Development runs a local Supabase in Docker Desktop ([ADR-0010](decisions/0010-environments.md)). The owner chose this over sharing the cloud project with a test account.

**Done**

- Merged the web app scaffold (PR #2).
- Wrote ADR-0010 and a [setup guide](setup.md) for the owner's computer and accounts.

**Next**

- The owner installs Docker Desktop, creates the Supabase project, and creates a Cloudflare account ([setup](setup.md)).
- The Python runner in the browser.

## 2026-11-05: Milestone A starts with the web app scaffold and CI

**Done**

- Merged the v1 spec (PR #1).
- Scaffolded the web app in `web/` with create-vite 9: Vite 8, React 19, TypeScript 7, React Router 8, Tailwind CSS 4, Vitest 5, Oxlint (with accessibility rules) and Prettier.
- Added placeholder pages (Today, the topic map, a topic, and "not found") inside a shared layout.
- The product name lives only in `web/src/config.ts`. A small Vite plugin puts it in the page title (ADR-0006).
- Wrote 5 route tests. Added CI on GitHub Actions: formatting, lint, type-check, tests and build.

**Notes**

- Several tools are newer than expected (React Router 8, Vitest 5, TypeScript 7), so I checked what they export before writing code against them.
- create-vite now defaults to Oxlint instead of ESLint. I kept the default.

**Next**

- The Python runner in the browser: Pyodide in a Web Worker, plus the `checks` test helper.
- The owner creates free Supabase and Cloudflare accounts.

## 2026-11-05: v1 spec

**Done**

- Wrote the [v1 spec](specs/v1.md): 16 features with acceptance criteria, four milestones (A–D), non-functional requirements, and a content definition of done.
- Wrote the [data model](specs/data-model.md): content file formats, the `checks` test helper, the Postgres tables, and the exact rules for topic states.
- Planned the [Python Foundations track](specs/python-foundations.md): 30 topics in 6 modules, each ending with a checkpoint, mostly built around CS50P lectures.
- Proposed ADR-0008 (append-only event log) and ADR-0009 (per-topic reviews, graded automatically).

**Decided** (the owner approved the spec pull request)

- The "prove it" checks, topic states and gating move from Phase 2 into Phase 1. They reuse the exercise engine, and v1 shouldn't call anything Learned without proof.
- ADR-0008 and ADR-0009 accepted.
- The topic list is approved as written.
- AI budget cap: $10 a month to start.

**Next**

- Milestone A: scaffold the app and CI, then the Python runner, the content pipeline, Supabase, the deploy, and Module 1 content.

## 2026-11-05: From idea to project setup

**Done**

- Researched Brilliant, roadmap.sh and Math Academy ([competitors](research/competitors.md)).
- Pinned down the concept through a Q&A ([vision](vision.md)):
  - Adaptive, from total beginner to principal engineer. First track: CS foundations → ML engineering.
  - Core promise: you can *apply* it, not just recognize it.
  - Mastery needs all four proofs: blank editor, explain it back, debug unfamiliar code, delayed review.
  - Gated, with test-out.
  - AI as hint-only tutor, reviewer, practice generator, and an "earn the AI" track.
  - Content: curated free resources plus AI-written supporting material; practice owned by the platform.
  - Free and personal-use first; free hosting; owner full time, learning in the mornings and building in the afternoons.
- Picked the working name **Switchback** (may change).
- Set up the repository: CLAUDE.md, README, CHANGELOG, ADR-0001 to ADR-0007, git config files.
- Backed it up to a private GitHub repo, `education-platform`.

**Decided:** ADR-0001 to ADR-0007 accepted, including the tech stack (ADR-0007): a TypeScript/React app on Cloudflare, Supabase, Pyodide, and Python for tooling and ML. It replaced the earlier "Python backend" idea because free Python hosting sleeps when idle.

**Next**

- Write the v1 spec: feature list, data model, the first 30 Python topics.
- Scaffold the app, CI and first deploy.
