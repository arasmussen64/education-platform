"""Writes ml.m5.checkpoint, "Checkpoint 5: is the model better?", which closes
the ML track's Module 5. Run from the repository root under uv (python -m uv
run python <this file>), so every program's expected output is captured from
CPython rather than typed in. Files are written as bytes with LF endings."""

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.m5.checkpoint")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, check=True
    )
    return result.stdout.replace("\r\n", "\n")


def block(text: str, indent: str = "  ") -> str:
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


# --- the pieces -------------------------------------------------------------------------

FUNCTIONS = '''def confusion(y, pred):
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    return tp, fp, fn, tn


def metrics(tp, fp, fn, tn):
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)
    return accuracy, precision, recall, f1


def accuracy_interval(correct, z=1.96):
    p = correct.mean()
    se = np.sqrt(p * (1 - p) / len(correct))
    return float(p - z * se), float(p + z * se)


def paired_bootstrap(rng, correct_a, correct_b, draws=2000):
    diff = correct_a - correct_b
    means = np.array([rng.choice(diff, size=len(diff)).mean() for _ in range(draws)])
    low, high = np.percentile(means, [2.5, 97.5])
    return float(diff.mean()), float(low), float(high)


def choose_threshold(y_val, score_val):
    thresholds = np.arange(0.0, 2.01, 0.05)
    accuracies = [((score_val > t).astype(int) == y_val).mean() for t in thresholds]
    return float(round(thresholds[int(np.argmax(accuracies))], 2))


def report(rng, y, score_a, score_b, threshold_a, threshold_b):
    pred_a = (score_a > threshold_a).astype(int)
    pred_b = (score_b > threshold_b).astype(int)
    for name, pred in (("A", pred_a), ("B", pred_b)):
        counts = confusion(y, pred)
        print(name, counts, np.round(metrics(*counts), 3))
    correct_a = (pred_a == y).astype(int)
    correct_b = (pred_b == y).astype(int)
    print("interval A", np.round(accuracy_interval(correct_a), 3))
    print("interval B", np.round(accuracy_interval(correct_b), 3))
    mean, low, high = paired_bootstrap(rng, correct_a, correct_b)
    print("A minus B", round(mean, 3), np.round([low, high], 3))
    if low > 0:
        print("verdict: A is better")
    elif high < 0:
        print("verdict: B is better")
    else:
        print("verdict: not established")
'''


def data_block(seed, sep_a, sep_b):
    return f'''rng = np.random.default_rng({seed})
n = 200
y = (rng.random(n) < 0.3).astype(int)
score_a = y * {sep_a} + rng.normal(0, 1, size=n)
score_b = y * {sep_b} + rng.normal(0, 1, size=n)
y_val = (rng.random(n) < 0.3).astype(int)
score_a_val = y_val * {sep_a} + rng.normal(0, 1, size=n)
score_b_val = y_val * {sep_b} + rng.normal(0, 1, size=n)
'''


CALL = '''threshold_a = choose_threshold(y_val, score_a_val)
threshold_b = choose_threshold(y_val, score_b_val)
print("thresholds", threshold_a, threshold_b)
report(rng, y, score_a, score_b, threshold_a, threshold_b)
'''

DATASETS = {
    "main": (21, 2.0, 1.2),
    "close": (22, 1.5, 1.4),
    "reversed": (23, 1.3, 2.2),
}


def build_solution(key):
    seed, sep_a, sep_b = DATASETS[key]
    return "import numpy as np\n\n\n" + FUNCTIONS + "\n\n" + data_block(seed, sep_a, sep_b) + CALL


EXPECTED = {key: out(build_solution(key)) for key in DATASETS}
for key, text in EXPECTED.items():
    print(key + ":\n" + text)
    assert "e-" not in text and "nan" not in text, text
verdicts = {key: text.splitlines()[-1] for key, text in EXPECTED.items()}
assert verdicts["main"] == "verdict: A is better", verdicts
assert verdicts["close"] == "verdict: not established", verdicts
assert verdicts["reversed"] == "verdict: B is better", verdicts
for key in DATASETS:
    nudged = build_solution(key).replace("score_a = y * ", "score_a = 0.0000000001 + y * ")
    assert out(nudged) == EXPECTED[key], "a tenth-decimal nudge changed the output"
MAIN_EXPECTED = EXPECTED["main"]

WRONG = {
    "swapped": ("    precision = tp / (tp + fp)\n    recall = tp / (tp + fn)", "    precision = tp / (tp + fn)\n    recall = tp / (tp + fp)"),
    "no-root": ("    se = np.sqrt(p * (1 - p) / len(correct))", "    se = p * (1 - p) / len(correct)"),
    "unpaired": (
        "    means = np.array([rng.choice(diff, size=len(diff)).mean() for _ in range(draws)])",
        "    means = np.array([rng.choice(correct_a, size=len(diff)).mean() - rng.choice(correct_b, size=len(diff)).mean() for _ in range(draws)])",
    ),
}
for name, (old, new) in WRONG.items():
    assert old in build_solution("main"), name
    assert out(build_solution("main").replace(old, new)) != MAIN_EXPECTED, name

# --- the debug: three bugs -----------------------------------------------------------------

DEBUG_SOLUTION = build_solution("main")
BUG_LEAK = ("threshold_a = choose_threshold(y_val, score_a_val)\nthreshold_b = choose_threshold(y_val, score_b_val)", "threshold_a = choose_threshold(y, score_a)\nthreshold_b = choose_threshold(y, score_b)")
BUG_SWAP = WRONG["swapped"]
BUG_UNPAIRED = WRONG["unpaired"]
for old, new in (BUG_LEAK, BUG_SWAP, BUG_UNPAIRED):
    assert old in DEBUG_SOLUTION, old
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_LEAK).replace(*BUG_SWAP).replace(*BUG_UNPAIRED)
DEBUG_TWO_LEFT = DEBUG_SOLUTION.replace(*BUG_SWAP).replace(*BUG_UNPAIRED)
DEBUG_ONE_LEFT = DEBUG_SOLUTION.replace(*BUG_UNPAIRED)
for variant in (DEBUG_STARTER, DEBUG_TWO_LEFT, DEBUG_ONE_LEFT):
    assert out(variant) != MAIN_EXPECTED
print("buggy prints:\n" + out(DEBUG_STARTER))
print("two bugs left prints:\n" + out(DEBUG_TWO_LEFT))
print("one bug left prints:\n" + out(DEBUG_ONE_LEFT))
LEAKED_THRESHOLDS = out(DEBUG_STARTER).splitlines()[0]
HONEST_THRESHOLDS = MAIN_EXPECTED.splitlines()[0]
LEAKED_ACC_A = out(DEBUG_STARTER).splitlines()[1].split("[")[1].split()[0]
HONEST_ACC_A = MAIN_EXPECTED.splitlines()[1].split("[")[1].split()[0]
assert float(LEAKED_ACC_A) >= float(HONEST_ACC_A), (LEAKED_ACC_A, HONEST_ACC_A)
UNPAIRED_LINE = out(DEBUG_ONE_LEFT).splitlines()[-2]
PAIRED_LINE = MAIN_EXPECTED.splitlines()[-2]

# --- the solved sibling: one model against the baseline ------------------------------------------

EXAMPLE = "import numpy as np\n\n\n" + FUNCTIONS + "\n\n" + data_block(21, 2.0, 1.2) + '''
threshold = choose_threshold(y_val, score_a_val)
pred = (score_a > threshold).astype(int)
always_no = np.zeros(n, dtype=int)
tp, fp, fn, tn = confusion(y, pred)
print("model", (tp, fp, fn, tn), np.round(metrics(tp, fp, fn, tn), 3))
print("always no", confusion(y, always_no), round(float((always_no == y).mean()), 3))
correct = (pred == y).astype(int)
print("interval", np.round(accuracy_interval(correct), 3))
mean, low, high = paired_bootstrap(rng, correct, (always_no == y).astype(int))
print("model minus baseline", round(mean, 3), np.round([low, high], 3))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert EX[0].startswith("model (") and EX[1].startswith("always no (") and float(EX[3].split("[")[1].split()[0]) > 0, EXAMPLE_OUT
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text):
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if text in line)


# --- the steps ---------------------------------------------------------------------------------------

PRELUDE = "import numpy as np\n\n" + data_block(21, 2.0, 1.2) + "pred_a = (score_a > 1.0).astype(int)\npred_b = (score_b > 0.6).astype(int)\n\n\n"

STEP1_HEAD = PRELUDE + '''def confusion(y, pred):
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == ZERO)).sum())
    fn = int(((pred == ZERO) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    return tp, fp, fn, tn


print(confusion(y, pred_a))
print(confusion(y, pred_b))
print(sum(confusion(y, pred_a)))
'''
STEP1_SOLUTION = STEP1_HEAD.replace("ZERO", "0")
STEP1_STARTER = STEP1_HEAD.replace("ZERO", "...")
STEP1_OUT = out(STEP1_SOLUTION)
print("step 1:\n" + STEP1_OUT)
assert STEP1_OUT.splitlines()[2] == "200", STEP1_OUT

STEP2_HEAD = PRELUDE + '''def confusion(y, pred):
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    return tp, fp, fn, tn


def metrics(tp, fp, fn, tn):
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    precision = tp / (tp + FP)
    recall = tp / (tp + FN)
    f1 = 2 * precision * recall / (precision + recall)
    return accuracy, precision, recall, f1


print(np.round(metrics(*confusion(y, pred_a)), 3))
print(np.round(metrics(*confusion(y, pred_b)), 3))
'''
STEP2_SOLUTION = STEP2_HEAD.replace("(tp + FP)", "(tp + fp)").replace("(tp + FN)", "(tp + fn)")
STEP2_STARTER = STEP2_HEAD.replace("(tp + FP)", "(tp + ...)").replace("(tp + FN)", "(tp + ...)")
STEP2_OUT = out(STEP2_SOLUTION)
print("step 2:\n" + STEP2_OUT)

STEP3_HEAD = PRELUDE + '''def accuracy_interval(correct, z=1.96):
    p = correct.mean()
    se = np.sqrt(p * (1 - p) / LEN)
    return float(p - Z * se), float(p + Z * se)


correct_a = (pred_a == y).astype(int)
correct_b = (pred_b == y).astype(int)
print(round(float(correct_a.mean()), 3), np.round(accuracy_interval(correct_a), 3))
print(round(float(correct_b.mean()), 3), np.round(accuracy_interval(correct_b), 3))
'''
STEP3_SOLUTION = STEP3_HEAD.replace("/ LEN)", "/ len(correct))").replace("Z * se", "z * se")
STEP3_STARTER = STEP3_HEAD.replace("/ LEN)", "/ ...)").replace("Z * se", "... * se")
STEP3_OUT = out(STEP3_SOLUTION)
print("step 3:\n" + STEP3_OUT)

STEP4_HEAD = PRELUDE + '''def paired_bootstrap(rng, correct_a, correct_b, draws=2000):
    diff = correct_a - correct_b
    means = np.array([rng.choice(DIFF, size=len(diff)).mean() for _ in range(draws)])
    low, high = np.percentile(means, [2.5, PCT])
    return float(diff.mean()), float(low), float(high)


correct_a = (pred_a == y).astype(int)
correct_b = (pred_b == y).astype(int)
mean, low, high = paired_bootstrap(rng, correct_a, correct_b)
print(round(mean, 3), round(low, 3), round(high, 3))
print(low > 0)
'''
STEP4_SOLUTION = STEP4_HEAD.replace("rng.choice(DIFF,", "rng.choice(diff,").replace("[2.5, PCT]", "[2.5, 97.5]")
STEP4_STARTER = STEP4_HEAD.replace("rng.choice(DIFF,", "rng.choice(...,").replace("[2.5, PCT]", "[2.5, ...]")
STEP4_OUT = out(STEP4_SOLUTION)
print("step 4:\n" + STEP4_OUT)

# =====================================================================================
# the build and its fresh versions
# =====================================================================================

TEST_SKILLS = '''# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.prob.evaluating-models/metrics, ml.prob.evaluating-models/compare, ml.prob.evaluating-models/splits]
  test_confusion_and_metrics: [ml.prob.evaluating-models/metrics, ml.prob.bayes/conditional]
  test_accuracy_interval: [ml.prob.evaluating-models/interval, ml.prob.sampling-and-confidence/standard-error, ml.prob.sampling-and-confidence/clt]
  test_paired_bootstrap: [ml.prob.evaluating-models/compare, ml.prob.sampling-and-confidence/bootstrap]
  test_choose_threshold: [ml.prob.evaluating-models/splits]
  test_the_verdict: [ml.prob.evaluating-models/compare, ml.prob.sampling-and-confidence/interval]
'''


def build_tests(key):
    return f'''import numpy as np

from checks import function, printed, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the thresholds, both reports, both intervals, the paired comparison and the verdict."""
    assert run() == {EXPECTED[key]!r}


def test_confusion_and_metrics():
    """Hand-made labels give the four counts, and 8, 2, 4, 86 give accuracy 0.94, precision 0.8 and recall 2/3."""
    confusion = function("confusion")
    metrics = function("metrics")
    y = np.array([1, 1, 0, 0, 1, 0])
    pred = np.array([1, 0, 1, 0, 1, 0])
    assert confusion(y, pred) == (2, 1, 1, 2)
    accuracy, precision, recall, f1 = metrics(8, 2, 4, 86)
    assert abs(accuracy - 0.94) < 1e-12 and abs(precision - 0.8) < 1e-12 and abs(recall - 2 / 3) < 1e-12


def test_accuracy_interval():
    """An accuracy of 0.9 on 100 examples has the interval 0.841 to 0.959."""
    accuracy_interval = function("accuracy_interval")
    low, high = accuracy_interval(np.array([1] * 90 + [0] * 10))
    assert abs(low - 0.8412) < 0.001 and abs(high - 0.9588) < 0.001


def test_paired_bootstrap():
    """Two identical models differ by exactly zero with a zero-width interval; a strictly better one has a positive interval."""
    paired_bootstrap = function("paired_bootstrap")
    rng = np.random.default_rng(0)
    correct = (rng.random(100) < 0.8).astype(int)
    assert paired_bootstrap(rng, correct, correct) == (0.0, 0.0, 0.0)
    better = correct.copy()
    better[correct == 0] = 1
    mean, low, high = paired_bootstrap(rng, better, correct)
    assert abs(mean - (1 - correct.mean())) < 1e-12 and 0 < low <= mean <= high


def test_choose_threshold():
    """On validation scores that separate perfectly at 1, the chosen threshold lies between the classes."""
    choose_threshold = function("choose_threshold")
    y_val = np.array([0, 0, 0, 1, 1, 1])
    score_val = np.array([0.1, 0.5, 0.9, 1.1, 1.5, 1.9])
    assert 0.9 <= choose_threshold(y_val, score_val) < 1.1


def test_the_verdict():
    """Two identical models get 'not established', and a model that is right wherever the other is wrong gets 'A is better'."""
    report = function("report")
    rng = np.random.default_rng(1)
    y = (rng.random(100) < 0.5).astype(int)
    scores = y * 1.0 + rng.normal(0, 1, size=100)
    same = printed(report, np.random.default_rng(2), y, scores, scores, 0.5, 0.5)
    assert same.strip().endswith("verdict: not established"), same
    perfect = y * 10.0
    better = printed(report, np.random.default_rng(3), y, perfect, scores, 5.0, 0.5)
    assert better.strip().endswith("verdict: A is better"), better
'''


def write_build(folder, title, opening, key, what):
    seed, sep_a, sep_b = DATASETS[key]
    prompt = f'''  {opening}

  **The data.** Two hundred held-out examples, 30 percent positive, with each model's score for each; a second two hundred are the validation set. The scores stand in for two trained models (A's separate the classes by {sep_a}, B's by {sep_b}, both with noise of spread 1), drawn from a seeded generator:

  ```python
{block(data_block(seed, sep_a, sep_b))}  ```

  {what}

  **Write:**

  - `confusion(y, pred)`: the counts `(tp, fp, fn, tn)` as plain ints.
  - `metrics(tp, fp, fn, tn)`: accuracy, precision, recall and F1 as floats.
  - `accuracy_interval(correct, z=1.96)`: the 95 percent interval for an accuracy from an array of 1s and 0s, as a pair of floats.
  - `paired_bootstrap(rng, correct_a, correct_b, draws=2000)`: the mean per-example difference and the 2.5th and 97.5th percentiles of its mean over `draws` resamples of the **differences** with replacement, as three floats.
  - `choose_threshold(y_val, score_val)`: the threshold in `np.arange(0.0, 2.01, 0.05)` with the highest accuracy on the **validation** data (the first of any ties), as a float.
  - `report(rng, y, score_a, score_b, threshold_a, threshold_b)`: prints, for each model, its name, its confusion counts and its metrics rounded to 3; then `interval A` and `interval B` rounded to 3; then `A minus B` with the mean rounded to 3 and the interval rounded to 3; then a verdict line: `verdict: A is better` if the interval is entirely above zero, `verdict: B is better` if entirely below, otherwise `verdict: not established`.

  Then choose each model's threshold on the validation data, print them as `thresholds`, and run the report:

  ```python
{block(CALL)}  ```

  ```
{block(EXPECTED[key])}  ```

  The checks call your functions on hand-made labels with known answers, on two identical models, and on a model that is right wherever the other is wrong.
'''
    write(
        f"exercises/{folder}/exercise.yaml",
        f'''id: {folder}
stage: build
rev: 1
title: "{title}"
prompt: |
{prompt}{TEST_SKILLS}''',
    )
    write(f"exercises/{folder}/starter.py", "")
    write(f"exercises/{folder}/solution.py", build_solution(key))
    write(f"exercises/{folder}/test_exercise.py", build_tests(key))
    for name, (old, new) in WRONG.items():
        write(f"exercises/{folder}/wrong/{name}.py", build_solution(key).replace(old, new))
    write(
        f"exercises/{folder}/wrong/typed-in.py",
        "import numpy as np\n\n\n"
        + "def confusion(y, pred):\n    return (0, 0, 0, 0)\n\n\n"
        + "def metrics(tp, fp, fn, tn):\n    return (0.0, 0.0, 0.0, 0.0)\n\n\n"
        + "def accuracy_interval(correct, z=1.96):\n    return (0.0, 1.0)\n\n\n"
        + "def paired_bootstrap(rng, correct_a, correct_b, draws=2000):\n    return (0.0, 0.0, 0.0)\n\n\n"
        + "def choose_threshold(y_val, score_val):\n    return 1.0\n\n\n"
        + "def report(rng, y, score_a, score_b, threshold_a, threshold_b):\n"
        + "".join(f"    print({line!r})\n" for line in EXPECTED[key].splitlines()[1:])
        + "\n\n"
        + data_block(seed, sep_a, sep_b)
        + f"print({EXPECTED[key].splitlines()[0]!r})\n"
        + "report(rng, y, score_a, score_b, 1.0, 1.0)\n",
    )


write_build(
    "build-is-the-model-better",
    "Is the model better?",
    "Starting from a blank editor, do Module 5 in one program: judge two classifiers on the same held-out examples and say, with the uncertainty stated, whether one is better.",
    "main",
    "Model A should come out ahead, and the question is whether the data is enough to say so.",
)
write_build(
    "build-is-the-model-better-close",
    "Is the model better? Two close models",
    "Starting from a blank editor, judge two classifiers that are close on the same held-out examples, and say whether the data can tell them apart.",
    "close",
    "The two models are close; the report has to be honest about what two hundred examples can and can't establish.",
)
write_build(
    "build-is-the-model-better-reversed",
    "Is the model better? The newer model loses",
    "Starting from a blank editor, judge two classifiers on the same held-out examples where the model everyone expects to win doesn't.",
    "reversed",
    "Here model B is the sharper one; the verdict must follow the interval, not the naming.",
)

# =====================================================================================
# the debug
# =====================================================================================

write(
    "exercises/debug-evaluation-report/exercise.yaml",
    f'''id: debug-evaluation-report
stage: debug
rev: 1
title: "Three bugs in an evaluation report"
prompt: |
  This is the checkpoint's program on its data, and it should print:

  ```
{block(MAIN_EXPECTED)}  ```

  It has three bugs, in three different places. None of them crashes; each makes a number lie. Run it and compare:

  1. **The thresholds are chosen on the test set.** The first line prints `{LEAKED_THRESHOLDS.split(" ", 1)[1]}` and model A's accuracy comes out as {LEAKED_ACC_A}, flattering numbers that come from trying forty-one thresholds on the very examples being reported. The thresholds belong on the **validation** data, `y_val` and the validation scores.
  2. **Precision and recall are swapped** in `metrics`: precision divides by everything flagged, `tp + fp`; recall by everything really positive, `tp + fn`.
  3. **The comparison's interval is built from the wrong resamples:** `paired_bootstrap` resamples A's and B's correctness separately and subtracts, which throws away the pairing. It must resample the per-example **differences**. With that fixed, the `A minus B` line reads `{PAIRED_LINE.split(" ", 3)[3]}` instead of `{UNPAIRED_LINE.split(" ", 3)[3]}`.
# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.prob.evaluating-models/splits, ml.prob.evaluating-models/metrics, ml.prob.evaluating-models/compare]
  test_thresholds_come_from_validation: [ml.prob.evaluating-models/splits]
  test_metrics_and_pairing: [ml.prob.evaluating-models/metrics, ml.prob.sampling-and-confidence/bootstrap]
''',
)
write("exercises/debug-evaluation-report/starter.py", DEBUG_STARTER)
write("exercises/debug-evaluation-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-evaluation-report/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {MAIN_EXPECTED!r}


def test_the_output():
    """Prints honest thresholds, both reports, both intervals, the paired comparison and the verdict."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_thresholds_come_from_validation():
    """choose_threshold picks from the data it is given: perfectly separated validation scores put it between the classes."""
    choose_threshold = function("choose_threshold")
    assert 0.8 <= choose_threshold(np.array([0, 0, 1, 1]), np.array([0.2, 0.8, 1.2, 1.8])) < 1.2


def test_metrics_and_pairing():
    """8, 2, 4, 86 give precision 0.8 and recall 2/3, and two identical models differ by exactly zero."""
    metrics = function("metrics")
    paired_bootstrap = function("paired_bootstrap")
    assert abs(metrics(8, 2, 4, 86)[1] - 0.8) < 1e-12 and abs(metrics(8, 2, 4, 86)[2] - 2 / 3) < 1e-12
    correct = np.array([1, 0, 1, 1, 0, 1, 1, 1])
    assert paired_bootstrap(np.random.default_rng(0), correct, correct) == (0.0, 0.0, 0.0)
''',
)
write("exercises/debug-evaluation-report/wrong/two-of-three.py", DEBUG_ONE_LEFT)
write("exercises/debug-evaluation-report/wrong/one-of-three.py", DEBUG_TWO_LEFT)
write(
    "exercises/debug-evaluation-report/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def choose_threshold(y_val, score_val):\n    return 1.0\n\n\n"
    + "def metrics(tp, fp, fn, tn):\n    return (0.0, 0.0, 0.0, 0.0)\n\n\n"
    + "def paired_bootstrap(rng, correct_a, correct_b, draws=2000):\n    return (0.0, 0.0, 0.0)\n\n\n"
    + "".join(f"print({line!r})\n" for line in MAIN_EXPECTED.splitlines()),
)

# =====================================================================================
# the way through: a solved sibling
# =====================================================================================

write(
    "exercises/example-one-model-against-the-baseline/exercise.yaml",
    f'''id: example-one-model-against-the-baseline
stage: worked_example
rev: 1
title: "One model against the baseline"
prompt: |
  The checkpoint's tools, run on a single model against the model that always says no. Press **Run**, then read how each part works; the checkpoint is this with a second real model in place of the baseline, and a verdict.
steps:
  - label: "The functions"
    lines: "{ln('def confusion')}-{ln('def report') - 3}"
    note: "The confusion counts, the four metrics, the interval on an accuracy, the paired bootstrap and the threshold chosen on validation data are the ones you built across the module; the checkpoint's `report` (below them) just calls them in order."
  - label: "A threshold chosen honestly"
    lines: "{ln('threshold = choose_threshold')}-{ln('always_no = ')}"
    note: "The threshold is chosen on the validation scores, never on the examples about to be judged. The baseline predicts 0 for everyone."
  - label: "Counts, metrics and the baseline"
    lines: "{ln('tp, fp, fn, tn = confusion')}-{ln('print(' + chr(34) + 'always no' + chr(34))}"
    note: "The model's four counts and metrics, then the baseline's counts (no positives flagged at all, so no precision or recall to speak of) and its accuracy, which is just the share of negatives."
  - label: "How sure, and how much better"
    lines: "{ln('correct = (pred == y)')}-{ln('print(' + chr(34) + 'model minus baseline' + chr(34))}"
    note: "The interval on the model's accuracy, and the paired bootstrap of model minus baseline, which is well above zero: the model beats always-no by more than chance can explain. The checkpoint asks the same question of two real models, where the answer isn't obvious."
''',
)
write("exercises/example-one-model-against-the-baseline/solution.py", EXAMPLE)
write(
    "exercises/example-one-model-against-the-baseline/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the model's and the baseline's counts, the interval and the paired difference."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

# =====================================================================================
# the way through: the build in steps
# =====================================================================================


def write_step(folder, title, prompt, hints, starter, solution, tests, wrong_name, wrong, typed_in):
    write(
        f"exercises/{folder}/exercise.yaml",
        f'''id: {folder}
stage: fill_in
rev: 1
title: "{title}"
prompt: |
{block(prompt)}hints:
{"".join("  - " + json.dumps(h) + chr(10) for h in hints)}''',
    )
    write(f"exercises/{folder}/starter.py", starter)
    write(f"exercises/{folder}/solution.py", solution)
    write(f"exercises/{folder}/test_exercise.py", tests)
    write(f"exercises/{folder}/wrong/{wrong_name}.py", wrong)
    write(f"exercises/{folder}/wrong/typed-in.py", typed_in)


write_step(
    "step-confusion-counts",
    "Step 1: the four counts",
    f"The first part of the checkpoint is the confusion matrix. Replace each `...` so `confusion` counts the false positives (flagged, but the label is 0) and the false negatives (not flagged, but the label is 1), and the program prints both models' counts and shows the four add up to all 200 examples:\n\n```\n{STEP1_OUT}```\n",
    ["A false positive is `pred == 1` together with `y == 0`.", "A false negative is `pred == 0` together with `y == 1`."],
    STEP1_STARTER,
    STEP1_SOLUTION,
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints both models' counts and 200."""
    printed = run()
    assert printed == {STEP1_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_hand_made_labels():
    """Six hand-made labels give (2, 1, 1, 2)."""
    confusion = function("confusion")
    assert confusion(np.array([1, 1, 0, 0, 1, 0]), np.array([1, 0, 1, 0, 1, 0])) == (2, 1, 1, 2)
''',
    "fn-counts-positives",
    STEP1_SOLUTION.replace("    fn = int(((pred == 0) & (y == 1)).sum())", "    fn = int(((pred == 1) & (y == 1)).sum())"),
    PRELUDE + "def confusion(y, pred):\n    return (0, 0, 0, 0)\n\n\n" + "".join(f"print({line!r})\n" for line in STEP1_OUT.splitlines()),
)

write_step(
    "step-four-metrics",
    "Step 2: the four metrics",
    f"With the counts in hand, the metrics follow. Replace each `...` so precision divides by everything flagged and recall by everything really positive, and the program prints both models' accuracy, precision, recall and F1:\n\n```\n{STEP2_OUT}```\n",
    ["Everything flagged is `tp + fp`.", "Everything really positive is `tp + fn`."],
    STEP2_STARTER,
    STEP2_SOLUTION,
    f'''from checks import function, run


def test_the_output():
    """Prints both models' metrics."""
    printed = run()
    assert printed == {STEP2_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_known_counts():
    """8, 2, 4, 86 give accuracy 0.94, precision 0.8, recall 2/3 and F1 8/11."""
    metrics = function("metrics")
    accuracy, precision, recall, f1 = metrics(8, 2, 4, 86)
    assert abs(accuracy - 0.94) < 1e-12 and abs(precision - 0.8) < 1e-12
    assert abs(recall - 2 / 3) < 1e-12 and abs(f1 - 8 / 11) < 1e-12
''',
    "swapped",
    STEP2_SOLUTION.replace("    precision = tp / (tp + fp)\n    recall = tp / (tp + fn)", "    precision = tp / (tp + fn)\n    recall = tp / (tp + fp)"),
    PRELUDE + "def metrics(tp, fp, fn, tn):\n    return (0.0, 0.0, 0.0, 0.0)\n\n\n" + "".join(f"print({line!r})\n" for line in STEP2_OUT.splitlines()),
)

write_step(
    "step-interval-on-an-accuracy",
    "Step 3: an interval on each accuracy",
    f"Each accuracy is a mean of 200 zeros and ones, so it gets a standard error and an interval. Replace each `...` so the standard error is `sqrt(p(1 - p) / n)` and the interval reaches `z` standard errors each side, and the program prints each model's accuracy with its interval:\n\n```\n{STEP3_OUT}```\n",
    ["`n` is `len(correct)`, and the whole fraction goes under the square root.", "The half-width is `z` times the standard error."],
    STEP3_STARTER,
    STEP3_SOLUTION,
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints both accuracies with their intervals."""
    printed = run()
    assert printed == {STEP3_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_known_accuracy():
    """0.9 on 100 examples spans 0.841 to 0.959."""
    accuracy_interval = function("accuracy_interval")
    low, high = accuracy_interval(np.array([1] * 90 + [0] * 10))
    assert abs(low - 0.8412) < 0.001 and abs(high - 0.9588) < 0.001
''',
    "no-root",
    STEP3_SOLUTION.replace("    se = np.sqrt(p * (1 - p) / len(correct))", "    se = p * (1 - p) / len(correct)"),
    PRELUDE + "def accuracy_interval(correct, z=1.96):\n    return (0.0, 1.0)\n\n\n" + "".join(f"print({line!r})\n" for line in STEP3_OUT.splitlines()),
)

write_step(
    "step-paired-bootstrap",
    "Step 4: the paired comparison",
    f"The last piece before the full build: are the two models really different? Replace each `...` so the bootstrap resamples the per-example **differences** with replacement and takes the 2.5th and 97.5th percentiles of their mean, and the program prints the mean difference with its interval and whether the interval sits above zero:\n\n```\n{STEP4_OUT}```\n",
    ["Resample `diff`, the array of per-example differences, not the two models separately.", "The upper percentile of a 95 percent interval is 97.5."],
    STEP4_STARTER,
    STEP4_SOLUTION,
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the mean difference, its interval and the comparison with zero."""
    printed = run()
    assert printed == {STEP4_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_identical_and_better_models():
    """Two identical models differ by exactly zero with a zero-width interval; a model right where the other is wrong gets a positive interval."""
    paired_bootstrap = function("paired_bootstrap")
    correct = np.array([1, 0, 1, 1, 0, 1, 1, 0, 1, 1] * 4)
    assert paired_bootstrap(np.random.default_rng(0), correct, correct) == (0.0, 0.0, 0.0)
    better = np.ones(40, dtype=int)
    mean, low, high = paired_bootstrap(np.random.default_rng(0), better, correct)
    assert abs(mean - 0.3) < 1e-12 and 0 < low <= high
''',
    "unpaired",
    STEP4_SOLUTION.replace(
        "    means = np.array([rng.choice(diff, size=len(diff)).mean() for _ in range(draws)])",
        "    means = np.array([rng.choice(correct_a, size=len(diff)).mean() - rng.choice(correct_b, size=len(diff)).mean() for _ in range(draws)])",
    ),
    PRELUDE + "def paired_bootstrap(rng, correct_a, correct_b, draws=2000):\n    return (0.18, 0.11, 0.255)\n\n\n" + "".join(f"print({line!r})\n" for line in STEP4_OUT.splitlines()),
)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.m5.checkpoint
kind: checkpoint
status: ready
title: "Checkpoint 5: is the model better?"
summary: "Two classifiers' predictions on a held-out set, judged with a confusion matrix, the metrics, bootstrap intervals and a decision."
prerequisites: [ml.prob.bayes, ml.prob.maximum-likelihood, ml.prob.evaluating-models]
estimated_minutes: 120
packages: [numpy]
rev: 1
objectives:
  - "Evaluate two models' predictions on a held-out set with a confusion matrix, precision, recall and a bootstrap interval on the difference, and recommend one."
  - "Find and fix three bugs in an evaluation report: a threshold chosen on the test set, precision and recall swapped, and an interval built from the wrong resamples."
  - "Explain Bayes' rule with a base rate, and what a confidence interval does and doesn't promise."
prove:
  build: build-is-the-model-better
  debug: debug-evaluation-report
  explain:
    prompt: |
      Your checkpoint report says model A's accuracy is about 0.83 with an interval of roughly 0.78 to 0.88, and that A beats B by about 0.09 with an interval that stays above zero. A stakeholder asks three things. First: "the test for the rare condition this model screens for is 95 percent accurate, so a positive means the person almost certainly has it, right?" Second: "does your interval mean there's a 95 percent chance the true accuracy is inside it?" Third: "why not just compare the two accuracies?" In your own words, answer all three: Bayes' rule with a base rate for the first, what a confidence interval promises and doesn't for the second, and why the comparison was paired, and what "not established" would have meant, for the third.
    rubric:
      - id: bayes
        required: true
        description: "Walks a base rate through: with a rare condition (say 1 in 100), a 95 percent hit rate and a few percent of false alarms among the many healthy, the false positives outnumber the true ones, so a positive person's chance of having it is a small fraction, not 95 percent; P(positive given sick) is not P(sick given positive), and the prior decides."
      - id: interval
        required: true
        description: "The 95 percent is a property of the procedure: over many repeated test sets and intervals, about 95 percent of the intervals would contain the true accuracy. It is not a statement that 95 percent of examples are inside, nor that the true value is likelier near the middle; the sample's own accuracy is always exactly in the middle."
      - id: paired
        required: true
        description: "Both models were scored on the same examples, so the hard examples are hard for both; differencing per example and bootstrapping the mean difference removes that shared noise and asks only where the models disagree. Comparing two separate intervals would be weaker, and overlapping intervals wouldn't prove the models equal. 'Not established' would mean the difference's interval included zero: the data can't tell, and the answer is more test data, not a coin flip."
      - id: recommendation
        required: false
        description: "A recommendation follows the interval, not the naming or the raw gap: A, here, because the interval excludes zero; and with 'not established' the honest recommendation is to keep the simpler or cheaper model until more data decides."
    model_answer: |
      For the first question, the 95 percent is the chance of a positive test given that someone has the condition, and that is the wrong way round for the stakeholder's question. Suppose one person in a hundred has it and the test wrongly flags five percent of the healthy. In a hundred thousand people, a thousand have it and about 950 test positive; ninety-nine thousand don't, and about 4,950 of them test positive anyway. A positive person is one of about 5,900, of whom 950 have the condition: roughly sixteen percent, not ninety-five. The base rate decides, because the healthy group is so much larger that its small error rate outweighs the sick group's high hit rate. That is Bayes' rule: prior times likelihood, divided by the total chance of a positive from both groups. For the second, the 95 percent describes the procedure, not this one interval. If we drew many test sets of two hundred and built an interval from each, about ninety-five in a hundred of those intervals would contain the model's true accuracy. It doesn't mean ninety-five percent of the examples fall inside the range, and it doesn't make the true value likelier near the middle; our measured 0.83 is always exactly in the middle, because we built the interval around it. For the third, both models were scored on the same two hundred examples, and the hard examples are hard for both, so a lot of the wobble in the two accuracies is shared. Taking A's correctness minus B's on each example and bootstrapping the mean of those differences removes the shared wobble and asks only about the examples where the models disagree, which is a sharper test than comparing two separate intervals, and two overlapping intervals wouldn't have proved the models equal anyway. The verdict follows that interval: it stays above zero, so A is better by more than chance explains. Had it included zero, "not established" would have meant the data can't tell the models apart, and the right next step would be more test data, keeping the simpler or cheaper model meanwhile.
# For a learner who's stuck on the build (ADR-0012): a solved sibling, the
# build in steps with hints, then fresh versions.
unstuck:
  example: example-one-model-against-the-baseline
  steps: [step-confusion-counts, step-four-metrics, step-interval-on-an-accuracy, step-paired-bootstrap]
  versions: [build-is-the-model-better-close, build-is-the-model-better-reversed]
''',
)

print("ml.m5.checkpoint written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
