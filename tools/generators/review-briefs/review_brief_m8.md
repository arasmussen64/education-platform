# Cold review brief: Module 8 of the ML track, "Neural networks from scratch"

You are a cold reviewer of learning content. You have not seen this material before and you must read it as its first learner would: an adult beginner coder with no assumed strengths in any area, who reads every topic in order. Your job is to find what is wrong, unclear, inconsistent, or unkind to a beginner, and to report it precisely. **Do not edit any file, and do not run git commands that change anything** (no checkout, no stash, no commit). Report only.

## What to read

The repository is the folder you were started in (`<repo root>`). The working tree is on the branch that holds the whole module; read the files as they are. The module is eight topic folders under `content/topics/`:

- `ml.nn.neurons-and-layers`
- `ml.nn.backward-layers`
- `ml.nn.initialization-and-activations`
- `ml.nn.training-loop`
- `ml.nn.regularization`
- `ml.nn.convolution`
- `ml.nn.debugging-training`
- `ml.m8.checkpoint`

In each folder read, in this order: `topic.yaml` (summary, objectives, resources, the explain prompt, rubric and model answer, skills), `lesson.mdx` (intro and recap; the checkpoint has none), every file under `recall/` (predict, MCQ and Parsons items), and every `exercises/*/exercise.yaml` with its `solution.py`, `starter.py` (if any), `test_exercise.py` and the `wrong/` folder. The spec section for the module is `docs/specs/ml-foundations.md`, heading "Module 8"; the track file is `content/tracks/ml-foundations.yaml`. What the learner is assumed to know before this module is Modules 1 to 7 of the same track (`docs/specs/ml-foundations.md`), in particular Module 4's two-layer network and gradient descent; the module must not assume anything from outside the track.

## What to check

1. **Numbers and claims against the code.** Every number in prose (lessons, notes, explanations, prompts) must match what the code actually prints. Run programs yourself with `python -m uv run python <file>` from the repository root (uv is installed; NumPy is available; a training run takes seconds) whenever you doubt a number. Flag any prose number that the output doesn't support, any arithmetic that doesn't add up (parameter counts, output sizes, steps per epoch, the sums in a predict item's explanation), and any factual claim about backpropagation, initialization, optimizers, regularization, convolutions or NumPy that you believe is wrong. Be specific about why.
2. **Internal consistency.** A topic's summary, objectives, lesson, recap, recall items, exercises and skills must agree with each other and with the spec's table for the topic. Prompts must describe what the tests actually check. Hints must be true. Known-wrong solutions must really exhibit the mistake their file name says. Explanations of MCQs must not contradict the lesson. The same class (`Dense`, `Sequential`, `fit`, `Adam`...) appears in several topics with additions as the module goes on; flag any place where a later topic's prose describes an earlier version, or where a method's signature or behaviour silently changes without the lesson saying so.
3. **MCQ quality.** For every multiple-choice item: the correct answer must not be the longest choice; the distractors must be plausible and not trivially wrong; the explanation must say why the right answer is right and why the others aren't.
4. **Predict and Parsons items.** The expected output must follow from the code with nothing hidden; the explanation must account for every line. A Parsons must have exactly one correct order; flag any pair of lines that could be swapped and still work.
5. **Resources.** For every resource in a `topic.yaml`, fetch the page (`curl -sL -A "Mozilla/5.0" <url> | grep -o "<title>[^<]*</title>"` works, and for section names grep the page for the heading text) and confirm: the title matches, the URL resolves, any chapter, section or timestamp named in the title exists, and the licence stated is the licence the page states. Report mismatches with what the page actually says.
6. **Beginner readability.** Every piece of jargon must be defined the first time it is used in the module (if a later topic re-introduces a term without a gloss, say so when a beginner would stumble). Sentences that need two readings, references to "the last topic" where the topic should be named, number lists without commas, and anything that assumes the learner already knows deep learning, PyTorch or statistics beyond Module 5 are findings.
7. **YAML and formatting.** A doubled apostrophe (`''`) inside a `|` block scalar renders literally and is a bug; backticks must pair; code fences must close; the `lines:` ranges in worked examples must point at the lines the note describes (open the `solution.py` and count).
8. **Browser constraints.** The learner's Python runs in the browser (Pyodide, 32-bit, NumPy present, coarse clock). Flag any pinned output that could differ there: object sizes, default integer dtypes (`np.arange` without a dtype is int32 there), timing values compared exactly, random values from `default_rng` printed to many digits after long computations, and anything that would take more than about a minute to run.
9. **The checkpoint.** Its build prompt must list exactly what the hidden tests need; its steps must each be solvable from their prompt and hints; its debug prompt's three symptoms must be what the starter actually prints (run `starter.py`); its explain rubric must be answerable from the module alone.

## How to report

Write a numbered list of findings, most serious first. For each finding give: the file path (relative to the repository), the exact text or line, what is wrong, and the fix you propose (the corrected text where it is short). Group trivial style points at the end. If something is right but you had to work to confirm it, do not report it. Aim for completeness over brevity: a long list of true findings is what is wanted; an empty list is not credible for this much material. Do not report the absence of problems topic by topic. End with a one-paragraph overall judgement of the module for a beginner.
