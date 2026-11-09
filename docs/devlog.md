# Devlog

A dated log of each working session: what changed, what was decided, what's next. Newest first.

## 2026-11-09: Parsons problems in every topic

Eighteen more Parsons problems, written to the pattern of the first eleven, so 29 of the track's 30 topics now have one right after the worked example; six are also in their topic's review pool. The validator runs each one's lines in order and checks its decoy against the real lines. 190 recall items; 939 programs run with no problems.

**Why one topic is left out.** Testing with assert's natural programs are a function plus several `assert` lines, and the asserts can go in any order, as can two `def` blocks. A Parsons problem needs exactly one right order, so instead of a contrived item the topic keeps its ladder as it was. The same constraint shaped several items: lines that could swap without changing the output were chained (each line uses the one before) or merged into one print, and every prompt states the output.

**Decisions for you to review:**
1. *One convention is stated rather than forced:* the Modules and libraries item puts `import statistics` first, which Python doesn't require, so the prompt says "the import comes first, as it always does". Everywhere else the order is forced by the program itself.
2. *Reading errors has two decoys* (two misspelled names), the only item with more than one, because spotting the misspelling is the topic.
3. *Review pools gained a Parsons item* in Booleans and comparisons, Tracing code, Nested loops, List algorithms and From spec to program, as well as the three from the first batch. A review session can now pair one with a quick check, since it counts as a code question.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills (ADR-0014) and the lab checker.

## 2026-11-09: Parsons problems

A new kind of practice question, from the Phase 2 list, chosen because it helps most at the start of the track the owner is on: the lines of a short program are scrambled, with a decoy, and the learner puts them back in order. The research (Ericson, Margulieux and Rick, 2017) finds this teaches program structure with less effort than writing from scratch, for the same learning. [ADR-0016](decisions/0016-parsons-problems.md), proposed.

**What changed.** A third recall item type, `parsons`, in the content model and the validator: `lines` in the right order with their indentation, optional `distractors`, a prompt that says what the program prints, an explanation and skills. The validator runs the lines in order (no error, no input) and checks that lines are distinct and that no decoy equals a line; its tests cover a crashing order and a decoy that copies a line. In the app, `ParsonsProblem` shows the scrambled lines in a tray and an empty program with Add, Up, Down and Remove buttons, then Check; right means exactly the solution's lines in order. `PracticeItem` gives it the heading "Put the lines in order" and saves an `answer` event whose data holds the program. Review sessions count it as "code or predict". The scramble is seeded by the item's ID (same every time) and never the solved order.

**Content.** Eleven items, one per topic, right after the worked example: a shopping list of prints (Programs and print), a running total (Variables), an adult check with `if`/`else` (If, elif and else), a countdown (While loops), a sum over a range (For and range), a running sum with prints inside and after the loop (Accumulator patterns), a function defined then called twice (Defining functions), appends and a lookup (Lists), word counting with `get` (Dictionaries), a safe `int()` with `try`/`except` (Exceptions), and write-then-read (Files). Each has one decoy that teaches something: `Print` for `print`, `Total` for `total`, `elif` with no second test, `while count < 0:`, `range(1, 3)`, `total = n`, `def greet():`, `append[...]`, `counts[word] + 1`, `except NameError:`, `f.write(hello)`. Three are also in review pools (Variables, For and range, Exceptions).

**Numbers.** 172 recall items (11 new); the validator runs 921 programs with no problems; 409 web tests (6 new) and 39 tool tests pass.

**Decisions for you to review:**
1. *Buttons, not drag-and-drop.* Add, Up, Down and Remove work with a keyboard and on a phone and are easy to test; dragging can be layered on later without changing the item format.
2. *One-dimensional Parsons:* lines keep their indentation and the learner only orders them. Setting indentation too (the two-dimensional kind) can be an option on the item later.
3. *The prompt states the output,* so every item has exactly one right order; the content checklist says to avoid lines that could swap without changing the output, because the validator can't catch that.
4. *The scramble is fixed per item* (seeded by its ID), so a question looks the same when it comes back, and it's never the solved order.
5. *Placed right after the worked example* in each practice ladder, where the research puts it, which makes the first topics' ladders one step longer (Programs and print now has 7 practice items).
6. *An ADR for a new item type,* since it changes the content format and the event data; proposed until you accept it.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills (ADR-0014) and the lab checker.

## 2026-11-09: Practice hours on the Today page

The owner's own idea from 2026-11-06, pulled forward from Phase 2 because it needed nothing new recorded: every graded attempt has saved its `duration_ms` since the event log began.

**What changed.** `Attempt` now carries `duration_ms` (the server query selects it; a row without one leaves it out). `progress/practiceTime.ts` adds the durations up, all time and the last 7 days, counting at most 30 minutes per attempt, and names the next milestone. The Today page shows it below Next up as "Practice hours": the total, the recent part, a progress bar toward the next milestone, and the rule in one line ("Counting the time spent on answers, Checks and reviews, not time with the site open"). With nothing counted yet it says so. No extra request: the Today page already loads every attempt for the reviews and the plan.

**Decisions for you to review:**
1. *A 30-minute cap per attempt.* An attempt's duration runs from the first touch of an item, or the previous attempt, to this one, so a page left open overnight would record hours. Capping each attempt at 30 minutes keeps the count honest; a long blank-editor build without a Check in between is undercounted a little, which seemed the right side to err on. The number lives in one constant.
2. *Milestones start at 1 hour,* not 10 as the roadmap said, so a new learner sees the first one within a week; then 5, 10, 25, 50, 100, 250, 500, 1,000, 2,500, 5,000, 10,000.
3. *"Recent" means the last 7 days,* rolling, rather than the calendar week, because it needs no decision about which day a week starts on.
4. *It lives on the Today page,* under the plan, rather than on the Account page, because that's the page the learner sees every day and the number is meant to be encouraging.
5. *The learning-science doc gained a row for deliberate practice,* with the note that "10,000 hours" is a popularization of Ericsson's work, not a rule, so the tracker is read the way it's meant.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills (ADR-0014) and the lab checker.

## 2026-11-09: A smaller first download: outline-only tracks load on demand

The last item of Milestone D, noted as a chore on 2026-11-08 when the cloud track's outlines went on the map: 357 topics nobody can open yet were being downloaded by every visitor, in the app's main file.

**What changed.** `content.ts` bundles the tracks and the main track's outlines as before, but leaves out the cloud track's (`csa.*`). Those live in their own module, `content/outlines/cloud-solutions-architect.ts`, which Vite turns into a separate file. `loadTrackTopics(trackId)` downloads it once and adds its topics to the same lookup `getTopic` uses; `trackTopicsLoaded` says whether that has happened; `loadTrackOf(topicId)` does it for whichever track a topic belongs to. The map page shows "Loading this track's map…" until the outlines arrive, and a Try again if the download fails; the topic loader awaits them before looking the topic up. The Today page, the follow-ups and the interleaved questions are unchanged: they only look at topics bundled in, which is right because a lazy track has no open topic, and `content.lazy.test.ts` fails the day one does.

**Numbers.** The main file went from 1,034 KB to 853 KB (260 KB to 221 KB gzipped). The cloud outlines are a 181 KB file (37 KB gzipped) that most visits never download. 393 web tests pass, 4 of them new.

**Decisions for you to review:**
1. *Which tracks load lazily is decided by hand:* a module per outline-only track, its pattern left out of the main glob, and a line in `LAZY_TRACKS`. A build-time rule ("any track with no open topic") would need a Vite plugin that watches the content folder for changes; two lines and a test seemed the better trade. When the cloud track gets its first ready topic (the Stage 1 drills), either bundle it back in or teach the Today page to load the tracks the learner has progress in; the test will remind whoever does it.
2. *Milestone D is built but not all live.* Every item on its list is ticked, but the proxy deploy, the problem-reports migration and the tutor test-set run still wait for your go, as do ADR-0014 and ADR-0015. The roadmap keeps "current phase: Milestone D" until those are done; say the word and I'll move it on to Phase 2 planning.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills, which need ADR-0014's decision on how cloud work is proven, and the lab checker.

## 2026-11-09: Module 6, Real programs, written; the Python Foundations track is complete

Five topics and Checkpoint 6, the module where programs meet the world: input that's wrong, files on disk, data in CSVs, code other people wrote, and a spec instead of a recipe. Written while the owner was away; decisions at the end.

**Resources.** Exceptions is built on CS50P Lecture 3 (`LW7g1169v7w`), 0:28 to 26:30: a `ValueError` from `int()`, `try`/`except`, where the risky line goes, `else`, and `while True` around it all; the rest of the lecture (`get_int` as a function, `pass`, a prompt parameter, `raise`) is linked. Files is the text-file half of Lecture 6 (`KD-Yoel6EVQ`), 0:28 to 30:26 (names.txt, `"w"` against `"a"`, `with`, `readlines`, `for line in file`, `rstrip`, sorting). CSV data is the `csv` module section of the same lecture, 1:01:35 to 1:19:02 (`csv.reader`, `DictReader`, `writer`, `DictWriter`), with the `split(",")` part linked. Modules and libraries is Lecture 4 (`MztLZWibctI`), 0:28 to 19:13 (`import random`, `from random import choice`, `randint`, `shuffle`, `statistics.mean`), with its last seven minutes, `sayings.py` and `__name__`, linked as a second resource (the lesson format shows one embed). From spec to program has no video: the lesson is the platform's own, and the reading is Think Python's section 6.4, Incremental development (3rd edition, CC BY-NC-SA 4.0), which grows a `distance` function from a stub with scaffolding prints. Python docs anchors: the tutorial's errors (handling, raising), input and output (reading and writing files) and modules (up to executing modules as scripts) sections, and `csv.DictReader`.

**What each topic drives at:**
- *Exceptions*: `try`/`except ValueError` (name the error; a bare except hides bugs), the risky line inside `try` and its use in `else` or after a `return`, `while True` with `try` and `return` on success, `raise ValueError("...")` when a function is given something it can't work with, `as error`. The debug catches `NameError`, has `int()` outside the `try`, and returns from the `except`.
- *Files*: `with open(path, mode) as f` (closes the file, even on an error), `"w"` erases and `"a"` appends, `write` adds no `\n`, `for line in f` with `rstrip()`, `readlines`, `except FileNotFoundError`, numbers come back as text. Tests create their own files with `Path.write_text` and check the learner's with `read_text`. The debug opens for writing with `"r"`, writes without `\n`, and prints lines with their line breaks still on.
- *CSV data*: the shape (header line, one record per line), `csv.DictReader` giving one dictionary per row with string values, `list(...)` inside the `with`, totals and counts by group with a dictionary, filtering rows. The debug reads after the file has closed, adds text as if it were numbers, and uses `"Item"` for `"item"`.
- *Modules and libraries*: `import m` then `m.f()`, `from m import f` and its trade-off, `random` (`choice`, `randint`, `shuffle` returning `None`), `statistics.mean` and `median`, `math.sqrt`, `floor` and `pi`, a file as a module, and why `if __name__ == "__main__":` finally gets its full explanation; a hidden test imports the learner's file and checks that importing prints nothing. The debug uses `random` without importing it, calls `sqrt` without `math.`, and calls `main()` bare.
- *From spec to program*: the method as a checklist: examples (ordinary, boundaries, just past them, empty), gaps written down and asked about, functions planned as name, inputs and result and written as stubs, asserts from the examples that must fail first, one function at a time. The worked example is a quiz scorer with its spec and examples kept at the top of the file. The build is a prose spec for car park fees (a first hour, part hours, a daily maximum, 0 minutes); the debug is a program that disagrees with the spec at the top of its own file in three places.

**Checkpoint 6, CSV report tool (the capstone):** a prose spec: a sales CSV with bad rows (a blank or non-numeric amount), skipped and counted; totals by region in first-seen order; a report written to `report.txt` and printed. `write_sample` is given, so there's a file to work on; the learner writes `read_rows`, `amount_of` (a number or `None`, via `try`), `good_rows`, `totals_by_region`, `report_lines`, `write_report`, `test_report` and `main`. Hidden tests cover each function, first-seen order, two-decimal formatting, the empty case, that the rows list is unchanged, every docstring, that the learner's tests fail when `amount_of` calls every row worth 1.0, the printed output, and the file. Five wrong solutions (crashes on the bad row, counts only good rows, opens the report inside the loop, two weak asserts, typed-in) each fail. The debug catches `TypeError` instead of `ValueError` (a crash), overwrites a region's total instead of adding to it, and opens the report file inside the loop so one line survives. The sibling is an attendance report (whole numbers, `int()`); the steps fill in reading and cleaning, totals, the report and file, then the outline; the versions are an expenses report (by category) and a rainfall report (by station, one decimal place).

**Harness.** A new scenario, `check-files`, pins that a test can create a file and the learner's program can read and write files in the working folder, identically in CPython and Pyodide (its in-memory file system). No harness code changed. `harness/README.md` and `content/README.md` say how file-based tests work.

**Numbers:** 40 exercises and 26 recall items added; 36 topics ready, which is every topic of Modules 1 to 6, the whole Python Foundations track; the validator runs 910 programs over the content, none failing. Web checks (389 tests), Python checks (69 tests) and the build pass.

**Decisions for you to review:**
1. *Think Python is the first main resource that isn't CS50's or the PSF's:* section 6.4 of the 3rd edition, CC BY-NC-SA 4.0 (the same license family as CS50's material), linked, not copied. The spec said "AI-written lesson" for From spec to program; the lesson is ours, and the reading backs it.
2. *Modules and libraries links its second clip instead of embedding it.* The lesson format shows one embed and lists the other resources after the lesson, so the `sayings.py` clip (seven minutes) is listed there with its timestamps. Allowing two embeds would be a small web change if you'd rather.
3. *A bad CSV row means a blank or non-numeric amount, nothing else.* A row with a missing field (fewer commas) makes `DictReader` give `None`, which `float()` rejects with a `TypeError`, not a `ValueError`. I kept that case out of the spec and the tests so the module teaches one error at a time; it's a note for a later data-cleaning topic.
4. *The spec-to-program build and the capstone give the function names* ("so the checks can find them") but not the algorithm or the edge cases; those have to come from reading the spec. That's the compromise between a real spec and a machine-checkable one.
5. *Checkpoint 6 hands the learner `write_sample`,* the way Checkpoint 5 handed over `STUDENTS`: typing a CSV by hand isn't the skill being proven, and the hidden tests write their own files anyway.
6. *The checkpoint's reference solution totals with a running total over the dictionary's keys,* which Module 5 taught, rather than `sum(totals.values())`; a learner may use either.
7. *Windows's `newline=""` for CSV writing is mentioned once, in the CSV recap, and not tested:* files in the browser sandbox don't have the problem.

**Next:** the Python Foundations track is complete, so the owner can learn on it end to end. Left in Milestone D: the lazy-outlines bundle chore. After that, the cloud track's Stage 1 drills and the lab checker (ADR-0014). The proxy deploy, the problem-reports migration and the tutor test-set run still wait for your go.

## 2026-11-09: Module 5, Collections, written

Five topics and Checkpoint 5, the module where a variable stops holding one thing. Written while the owner was away; decisions at the end.

**Resources.** Three more clips of CS50P Lecture 2 (`-7xg8pGcP6w`), timed from its subtitles: the list of students, indexing from 0, looping and `range(len(...))`, 34:55 to 45:36 (Lists); the dictionary of houses and looping over its keys, 45:36 to 56:11 (Dictionaries); one dictionary per student and a list of them, 56:11 to 1:05:56 (Nested data, with a note to read past the `lambda` sort near the end). List algorithms has no clip: the Python tutorial's More on Lists and Looping Techniques sections, and the filter/transform patterns in the platform's own words. References and mutation is built around two Python Tutor programs, one drawing a second name and a copy as arrows, one drawing a function that changes the caller's list and one that only rebinds its parameter; the reading is Ned Batchelder's "Facts and myths about Python names and values", linked (it's his copyright, so nothing is copied), with his PyCon 2015 talk linked too (video `_AEJHKGk9ns`, confirmed through PyVideo; standard YouTube license, so a link rather than an embed).

**What each topic drives at:**
- *Lists*: make, index from 0 and −1, `len`; replace, `append`, `del`, `in`; items versus positions; `append` returns `None`; `split()` turns a string into a list of words. The debug has `scores = scores.append(100)`, an index one past the end, and a loop that prints positions instead of items.
- *List algorithms*: filter and transform as a loop with `append` into a new list; search returning the first position or −1; `sorted` (new list, `reverse=True`) against `.sort()` (in place, `None`); slices and `min`/`max`/`sum`. The debug has `ordered = scores.sort()`, a slice two long, and a search that keeps the last match.
- *References and mutation*: two names, one list; assignment never copies; `list()`, `[:]`, `copy()`; `==` against `is`; a function that mutates its argument against one that rebinds its parameter; prefer returning new lists. Tests check the original is unchanged and that the result `is not` the input. The debug has an `add_item` that mutates, a backup that's an alias, and `shopping = shopping.append(...)`.
- *Dictionaries*: curly braces, lookup by key, `KeyError`, add/change/`del`/`in`/`len`, looping gives keys, `items()`, counting both ways. The debug has a count that never starts, a loop over `items()` used as keys, and a lookup of a missing key.
- *Nested data*: a list of lists read outside in (`grid[row][col]`, row loop with cell loop); a list of dictionaries as records; choosing the shape; copies of nested data share the inner lists. The debug appends whole records instead of names, uses `"Name"` for `"name"`, and swaps row and column.

**Checkpoint 5, gradebook:** `STUDENTS`, a list of records each holding a scores list; `average(scores)`, `letter_grade(average)` with its boundaries, `best_student(students)` (first of a tie), `report_lines(students)` returning the lines and a `Best:` line, `test_gradebook()` with at least four asserts, `main` printing the lines, both under the guard. Hidden tests check the boundaries exactly (90, 89.9, 80, 70, 60, 59.9), the tie, the lines for another list, that no function changes the data, every docstring, that the learner's tests fail for a `letter_grade` that always says A, and the program's output. Five wrong solutions (an `average` that sorts in place, `>` for `>=`, tests that only check A grades, no docstrings, typed-in) each fail their test. The debug divides by one too many, grades with `>`, and consumes the list it reports on with `pop`, so the last line counts zero students. The sibling is an inventory report; the versions are team stats (points, star/starter/bench) and a weather report (temperatures, hot/mild/cold).

**Numbers:** 39 exercises and 27 recall items added; 30 topics ready, which is every topic of Modules 1 to 5; the validator runs 749 programs over the content, none failing. Web checks, Python checks and the build pass.

**Decisions for you to review:**
1. *`split()` is introduced in Lists* (a string's words as a list) and used in Dictionaries' word counting; string methods otherwise wait, as before.
2. *Ned Batchelder's article and talk are linked, never embedded or quoted:* the article is his copyright and the talk is under YouTube's standard license. They're the only non-CC, non-PSF resources so far; the spec named them.
3. *Comprehensions, `lambda` and `enumerate` are named as shortcuts for later,* not taught. The filter/transform loop is the pattern every exercise uses, because it generalizes and because it's what the capstone's CSV work needs.
4. *"Leaves the data alone" is a hidden test in every build of the module,* and in the checkpoint it's one of the named skills a failure brings back. Mutation bugs otherwise go unnoticed until much later.
5. *Checkpoint 5 keeps its data in a constant* (`STUDENTS`) and its functions take the list as a parameter, so the tests can pass other data; the alternative, functions that read the global, would have taught the opposite of Module 4.

**Next:** Module 6 (Real programs: exceptions, files, CSV, modules, spec to program, and the CSV capstone), which ends the Python Foundations track; then the lazy-outlines bundle chore. The proxy deploy, the problem-reports migration and the tutor test-set run still wait for your go.

## 2026-11-09: Module 4, Functions, written

Five topics and Checkpoint 4, written overnight while the owner was away, so the content stays a module ahead. Decisions are listed at the end for review.

**Resources.** CS50P again, timed from CS50's subtitles (downloaded from the course's CDN, used only to find times): the end of Lecture 0 (`JP7ITIXGpHk`) carries two topics, `def`, parameters, default values, `main()` and the first brush with scope from 1:26:44 to 1:41:22, then `return` and the `square` function to 1:45:36; Lecture 9 (`6pgodt1mezg`) gives scope its clip, the bank balance that can be read but not changed from inside a function, 7:45 to 17:33, stopping where David turns to classes; Lecture 5 (`tIrcxwLqzjQ`) gives testing its clip, from the calculator's `square` to the corner-case discussion, 1:20 to 16:25. Python Tutor draws frames and the call stack for scope. The Python tutorial's Defining Functions and Documentation Strings sections are the readings. Decomposition has no video, as the spec said: its lesson is the platform's own, around a worked example that rebuilds Checkpoint 1's receipt as functions.

**The harness had to grow first.** Exercises now test functions, and `from solution import f` at the top of a test file breaks every test at once when `f` is missing or misnamed. So `checks.py` gained `function(name)`, which loads one function and fails one test with "Define a function called ...", and `printed(f, *args)`, which captures what a call prints. Loading a file runs its top-level code, so `function` swallows what the file prints and turns an `input()` at load time into a plain message about the `__name__` guard. The test runner now also keeps anything printed during a Check out of the report; a program that printed while being loaded was corrupting the command-line checker's JSON. Scenario `check-functions` pins all of this; CPython and Pyodide agree on it (68 harness tests, 20 Pyodide scenarios).

**What each topic drives at:**
- *Defining functions*: define versus call (a bare `hello` does nothing); parameters fill in order, defaults when left out; `main()` defined above and called once at the bottom, and why the order of defs doesn't matter but the call's position does. The debug has a missing colon, swapped arguments and a `main` never called.
- *Return values*: the print-versus-return table; `None` from a function with no `return`; `return` ends the function, which is right for a search and wrong on a loop's first pass. The debug has `print(b)` for `return b`, a `return` inside a loop and an expression with no `return`.
- *Scope and the call stack*: local names die at return; reading a global works, assigning makes a local (`UnboundLocalError`); the `global` keyword exists and the rule is not to use it; frames stacked and unwound. Exercises insist a function use only its parameters, tested by calling it with other values. The debug is a plant that won't grow: three values that never make it between functions.
- *Decomposition*: one job per function, names that say the job, docstrings on the first line (a comment above the def, or a string after the first statement, isn't one), and `main` as the plan. Tests check `__doc__`. The debug has a misplaced docstring, a missing return and a `main` that uses names before setting them.
- *Testing with assert*: a true assert is silent, a false one stops the program; cases that catch bugs (typical, boundary, zero, negative); `test_` functions; and `if __name__ == "__main__":`, taught here because the Check button loads the file. Several exercises test the learner's tests: the function under test is swapped for a broken one and the learner's test function must then fail. A test that compares a function with itself, or asserts `True`, doesn't.

**Checkpoint 4, password checker:** `has_min_length`, `has_digit`, `has_upper`, each a yes/no question; `check_password` returns the first problem in a fixed order; `test_check_password` with at least four asserts; `main` with the input, under the guard, which runs the tests and then the program. The hidden tests check each rule at its boundary, the order of the verdict, every docstring, that the learner's tests pass and would fail for a verdict that always says OK, and the program's output. Five wrong solutions (an unguarded `main`, rules in the wrong order, tests that only check good passwords, no docstrings, typed-in output) each fail the test for their mistake. The debug is a code-word checker with `>` for `>=`, a search that returns on the first character, and a test that expects the wrong verdict. The sibling is a ticket-code checker; the fresh versions are a PIN checker (digits, not all the same, not counting up) and a username checker (length, first character, allowed characters).

**Numbers:** 39 exercises and 27 recall items added; 24 topics ready; the validator runs 596 programs over the content, none failing. Web checks, Python checks and the build pass.

**Decisions for you to review:**
1. *The harness grew two helpers and now hides prints during a Check.* The scenario contract is unchanged (existing expected files are byte-identical) and extended by one scenario. The Check button never showed prints anyway.
2. *The `__name__` guard is taught in Testing with assert and used from there on.* Earlier Module 4 programs call `main()` directly, which is fine because none of them asks for input; the first program that does (the checkpoint) needs the guard, and the lesson says why.
3. *Character kinds use comparisons* (`"0" <= ch <= "9"`, `"A" <= ch <= "Z"`) rather than string methods like `isdigit()`, which come in Module 5. The checkpoint prompts give the idiom.
4. *Lecture 5's clip keeps a try/except passage* (12:30 to 14:05, Module 6 material) because the corner-case discussion after it is the point of the topic; the Intro says to read past it.
5. *Testing the learner's tests* by swapping in a broken function is a pattern worth keeping in later modules: it's the only way the platform can tell real asserts from decorative ones.
6. *Estimates* are 40 to 45 minutes per topic, as in Module 3.

**Next:** Module 5 (collections), then the lazy-outlines bundle chore. The proxy deploy, the problem-reports migration and the tutor test-set run still wait for your go.

## 2026-11-08: Report a problem

Milestone D's F15, small and self-contained: a way for the learner to say "this is wrong" from the page where it's wrong, so content mistakes don't get lost.

**The table.** Migration `problem_reports`: who, when, `topic_id`, `item_id` (an item, `lesson`, `explain`, or null for the topic), `item_rev`, a 1 to 2,000 character `message`, and `status` (`open` or `resolved`). Row-level security lets a learner insert and read their own rows; `status` is left out of their insert grant, so every report starts open and only the owner, in the dashboard, resolves it. Nine pgTAP tests cover all of that, including that a learner can't report in someone else's name or delete a report.

**The page.** `ReportProblem` (`web/src/reports/`) is a quiet "Report a problem" link that opens a box with a Send button; it's placed in three spots: the bottom of every `PracticeItem` card (so practice, proof and review items all have it, with the item's `rev`), under the lesson (`item_id: lesson`), and under the explain check (`item_id: explain`). `sendReport` inserts straight into the table and never throws; the box keeps the text on failure. Hidden when signed out, like the tutor.

**Tests:** 6 new web tests, 351 pass; 9 new database tests, which CI runs (Docker isn't running on this machine, so they weren't run locally). Format, lint, types pass.

**Decisions for you to review:**
1. *Where reports are read:* in the Supabase dashboard's table editor, for now. A "Your reports" list on the account page, and an owner's inbox, can come when there's more than one learner.
2. *`database.types.ts` was edited by hand* to add the table, in the exact shape `npm run db:types` generates, because the generator needs the local database and Docker was off. Running `npm run db:types` once Docker is up should change nothing; if it does, keep the generated version.
3. *No event is recorded for a report,* since the report is itself the record and the table is the owner's to-do list.

**To go live (needs your go):** `npx supabase db push --remote --dry-run` should list only `20261109063021_problem_reports.sql`; then the same command with `--yes` applies it. Until then, sending a report on the live site fails politely ("couldn't be sent").

**Next:** Module 4 (functions), then the lazy-outlines bundle chore.

## 2026-11-08: The hint-only tutor

Milestone D's first item, F13, built on the proxy that already grades explanations. The design is [ADR-0015](decisions/0015-hint-only-tutor.md), proposed; the owner was away, so it's built as proposed and waits for their review and the deploy.

**The proxy** (`supabase/functions/ai/`) now has two actions. `tutor.ts` builds the request: the exercise's prompt, written hints and reference solution, the learner's code, a summary of their latest Check, the tutor's earlier replies, and the learner's question, each in its own tagged block with the learner's text stripped of our tags; the rung is chosen from how many hints came before (nudge, concept, specific, step) and named at the end of the message; the reply is structured output with one `hint` field. `readHint` then keeps it safe: more than 600 characters, more than two lines of fenced code, or two or more lines copied from the solution (compared without spaces or capitals, ignoring lines under 10 characters), and the reply is replaced by the exercise's next written hint, or a fixed hint for the rung. `handler.ts` grew `readHintRequest` with its size limits, and a `completeCall` step shared by both actions: ask, log (even an unusable answer, with its cost), answer. `index.ts` wires `TUTOR_MODEL` and `TUTOR_EFFORT` (defaults: Claude Haiku 5.5, low). No migration: `ai_calls.action` already allowed `tutor_hint`.

**The test set** (`tutor-test-set/`): nine conversations on five real exercises from Modules 1 to 3, five of them trying to get the answer out (outright, "answer mode", "I'm the teacher", a plea, a `# SYSTEM:` comment in the code) and four honest asks at different rungs. Each names text the reply must not contain. `npm run fn:eval:tutor` runs them against Claude, prints every reply, and fails on a replaced reply or a forbidden line. It costs about a cent on Haiku, so the owner runs it.

**The page.** `TutorBox` (`web/src/tutor/`) sits under the written hints of a fill-in or write exercise in practice: an optional "What are you stuck on?" line, a button, and the exchanges so far, each hint labelled with its rung. Six asks, then it points back to the recap. `CodeRunner` reports the code as it's typed, so the tutor sees unsaved work; `ExerciseView` keeps the code and the latest Check, and counts tutor hints with written ones in `hints_used`. `PracticeItem` switches the tutor on for the practice context only and saves each hint as a `hint` event with `source: tutor`, the rung, `replaced`, the question, the call ID and the model. Signed-out visitors don't see the box at all; the page already asks them to sign in once.

**Tests:** 38 Deno tests on the proxy (12 new), 345 web tests (14 new). Format, lint, types and the build pass. The pricing page was checked before reusing the price table: Haiku 5.5 $0.10/$0.50, Sonnet 5.5 $2/$10, Opus 5.5 $4/$20 per million tokens, unchanged.

**Decisions for you to review:**
1. *The tutor is practice-only and also on in a checkpoint's "Stuck?" steps,* which are fill-ins with hints and were always meant as practice. Off in fresh versions, which are proof.
2. *Six asks per exercise.* A guess at where "the next step" would start dictating the solution. Tune it from the `ai_calls` log.
3. *Hidden when signed out* rather than shown with a sign-in link, to keep the page quiet; the explain check keeps its link because it's a single box.
4. *The reference solution travels from the browser to the proxy,* as the model answer already does (ADR-0013); the same "fix before other learners" note applies.
5. *Default model Haiku 5.5 at low effort,* like grading, pending the test-set run you approve. If hints read poorly, try `TUTOR_EFFORT=medium` before a bigger model.

**To go live (needs your go):** `npx supabase functions deploy ai --no-verify-jwt --yes`, then `npm run fn:eval:tutor` to read the hints. Until the deploy, the live site's box says the tutor isn't available.

**Next:** problem reports (F15), then Module 4 (functions) and the lazy-outlines bundle chore.

## 2026-11-08: Module 3, Loops, written

Five topics and Checkpoint 3, the content item of Milestone C, written while the owner is away (they asked for building to continue, with decisions made by best judgement and written down here; see *Decisions for you to review* below).

**Resources.** Lecture 2 of CS50P (Loops, video `-7xg8pGcP6w`) carries four topics, in clips whose times came from CS50's published subtitles: `while` and the accidental infinite loop, 0:28 to 16:13; `for`, lists as "these values", `range` and `_`, to 26:47; asking the user for a positive number with `while True`, `continue` and `break`, to 31:34; and the Mario section, a column, a row and a square of bricks, 1:05:56 to 1:19:15. Strings as sequences is built on the Text section of Python's own tutorial, with Python Tutor walking `for ch in word`. The Python tutorial's `while`, `range` and `break`/`continue` sections are linked as readings. Every lesson is the platform's own words (ADR-0004).

**What each topic drives at:**
- *while loops*: the condition is checked before each pass, so a loop can run zero times; a counting loop's three parts (start, test, update); infinite loops and how to stop one. The debug is a doubling program that adds 2, overshoots with `<=`, and counts its steps outside the loop.
- *for and range*: the stop value is never included; `range(start, stop, step)`; `_` for a value that isn't used; when `for` fits and when `while` does. The debug has `range(1, n)`, a variable printed after the loop that ends with the wrong value, and a `Ready` line that prints its counter.
- *Accumulator patterns*: the before/inside/after shape; running totals and counts; best-so-far and its starting value; `while True` with `break` and `continue`. The build reads numbers until 0 and reports count, total and largest. The debug has `total = 0` inside the loop, an off-by-one range, and `//` where `/` was meant.
- *Strings as sequences*: positions from 0, negatives from the end, slices that stop before their stop, `len()`, and `for ch in text`. The build prints initials; the debug has `word[1]` for the first letter, `word[len(word)]` (an `IndexError` to read first) and a slice one too long.
- *Nested loops*: the inner loop runs completely on every pass of the outer; `end=""` and the bare `print()`; patterns from the loop variables. The build is a right-aligned pyramid; the debug is a times table with a short range, `row * row`, and the line break inside the inner loop.

**Checkpoint 3, text statistics:** from a line of words separated by single spaces, the number of words and letters, the longest word (the first of equals) and a bar per word, using loops and strings only, because lists and `split()` are Module 5. The crux is the last word, which has no space after it: it's a hidden test of its own (`test_last_word`), the point of the sibling example (a week of weather, with the longest sunny streak), the subject of a step and of the explain. Five wrong solutions each fail the test for their mistake. The debug draws a triangle and counts its stars, with `range(1, n)`, a `print()` indented into the inner loop, and `star` for `stars`. The fresh versions are number statistics (digits built up as text, then `int()`) and match results (`W`/`L` streaks, a bar per streak). Every test names skills across Modules 1 to 3.

**Numbers:** 39 exercises and 26 recall items added; the validator runs 441 programs over the content, none failing; 18 topics are ready. Web checks, Python checks and the build all pass. The main bundle grew to 894 KB (233 KB gzipped), mostly content; the lazy-outlines chore noted on 2026-11-08 is now worth doing.

**Decisions for you to review:**
1. *Accumulators have no clip of their own.* CS50P's lecture doesn't teach sums, counts or maximums as patterns, so the lesson's Intro and Recap carry them, and the clip covers `while True`, `break` and `continue`. A Runestone chapter on the accumulator pattern was considered as a reading, but its license couldn't be read (the site sits behind a bot check), so it was left out, as ADR-0004 asks.
2. *The nested-loops clip includes a function.* David writes the square inside `def print_square(size):`, and functions are Module 4. The Intro says to read the indented lines as the program with `size` standing for 3, and to stop when he splits the code into `print_row`. Cutting the clip before the function would have cut before the nested loop.
3. *"Letters", not "characters".* The spec says Checkpoint 3 counts characters; the checkpoint counts non-space characters and labels them `Letters:`, because counting every character is just `len(text)` and tests nothing.
4. *Time estimates* are 40 to 45 minutes per topic rather than the outline's 35, to match a lesson, six or seven practice items and three proofs.
5. *Module 3's debug exercises each hide one crash* (a `NameError` or `IndexError`) among the three bugs, so Reading errors keeps being practised. That's a pattern worth keeping in later modules.

**Next:** Milestone D (the hint-only tutor and problem reports), the lazy-outlines bundle chore, and Module 4 (functions), in whichever order keeps the owner ahead of the content.

## 2026-11-08: Interleaved practice

The last app piece of Milestone C (F5): each practice ladder mixes in one recall question from an earlier topic, so the learner has to decide which idea applies rather than knowing it from the page they're on.

- `web/src/practice/interleave.ts`: `earlierTopicFor` walks the topic's most recent prerequisite, looking through a checkpoint to the last topic before it (so Module 2's first topic borrows from Strings and input), and `interleavedItem` picks one of that topic's recall questions, rotating day by day and stable within a day.
- The topic page's loader fetches the earlier topic's content alongside the topic's own, and `Practice` splices the question in after the topic's own recall items, labelled "from <topic>". The answer is recorded under the earlier topic, so it counts toward that topic's follow-ups and reviews.
- 10 new tests (the chooser, the loader, the ladder). Milestone C's app work is done; what's left in C is content: Module 3.

## 2026-11-08: Reviews, timed to how fast you forget

Milestone C starts with ADR-0009: one review card per Learned topic, scheduled by FSRS, with sessions rated from performance.

**The scheduler is our own code.** `ts-fsrs` is at version 6 with a new, sparsely documented API (an awaited factory, model plug-ins), and the ML capstone is to fit this very scheduler to the owner's history. So `web/src/reviews/fsrs.ts` implements the published FSRS-4.5 formulas and default parameters in about a hundred lines: the forgetting curve, the first stability per rating, the next stability after a pass or a lapse, difficulty with mean reversion, and the interval for a 90% target retention (which makes the interval equal the stability). Intervals are capped at 365 days. The tests check the shape of the behavior, not magic numbers: 90% at `t = S`, growth on Good, less on Hard, shrinkage on Again, bounded difficulty, overdue reviews rewarded more than early ones.

**Cards are replayed from events** (ADR-0008), not stored: Learned counts as a first review rated Good, and each `review` event after it updates the card. `progressOf` now carries `reviews` and `card` per topic, and `stateOf` takes `now` and adds Relearning (last review Again), Fading (due) and Mastered (a Good review at least 7 days after Learned), in that order. A topic in any of those still unlocks what builds on it.

**Sessions on Today.** The page now reads progress once (`Plan`) and shows, in the spec's order: Reviews, Mistakes to revisit, Next up. A session (`ReviewSession`) asks two items from the review pool, at least one code or predict-the-output, choosing the ones answered longest ago so sessions rotate; it rates itself from each item's first attempt (Good, Hard, Again) and records one `review` event (item `review`, `data.rating` and `data.items`). `PracticeItem` gained `onGraded`, called for answers and Checks alike. The due list is fixed when it loads, so finishing a review doesn't make it vanish. Up to 20 a day, most forgotten first.

**History transport.** `fetchAttempts` now includes `review` events and their rating (`data->>rating`), so `Attempt` has an optional `rating`. A review with no rating is dropped rather than guessed.

**Docs:** the `review` event in the data model's events table, the reviews rules under Derived progress, F11 and F12 marked built, and a Milestone C checklist in the roadmap.

**Tests:** 11 for the scheduler, 9 for sessions and due lists, 5 for the new states, 6 on Today (including the Good, Hard and Again flows, and the saved event), 1 on the map, 1 on history. 308 web tests pass.

**Next:** interleaved practice (a recall item from an earlier topic in each ladder, F5), then Module 3 (loops).

## 2026-11-08: Module 2, Decisions and debugging, written

Five topics and a checkpoint, so Module 2 is ready before the owner finishes Module 1. This closes Milestone B.

**Resources.** Lecture 1 of CS50P (Conditionals, video `_b6NgY_pMdw`, embeddable by its oEmbed) carries the first three topics. Its section times came from CS50's published subtitles, used only to find the times: comparisons and the first `if` from 0:28 to 9:55; `elif` and `else` to 18:28; `or`, `and`, the grade program and chained comparisons to 34:07. The `match` section (48:18 to 55:37) is linked, not embedded, from if / elif / else. Tracing code's main resource is Python Tutor with a preloaded program; Reading errors' is Python's own tutorial chapter on errors, with Python Tutor stepping into a `NameError` as a second resource. Both lessons are the platform's own words, as ADR-0004 requires.

**What each topic drives at:**
- *Booleans and comparisons*: `=` against `==`, comparisons give a `bool`, and text is never equal to a number (`"7" == 7`). The debug plants `print(..., age = limit)`, which is a keyword argument and a `TypeError`, not a syntax error, so the learner meets the real message.
- *if / elif / else*: the first `True` condition wins; colons and indentation; two `if`s against one `if` / `elif`. The debug has an `elif` in the wrong order, a `==` where `=` was meant (so a name is never defined) and a print indented into a branch.
- *Logical operators*: `and`, `or`, `not`, and the `x == 1 or 2` trap, which the lecture doesn't cover and which shows up in the fill-in, the debug and the explain.
- *Tracing code*: trace tables. Several exercises run the learner's code with other starting values (`run_with`), so they can't be passed by typing the expected output in; the build is "a program from its trace" and its tests change the starting values.
- *Reading errors*: the last line first, then the line number; five error kinds; one change per run. The debug plants three errors of three kinds (`SyntaxError`, `NameError`, a `ValueError` from formatting text with `:.2f`), so each fix reveals the next.

**Checkpoint 2, ticket pricing:** age bands, a weekend extra that skips free tickets, a member discount applied after the extra, two decimal places. The hidden tests parse the output loosely and check one rule each, naming skills across Modules 1 and 2; four wrong solutions (the `or` trap, a boundary, the discount before the extra, no decimals) each fail exactly the test for that mistake. The debug is a parking-fee program with the `or` trap, a reversed `elif` order and a print indented into the `else`. The way through: a zoo-ticket sibling with labeled steps, the build in four fill-in steps, and two fresh versions, a swimming pool and a train fare, with the same rule shapes in different stories.

**Numbers:** 39 exercises and 26 recall items added; the validator runs 292 programs over the content, none failing; 275 web tests pass, including the follow-up invariants over every ready topic.

**Next:** Milestone C, starting with reviews (ADR-0009), and Module 3 (loops) before the owner finishes Module 2.

## 2026-11-08: Topic states, gating and "Prove it now"

The paused v1 work resumes, now that explanations can pass and topics can become Learned.

**Done (#43):**
- **States everywhere.** `stateOf` already existed; now every topic page and map row shows the learner's state with an icon and a word: Locked, Available, In progress, Learned on a date, or Passed for a checkpoint. `STATE_LABELS` in `progress.ts` holds the words, so no state is color alone (F9).
- **Gating (F8, ADR-0002).** A topic page loads the learner's history for the topic *and* its prerequisites, which is what the state depends on, in one `useTopicProgress` hook; the proof list reads from the same load instead of fetching again. A Locked topic shows its header and lesson only, with a notice naming the topics that open it; its practice and proof checks wait. A Locked checkpoint shows only what it brings together, not the checks or the way through. While the history loads, the page shows everything rather than flashing sections in and out; gating applies the moment the state is known.
- **"Prove it now"** appears on an Available topic that hasn't been started. It hides the lesson and practice, moves focus to the Prove it heading, and can be undone with "Show them anyway". Nothing is recorded for the choice itself; the checks record as they always did.
- **Signed-out visitors** see no states and no gating. Their progress can't be known, and nothing of theirs is saved anyway.
- **"Next up" on Today (F12):** `nextUp` picks the first topic in progress in track order, or else the first Available one that can be opened, skipping anything Locked, even if it was started before gating existed. Today reads the history a second time for it; sharing one load between the two sections is a small follow-up.
- **Tests:** 5 for `nextUp`, 6 for gating on topic pages, 2 more on the map, 4 on Today. The page tests needed a helper, `unlocked(topic)`, that supplies passing proof checks for a topic's real prerequisites, since a fake topic with an unlearned prerequisite is now Locked. 263 web tests pass.

**What the owner will see.** Gating is live for their account. Values and types, where they are, is Locked until Programs and print's three checks are passed, and Today now says "Continue: Programs and print". That's ADR-0002 working as written, but it's worth saying out loud.

**Next:** Module 2's content, so it's ready before the owner finishes Module 1. Then Stage 1 of the cloud track, starting with browser drills.

## 2026-11-08: Building starts: more than one track, and the cloud track on the map

**The owner said "Start building everything."** The order follows the spec's *Building it* section and the roadmap: the app learns to show more than one track; the cloud track goes on the map as outlines; then the paused v1 work resumes (topic states and gating with "Prove it now", Module 2); then Stage 1 of the cloud track, starting with drills that run in the browser; the lab checker once ADR-0014 is accepted.

**Done (#42):**
- **The app shows every track.** `tracks()`, `getTrack()`, `topicIdsOf()` and `placeOf()` replace `mainTrack()` and `moduleFor()` in `web/src/content/content.ts`; `placeOf` says which track and module a topic is in, and whether it's a topic, a checkpoint or a capstone. The map is at `/map` for the first track and `/map/<track id>` for the others, with a switcher, and a note when a track is all outlines. Topic pages name their track.
- **Tracks have an `order`, and a module may name a `capstone`**: a bigger checkpoint shown after the module's own, building on every module before it. That keeps the spec's module numbering intact on the map. The validator checks capstones like checkpoints and that no two tracks share an order.
- **`tools/outline_cloud_track.py`** reads the spec's module tables, checkpoint paragraphs and capstone sections and writes the track file and 357 `planned` outlines: 324 topics (the 7 specialties included), 30 checkpoints and 3 capstones. It overwrites only files that still carry its marker and are `planned`, so written topics are safe. The spec gained a "Checkpoint 30" line so Module 30 parses like the rest.
- **Gating between modules** comes from the spec's module map: a module's topics list the checkpoints of the modules it builds on as prerequisites, a checkpoint lists its module's topics, and a capstone lists the checkpoints that feed it. Python Foundations' Checkpoint 6 gates Module 6 (Automation). Within a module there's no order, as the spec says.
- **Checked:** the validator passes over 393 topics (6 ready, 387 planned); 37 Python tests, including one that runs the validator over generated content; 246 web tests.

**A cost to come back to.** Topic outlines are bundled with the app, so the main bundle grew from 612 KB to 806 KB (173 KB to 215 KB gzipped) for topics nobody can open yet. Loading a track's outlines on demand would undo that. Noted as a chore, not done now.

**Waiting on the owner:** accepting ADR-0014, before the lab checker is built.

## 2026-11-08: The map in docs/research; the track assumes nothing about the learner

**The owner said:** move the map into `docs/research`, don't assume they're strong in any area, the track may one day serve absolute beginners, and don't worry about the L1, L2, L3 depth levels.

**Done:**
- The map is at `docs/research/senior-cloud-architect-knowledge-map.md`, renamed to the folder's style and otherwise unchanged. It's the owner's own document, committed at their request.
- **The spec no longer builds on anyone's standing.** Removed: the depth-level system (the L1–L3 tables, the default depth by module, proofs scaling with depth, the primary-cloud option), every "at the aware level" phrasing, the owner's strengths and gaps from the faster path, and the depth paragraph in ADR-0014. The faster path is now an *example* route for someone who starts on Azure, and the spec says plainly that what a learner skips is decided by "prove it now" and the placement test, never by their own estimate. Two of the map's four rules stay: every concept gets a build, and write as you go.
- **A correction to the entry below.** It recorded the owner's strengths and gaps from the map as the basis for the faster path. The owner asked not to assume strengths anywhere, so the spec doesn't, and neither should future sessions. The map still says what it says, as the owner's own document.
- Memory updated the same way.

**Checked:** every topic ID and heading from before this change is still present, no IDs are duplicated, and every relative link resolves.

## 2026-11-08: The cloud track, cross-referenced with the owner's knowledge map

**The owner asked** to cross-reference the Cloud Solutions Architect spec against their own *Senior Cloud Architect Knowledge Map & Learning Roadmap*, a Markdown file with twelve domains, a certification order, a 24-month plan and a 24-item self-assessment: add everything the map has that the spec lacks, remove nothing, keep it extensive.

**Finding the file took two tries.** It wasn't in the project folder at first; the owner had it in another folder and copied it to the project root. It isn't committed, because it holds the owner's career details. Where it lives is the owner's call; `docs/research/` is the natural home if it goes in.

**Done, in `docs/specs/cloud-solutions-architect.md`:**
- **4 new modules:** Virtualization, hardware and Windows (2); Software engineering literacy (7); Application architecture and integration (17); Specialized workloads (28). The track has 30 modules now.
- **107 new topics,** from 210 to 317, and many existing "You'll be able to" lines extended with the map's specifics: CUBIC and BBR, SCIM and PKCE, the confused deputy, CRDTs, Paxos and Raft, KEDA, Kyverno, FOCUS, provisioned throughput, and so on. Every existing topic is still there.
- **New sections from the map:**
  - *Depth levels*: L1 aware, L2 working, L3 deep; how the four proofs scale with depth; a default depth for each module; the primary-cloud option; the map's four rules of thumb.
  - *A faster path for an experienced learner*: the map's seven phases over 24 months, mapped to modules, with its capstone builds, milestones, weekly rhythm (60% building, 25% reading, 15% writing), kill criteria and reading list.
  - *Self-assessment*: the map's 24 "you're senior when you can" items, each tied to the checkpoint, topic or drill that proves it. Kept as a mirror: the platform never counts self-report (ADR-0002).
- **Certifications:** AZ-104, CCSP, TOGAF, Databricks and Snowflake, exam codes, and the map's suggested order.
- **The service table:** 20 more rows, such as customer identity, subnet scope, IPAM, layer 4 and layer 7 load balancers, appliance insertion, zero trust access, Arm chips, PaaS hosting, block and file storage, shipped devices, Oracle, confidential computing, AI accelerators and carbon data.
- **6 more drills,** including Kubernetes triage, a threat model and a decision record.
- ADR-0014 gained a line on proofs scaling with depth. The roadmap and CHANGELOG carry the new counts.

**Numbering shifted.** Modules were inserted, so module numbers and the positional checkpoint IDs (`csa.mN.checkpoint`) moved. Nothing is built, so nothing refers to them yet. Stable IDs are now an open question in the spec.

**Checked by script, not by eye:** all 244 IDs from the previous version are present; no duplicate IDs; all 47 previous headings are present; every checkpoint ID matches its module number; every relative link resolves; and a sweep of 660 distinctive terms from the map found all of them in the spec (four were missing on the first pass and were added).

**Personal context from the map,** kept out of the repo's text beyond what the faster path needs: the owner's strengths are Linux, networking and Azure, and their stated gaps are AWS, Kubernetes and platforms, data and streaming, FinOps, and the business layer. The faster path is built on that.

**Next:** the owner decides on ADR-0014 and on when the track gets built. The v1 work stays paused where the earlier entry left it.

## 2026-11-08: A second track, Cloud Solutions Architect (specified)

**The owner asked for** a Cloud Solutions Architect track:
- with everything a senior architect needs at the top of the pay band;
- multi-cloud;
- able to drill skills until competency is proven, not just knowledge;
- assuming access to every cloud environment for practice.

**Done:**
- **The spec,** [docs/specs/cloud-solutions-architect.md](specs/cloud-solutions-architect.md). It has 26 modules in 4 stages, about 210 topics, 3 capstones and 6 specialties to choose from. It also covers:
  - how competency is proven, with drills that have targets;
  - lab safety and cost;
  - one topic written out in full;
  - a map to certifications;
  - a table of equivalent services on the three clouds.
- **ADR-0014, proposed:** how cloud skills are proven.
  - A local, read-only lab checker inspects what the learner built in their own sandbox. The platform receives only which checks passed.
  - CI tests the checks against recorded API responses, so ADR-0004 still holds without touching a cloud.
- **Links:** the roadmap, the vision, CLAUDE.md and the ADR index now point to the spec and the ADR.
- **Checked by web search:** current product names.
  - Azure AI Foundry is now Microsoft Foundry.
  - AWS Interconnect – multicloud gives a managed private link to Google Cloud.
  - Google's framework is now the Well-Architected Framework, with six pillars.

**Deliberately not done:** the track isn't in `content/` yet. The app shows only the first track file it finds (`mainTrack()`), and `cloud-…` sorts before `python-foundations`. Adding the track would replace the owner's Python map on the live site, so support for more than one track has to come first.

**Waiting on the owner:**
- accepting or changing ADR-0014;
- deciding when the track gets built, relative to the rest of v1 and the ML path.

The v1 work stays paused where the entry below left it.

## 2026-11-08: Where we stopped (paused)

The owner paused work here.

**Done since the last pause** (all merged and live):
- ADR-0013 was accepted, and the owner's answers recorded (#33).
- Explanation grading, built and rolled out:
  - the AI proxy and its call log, `ai_calls` (#34);
  - the explanation box on every topic and checkpoint (#35);
  - the grading test set. Claude Haiku 5.5 at low effort got all 30 samples right twice, so it's the grader (#36);
  - the rollout notes, and how to deploy the function again (#37).

**Where we sit**
- **Phase 1, Milestone B (Prove it).** Milestone A is done.
  - Done in B: export my data, progress tracking part 1, and explain it back graded by AI.
  - Left in B: topic states and gating with "Prove it now", and Module 2's content.
- **The live site has everything on `main`.**
  - The `ai` function is deployed, and the Claude API key is in the live project's secrets.
  - The owner switched on `allowed` for their account, so their explanations get graded.
  - The app stops grading at $10 a month.
- **The owner is on Module 1, Values and types.** Their next explain check there will be the first real grading.
- **Nothing is left running.** The local Supabase and Docker Desktop are stopped. `main` is clean, with no open pull requests or leftover branches.

**Not confirmed yet**
- **The first grading on the live site.** If the box says grading isn't switched on for the account, the `allowed` update didn't run. The SQL is in `setup.md`, under "Who can use it".
- **The $10 monthly limit in the Anthropic Console** (step 2 in `setup.md`). It's a second safety net, on top of the app's own cap.

**Next, in order**
1. **The owner:** try Explain it back on Values and types on the live site, reloading the page first. Set the Console limit, if it isn't set.
2. **Topic states and gating, with "Prove it now"** (F8, F9). This was waiting for grading. Explanations can now pass, so topics can become Learned. It starts with a short plan, checked against ADR-0002 and the v1 spec:
   - which states lock what;
   - what "Prove it now" lets a learner skip.
3. **Module 2's content,** ready before the owner finishes Module 1.
4. **Then Milestone C** (FSRS reviews, the full Today page, recall items, interleaved practice) **and D** (the hint-only tutor, problem reports).
5. **Later, in Phase 2:** the practice-hours tracker, on the way to 10,000 hours.

**To remember on return**
- **Merging doesn't deploy the AI proxy.** See "Putting it live" in `supabase/README.md`.
- **From Claude Code, the Supabase CLI changes the live project only with `--yes`.** That flag goes in only after the owner's go-ahead.
- **Checking the app on my own dev server:** the recipe is in the 2026-11-06 "Where we stopped" entry.
  - Local grading also needs `npm run fn:serve`, with the key in `supabase/functions/.env`.
  - The local test account is `allowed` in the local database only.

## 2026-11-08: Explain it back is live

**Rolled out** in this order (ADR-0013's last steps), with the owner's go-ahead:
1. **The Claude API key went into the live project's secrets.**
   - The owner's first try changed nothing. The Supabase CLI saw it was running inside Claude Code, and from there it won't change the live project without `--yes`.
   - The owner had typed that command, so Claude re-ran it with `--yes`. It first checked that the file held only `ANTHROPIC_API_KEY`, without showing any values.
2. **The owner switched on `allowed` for their account,** in the dashboard's SQL editor.
3. **The `ai_calls` migration went to the live database.** The dry run listed only that one.
4. **The `ai` function was deployed** (2.5 MB). Three requests checked it without calling Claude or writing anything:
   - the browser's preflight got 204;
   - a GET got 405;
   - a POST from someone not signed in got 401.
5. **The explanation box (#35) was merged,** and Cloudflare deployed it. The live site's code now has "Check my explanation".

**Merging doesn't deploy the function.** Cloudflare deploys the web app on every merge, but a change to `supabase/functions/` reaches the live project only through `npx supabase functions deploy ai`. The steps are now in `supabase/README.md`. Deploying from CI would need a Supabase access token in GitHub's secrets. That can wait until function changes are frequent.

**Cleaned up:** the local function server, the local Supabase and Docker Desktop are all stopped.

**Next:**
- The owner's first real grading: the explain check on Values and types, the topic they're on.
- Milestone B: topic states and gating, and "Prove it now" (F8, F9).
- Module 2's content, ready before the owner finishes Module 1.

## 2026-11-08: The grader chosen, and checked end to end

**The test set** (the owner approved up to about $1.20):
- Claude Haiku 5.5 at low effort got all 30 samples right, for $0.0056.
- A second run, to check it wasn't luck, got all 30 right again, for $0.0054.
- So Haiku is the grader, as ADR-0013 says (the cheapest that passes). It's already the proxy's default, and Sonnet and Opus never ran. About 1 cent spent in all.

**Real costs are lower than the ADR's estimate.** A grading used about 1,100 tokens in and 100 out, about $0.00017. At low effort Haiku barely thinks. ADR-0013 assumed 1,000 out, so $10 a month covers about 60,000 gradings, not 15,000.

**Checked end to end** in a real browser, on the local Supabase with the owner's key, as the local test account on Values and types:
- an explanation without the fix got Needs work. Its one question, "What do you need to do to the text values before the + sign can add them as numbers?", points at the gap without giving the answer;
- the full explanation got Passed, and "Your proof so far" changed to "✓ Explain: passed on Nov 8" with no reload;
- the local database had both calls in `ai_calls` with their costs, and both `explain_submit` events, correct false then true, each linked to its call.

**Getting the key in place:** the first check found `supabase/functions/.env` empty, because the editor hadn't saved yet. The check names the file's lines and their lengths, never their values.

**Next: rollout to the live project** (ADR-0013's last steps):
1. The owner puts the key in the live project's secrets, and switches on `allowed` for their account.
2. With the owner's go-ahead: apply the `ai_calls` migration (`db push --remote`), deploy the function (`functions deploy ai`), then merge the explanation box (#35).
3. The owner tries it on the live site.

## 2026-11-08: The explanation box (part 2) and the grading test set (part 3)

**Done**

- **The explanation box** (draft PR #35):
  - a text box and "Check my explanation" in each explain card;
  - the result: Passed, or Needs work with guiding questions, or a plain message when it wasn't graded;
  - every attempt saved as an `explain_submit` event (item `explain`, context `prove`), with `correct` set only when graded;
  - the history now reads graded explanations, so a pass counts toward progress straight away;
  - 13 new tests, 242 in all.

  It stays a draft until the proxy is deployed to the live project. Merged before then, every Check on the live site would fail.
- **The test set** (`supabase/functions/ai/test-set/`), 5 samples for each of Module 1's six explain checks. They were written to be clear-cut:
  - the short passes still state every required idea;
  - the misses lack a required idea outright, or get it wrong.

  `npm run fn:eval -- <model> <effort>` runs them with the proxy's own request, and a Deno test checks the files are usable.

**Decided while building**

- **The test set runs straight against Claude,** from a Deno script that uses `grading.ts`, not a Python script posting to the locally served function as ADR-0013 sketched. That avoids rewriting the prompt in Python, and minting a local sign-in for the script. What's being tested, the instructions and the reading of Claude's answer, is the same code. The proxy's checks and logging have their own tests.

**Waiting on the owner**

- The API key in `supabase/functions/.env`, from `.env.example`. Then approval to run the test set: about $1.20 for all three models.

## 2026-11-08: The AI proxy (ADR-0013, part 1)

**Done**

- **`ai_calls`** (migration `20261108223826_ai_calls.sql`):
  - append-only, like `events`, with the same deliberate-account-deletion exception;
  - learners can read their own rows, and only the service role can write;
  - `ai_spend_this_month()` sums this calendar month's costs in UTC, and only the service role may call it;
  - 11 pgTAP tests.
- **The Edge Function `supabase/functions/ai/`**, split so the logic is testable:
  - `handler.ts`: the checks in ADR-0013's order, with the services passed in;
  - `grading.ts`: the instructions, the request and reading the answer;
  - `cost.ts`: the price table;
  - `index.ts`: connects the real Supabase and Claude.
- **19 Deno tests** with fakes:
  - every outcome: graded, not allowed, paused, unavailable;
  - a stranger gets a 401 before anything else runs;
  - a failed call costs nothing to log, but an unusable answer is still logged with its cost;
  - the model-answer filter;
  - the CORS check.
- **Deno 2.9.6** is pinned in the root `package.json` from npm, so neither the owner nor CI installs anything by hand. A new **Edge Functions** CI job runs `npm run fn:test`.

**Decided while building**

- **Claude returns only the rubric results and the questions; the code works out the verdict.** A pass needs every required item met, so Claude can't "pass" an explanation the rubric doesn't support.
- **Structured output uses a plain JSON schema,** with the rubric IDs as an enum, rather than the SDK's Zod helper: one library fewer.
- **`verify_jwt = false` for this function.** It checks the sign-in itself, with `auth.getUser`, which works with every kind of signing key.
- **The log keeps the topic, the explanation and the prompt version,** not the rubric or the model answer: those can be found from the topic.
- Deno found the root `package.json` and wanted the function's packages in `node_modules`. `--node-modules-dir=none` makes it use its own cache, as Supabase's runtime does.

**Checked**

- On the local Supabase, through the real runtime:
  - the CORS check answered;
  - no sign-in gave 401;
  - the local test account got "not allowed", then "unavailable" once allowed (no key yet), which also ran the spending check;
  - a malformed request got a 400 with a reason.
- The local test account is now `allowed` in the local database only, for building the explanation box.
- The first database test assumed an empty `profiles` table, which a local database with accounts never has. It now looks at its own two learners.

**Next**

- The explanation box on topic and checkpoint pages: `explain_submit` events, and progress counting a pass.
- Then the 30-sample test set, which needs the owner's API key.

## 2026-11-08: The owner's answers

- **ADR-0013 accepted** as proposed, so explanation grading is next.
- **Anthropic Console:** the owner has an account. Still to confirm before grading goes live: billing and the $10 monthly limit. The API key comes later, when we connect it.
- **Where the owner is:** Values and types, topic 2 of Module 1. Module 2's content isn't urgent yet, so the order holds: grading, then states and gating, then Module 2.
- **No spoiler-free notes needed:** the devlog and pull requests can describe exercises in full, as before.
- **The practice-hours tracker** (toward 10,000 hours) is already on the roadmap, in Phase 2. Every answer and Check already saves its duration, so practice done now will count once it's built.

**Next:** explanation grading, built to ADR-0013.

## 2026-11-06: Where we stopped (paused for the weekly usage limit)

The owner paused work until the usage limit resets on Sunday.

**State**

- `main` is clean and deployed, with everything from this session merged:
  - export my data (#29);
  - progress tracking, part 1 (#30);
  - ADR-0013, proposed (#31).
- Nothing is left running: the local Supabase and Docker Desktop are stopped, and my test dev servers stopped themselves.

**Next, in order**

1. **The owner:**
   - accept or change [ADR-0013](decisions/0013-explain-grading.md);
   - create the Anthropic account, with billing and a $10 monthly limit;
   - say how far they are in Module 1;
   - say whether notes about content should avoid spoilers.
2. **Explanation grading,** built to ADR-0013 once it's accepted. It needs Deno installed, and the key.
3. **Topic states, gating and "Prove it now"** (F8, F9).
4. **Module 2 content,** ready before the owner finishes Module 1.
5. **Then Milestone C** (reviews, the full Today page) **and D** (the tutor, problem reports).

**How I check the app on my own dev server** (the recipe CLAUDE.md points to). This script lives outside the repo. Run it with `node` as a background task; it serves `web/` on port 5180 and stops itself after 15 minutes:

```js
import { pathToFileURL } from 'node:url'
const web = 'C:/Users/arasm/Documents/Education Platform/web'
const { createServer } = await import(
  pathToFileURL(`${web}/node_modules/vite/dist/node/index.js`).href
)
const server = await createServer({ root: web, server: { port: 5180, strictPort: true } })
await server.listen()
setTimeout(async () => { await server.close(); process.exit(0) }, 15 * 60 * 1000)
```

- **Signing in on it:** the local test account is `test-learner@example.com`. Its sign-in link arrives in Mailpit; fetch it from `http://127.0.0.1:54324/api/v1/messages`.
- **Docker Desktop** is at `%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe`, and `docker desktop stop` quits it. If I start it, I quit it afterwards.

## 2026-11-06: Proposed: grading explanations (ADR-0013)

**Why:** explanation grading is the next item, and it's the first part of the platform that costs money and calls an outside service. So the design goes to the owner first.

**Done**

- [ADR-0013](decisions/0013-explain-grading.md), proposed:
  - the browser sends the explanation to an Edge Function, which checks sign-in, `allowed` and the month's spending, then asks Claude to grade it against the rubric;
  - a pass means every required rubric item is met; a miss gets up to 3 guiding questions, never the model answer;
  - an append-only `ai_calls` log carries the $10 monthly cap, with the Anthropic Console's own limit as a backstop;
  - the model is the cheapest of Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 that passes a 30-sample test set. Running that set once on all three costs about $1.20, and each run needs the owner's go-ahead.
- Checked first, on this PC: CLI 3.0 serves functions locally and deploys them to the live project. It sets secrets only on the live project, from a `.env` file or the dashboard. Deno isn't installed yet. Model names and prices come from the current Claude API reference (October 2026), not memory.

**Waiting on the owner**

- Accept or change ADR-0013.
- Create the Anthropic account, with billing and the $10 limit (setup guide).
- How far they are in Module 1, which decides when Module 2's content is needed. And whether notes about content should avoid spoilers.

## 2026-11-06: Progress tracking, part 1

**Decided: gating waits for explanation grading.** The plan had gating before grading. But a topic is Learned only once its build, debug and explain all pass, and explanations can't be graded yet. Gating now would lock the owner out of topics 2–5 partway through Module 1. So this part shows progress without locking anything. States, gating and "Prove it now" switch on with grading. Told to the owner; the roadmap's Milestone B list now says so.

**Done**

- `web/src/progress/progress.ts`, pure functions for the data model's rules:
  - `progressOf`: when each proof check first passed. A passing Check of the build (or of any fresh version, for a checkpoint) or the debug counts, as will an `explain_submit` event with `correct` true.
  - `stateOf`: Locked, Available, In progress, Learned, or a checkpoint's Passed.
  - 12 tests: one per state change, and that the order events arrive in doesn't change the result. That order-independence is the data model's "incremental equals rebuilt from scratch".
- `useProgress`: reads the history once, adds the events on this device, and recalculates after each one. It remembers whose history it read, so after switching accounts it never shows the previous learner's.
- **The map** marks started topics "In progress", with the proof checks passed there.
- **Topic and checkpoint pages:** "Your proof so far" lists the three checks, passed (with the date) or not yet. The Prove it intro no longer calls them extra practice.
- Docs: the data model's progress section, F8 and F9, the roadmap, and the web README.
- Tests: 20 new, 229 web tests in all.

**Checked end to end** on the local Supabase, as the local test account:
- the map showed "In progress" only on Programs and print, ignoring answers on a sample topic that no longer exists;
- on that topic, the banner build typed into the editor passed its hidden tests in real Pyodide, and "Your proof so far" changed to "✓ Build: passed on Nov 6" with no reload;
- the map then showed "In progress · Proof checks passed: build", and the Check was in the local database.

**Next**

- Explain it back, graded by AI (F7, F14): the AI proxy, its budget cap and the grading. It needs the owner's Anthropic API key. Then states and gating.
- Module 2 content, timed to the owner's progress through Module 1.

## 2026-11-06: Export my data (F16, built early)

**Why now:** the learning history exists only in the Supabase project, and ADR-0010's backup plan is this export, which didn't exist yet. The owner chose to build it first, then carry on with Milestone B.

**Decided**

- **Where:** a new account page, which opens from the learner's name in the header.
- **What's in the file:** the profile and every event, with every column, oldest first. It's indented JSON, named after the app and the local date. A `format` number lets the capstone's scripts tell layouts apart. Progress joins once Milestone B computes it.
- **The outbox too, read before the server.** The owner's answer to an explain-it-back question shaped this: they expected an unsaved answer to be in the file. A server-only export would have missed it.
  - Reading the outbox first means an event sent in between is on the server by then, and one sent later is in the copy of the outbox.
  - Events only in the outbox have `received_at: null`, and the page says how many there were.
  - The event log's new `getPendingRows()` reads the outbox fresh, so other tabs' unsent events count too.
- **Reading pages until an empty one,** not until a short one. Otherwise a server row limit below 1,000 would silently cut the file short. It costs one extra request.

**Done**

- `web/src/export/`: `exportData.ts` gathers the data, and `download.ts` saves it through the browser's normal download. The file never leaves the browser.
- `pages/AccountPage.tsx` at `/account`, with "Download my data" and a message saying how many events the file holds.
- `web/src/days.ts`: `dayOf` and `addDays` moved out of the follow-up rules. Importing `dayOf` from there had pulled 3.7 kB of those rules into the startup bundle.
- Docs: the file's layout in the data model, a weekly backup routine in the setup guide, and F16 and the roadmap.
- Tests: 15 new, 209 web tests in all.

**Checked end to end** against the local Supabase, on a dev server that stopped itself, signed in as the local test account:
- With the API container stopped, the page said the data couldn't be downloaded. On this PC a refused local connection takes a few seconds to fail, so "Gathering your data…" showed until then.
- With one made-up event placed straight in the outbox, the file had 7 events: the made-up one with `received_at: null`, every column, oldest first, no duplicates. The page said 1 wasn't saved yet. The event was then removed from the outbox, and it never reached the local database.
- A real download landed in Downloads and read back as valid JSON. I deleted it afterwards.

**Next**

- Progress tracking: each topic's state, worked out from the event log and shown on the map.

## 2026-11-06: Checkpoint 1, the receipt calculator

**Done**

- `content/topics/py.m1.checkpoint`, status `ready`. That completes Module 1's content.
  - **Build:** a restaurant receipt from a blank editor: meal and drinks (decimals allowed), a whole-number tip percentage, then the subtotal, tip and total to two decimal places.
  - **Debug:** cinema tickets with three bugs, one per test:
    - an unconverted `input()` (a `TypeError` crash);
    - `adults + children / 2 * price`, missing its parentheses (a wrong total);
    - `print("Total: $", total)`, which adds a space and has no two decimals.
  - **Explain:** walk through a three-line tip calculator, naming the type of every value, and say what goes wrong without `float()`.
  - **The way through:**
    - a solved sibling, a shop receipt with a discount, with labeled steps (it introduces `#` comments as a plan);
    - the receipt in 4 fill-in steps with hints, each giving the whole program but one part, the last only the three comments;
    - 2 fresh versions: splitting a bill, and an electricity bill.
- **Tests that point at the right skill.** The first draft compared exact amounts, so a single precedence slip also failed the decimals test. Now:
  - value tests read the numbers whatever their format, and check them against the program's own earlier lines;
  - inputs with decimals appear only in the test that reads them;
  - one test checks two decimal places, and one the layout with every number replaced.
  - Each of 14 single-mistake wrong answers now fails exactly the one test for its mistake (checked with `harness/cli.py check`).
- **Found by viewing the page:**
  - On an empty program, three hidden tests crashed with `KeyError: 'Subtotal'` from the test's own helper, and the page showed it. The page shows crashes even in hidden tests, because they're usually in the learner's code. The tests now fail with an `assert` instead, and the content checker runs every hidden-test exercise on an empty program to catch this. All earlier topics pass.
  - The suggestion scrolled the steps' heading only to the bottom of the screen, because the steps weren't drawn yet. It now draws them first (`flushSync`), then scrolls.
- **Checked:**
  - the content checker (147 programs);
  - the guarantee test, now over a real checkpoint: every one of its tests brings back a question on each skill it names;
  - on the dev server, signed out: two failing Checks on the build bring up the suggestion, which opens the steps with the first fresh version.

**Next**

- Milestone A's checklist is complete. Next is the owner's call: Milestone B (progress tracking, gating, explain grading), or the owner's own pass through Module 1 first.

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
