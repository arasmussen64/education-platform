# ADR-0022: Step through, a visualizer from Python's own trace hook

- **Status:** Accepted (the owner asked for Phase 2 to be built on 2026-11-09; this is its visualizer item)
- **Date:** 2026-11-09

## Context

- Reading and tracing code is a skill of its own, and novices who can't trace can't debug (Lister et al., 2004). Learners build a "notional machine", a mental model of what each line does to the variables, and most of their early confusion is a wrong one (du Boulay, 1986; [learning-science.md](../learning-science.md)).
- v1 pointed at Python Tutor for this and listed a built-in visualizer as out of scope. The roadmap's Phase 2 brings it in.
- The platform already runs every learner program through one small harness, in the browser (Pyodide) and in CI (CPython), and both must agree ([harness/README.md](../../harness/README.md)). Python's `sys.settrace` hook can watch that same run line by line.
- Predict-the-output questions are where tracing is practised most. After a wrong prediction, "why?" is the moment to show the machine's view.

## Decision

1. **A recorder in the harness.** `harness/tracer.py` runs the program exactly as the Run button does (same input handling, random seed and error trimming), under `sys.settrace`, and records a step for each line about to run, each call, each return and each error. A step holds the running calls (the program first, the innermost last), each with its variables as short text, and how much output had been printed by then. Only the learner's own frames are recorded.
2. **Limits that keep it small.** 300 steps at most; past that the program keeps running unrecorded, up to the usual time limit, and the result says so. Values are cut at 60 characters; functions, classes and modules show as "function f", "class C", and modules aren't listed. A long run that never reaches a new line is stopped by the existing time limit, like any run.
3. **The same contract in both runtimes.** `trace` is a third kind of scenario (an empty `trace.txt` marks the folder): CPython and Pyodide must produce the same `expected.json`, step for step.
4. **One player, three places.** `StepThrough` shows the code with the current line marked, each running call's variables (innermost first), the output so far, and First/Back/Next/Last with a slider. It appears under a **Step through** button beside Run in every code runner (exercises, worked examples, the playground), and as **Step through it** under a predict-the-output question _after_ it's answered, never before: predicting first is the point. The placement test's quiet questions don't offer it.
5. **Step through reuses the last Run's input and seed,** so it plays back what the learner just saw; a program that asks for input it wasn't given says to Run first and answer.
6. **It's a run in the log.** A Step through is saved as a `code_run` event with `stepped: true` and the number of steps, so the record of what the learner did stays whole without a new event type.

## Alternatives considered

- **Embedding Python Tutor.** Excellent, but an iframe to a third party: its own Python, no access to the learner's input or seed, and nothing we can test or fit later.
- **A separate interpreter in JavaScript** (Skulpt-style) for visualization only. Two Pythons that could disagree, which is exactly what the harness contract exists to prevent.
- **Recording every step with no cap.** A loop of a thousand iterations would produce megabytes and freeze the page; 300 steps shows the shape of any short program, and Run is still there for the whole output.
- **Showing the visualizer before a prediction is made.** It would turn retrieval practice into watching.

## Consequences

- The harness gains a file, a `trace` command in `cli.py` and two scenarios; `harness/README.md` describes them. Pyodide's `sys.settrace` behaves as CPython's, which the scenario test proves on every pull request.
- The worker protocol gains a `trace` request and reply; the runner gains `trace()`; the test fakes gain `traced()`.
- The event `code_run` gains `stepped`, `steps` and `truncated` in its data when it came from Step through ([data model](../specs/data-model.md)).
- Recording adds overhead to a run: a few milliseconds a step, which no short program notices. A learner can always just press Run.
- Later work can build on the recorded steps: "predict the next value" questions, or highlighting the step where a learner's prediction diverged.
