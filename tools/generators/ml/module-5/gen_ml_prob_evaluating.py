"""Writes the topic ml.prob.evaluating-models (Module 5's seventh topic). Run
from the repository root under uv (python -m uv run python <this file>), so
every program's expected output is captured from CPython rather than typed
in. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.prob.evaluating-models")


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


def numbered(program: str) -> str:
    return "".join(f"{i + 1:>3} {line}\n" for i, line in enumerate(program.splitlines()))


DATA = '''rng = np.random.default_rng(12)
n = 200
y = (rng.random(n) < 0.3).astype(int)
score_a = y * 2.0 + rng.normal(0, 1, size=n)
score_b = y * 1.2 + rng.normal(0, 1, size=n)
y_val = (rng.random(n) < 0.3).astype(int)
score_a_val = y_val * 2.0 + rng.normal(0, 1, size=n)
'''
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
'''

# --- the worked example --------------------------------------------------------------------

EXAMPLE = "import numpy as np\n\n\n" + FUNCTIONS + "\n\n" + DATA + '''
pred_a = (score_a > 1.0).astype(int)
pred_b = (score_b > 0.6).astype(int)
for name, pred in (("A", pred_a), ("B", pred_b)):
    tp, fp, fn, tn = confusion(y, pred)
    print(name, (tp, fp, fn, tn), np.round(metrics(tp, fp, fn, tn), 3))
print("always no", round(float((y == 0).mean()), 3))

correct = (pred_a == y).astype(int)
accuracy = correct.mean()
se = np.sqrt(accuracy * (1 - accuracy) / n)
print(round(float(accuracy), 3), round(float(se), 3), np.round([accuracy - 1.96 * se, accuracy + 1.96 * se], 3))

thresholds = np.arange(0.0, 2.01, 0.05)
best_val = thresholds[np.argmax([((score_a_val > t).astype(int) == y_val).mean() for t in thresholds])]
best_test = thresholds[np.argmax([((score_a > t).astype(int) == y).mean() for t in thresholds])]
print(round(float(best_val), 2), round(float(((score_a > best_val).astype(int) == y).mean()), 3))
print(round(float(best_test), 2), round(float(((score_a > best_test).astype(int) == y).mean()), 3))

diff = correct - (pred_b == y).astype(int)
boot = np.array([rng.choice(diff, size=n).mean() for _ in range(2000)])
print(round(float(diff.mean()), 3), np.round(np.percentile(boot, [2.5, 97.5]), 3))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
lines = EXAMPLE_OUT.splitlines()
A = lines[0]
B = lines[1]
acc_a = float(A.split("[")[1].split()[0])
acc_b = float(B.split("[")[1].split()[0])
BASELINE = lines[2].split()[-1]
assert acc_a > acc_b > float(BASELINE), (acc_a, acc_b, BASELINE)
INTERVAL = lines[3]
VAL_LINE, TEST_LINE = lines[4], lines[5]
assert float(TEST_LINE.split()[1]) >= float(VAL_LINE.split()[1]), (VAL_LINE, TEST_LINE)
DIFF_LINE = lines[6]
diff_low, diff_high = (float(v) for v in DIFF_LINE.split("[")[1].rstrip("]").split())
INCLUDES_ZERO = diff_low < 0 < diff_high
assert "e-" not in EXAMPLE_OUT

# --- the fill-in ----------------------------------------------------------------------------

FILL_HEAD = '''def metrics(tp, fp, fn, tn):
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    precision = tp / (tp + FP)
    recall = tp / (tp + FN)
    f1 = 2 * precision * recall / (precision + recall)
    return round(accuracy, 3), round(precision, 3), round(recall, 3), round(f1, 3)


print(metrics(8, 2, 4, 86))
print(metrics(30, 0, 70, 100))
print(metrics(100, 100, 0, 0))
'''
FILL_SOLUTION = FILL_HEAD.replace("(tp + FP)", "(tp + fp)").replace("(tp + FN)", "(tp + fn)")
FILL_STARTER = FILL_HEAD.replace("(tp + FP)", "(tp + ...)").replace("(tp + FN)", "(tp + ...)")
FILL_SWAPPED = FILL_SOLUTION.replace("    precision = tp / (tp + fp)\n    recall = tp / (tp + fn)", "    precision = tp / (tp + fn)\n    recall = tp / (tp + fp)")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT == "(0.94, 0.8, 0.667, 0.727)\n(0.65, 1.0, 0.3, 0.462)\n(0.5, 0.5, 1.0, 0.667)\n", FILL_OUT
assert out(FILL_SWAPPED) != FILL_OUT

# --- the write ---------------------------------------------------------------------------------

WRITE_STARTER = '''import numpy as np

rng = np.random.default_rng(5)
correct = (rng.random(200) < 0.84).astype(int)
'''
WRITE_SOLUTION = WRITE_STARTER + '''

def accuracy_interval(correct, z=1.96):
    p = correct.mean()
    se = np.sqrt(p * (1 - p) / len(correct))
    return round(float(p), 3), round(float(p - z * se), 3), round(float(p + z * se), 3)


print(accuracy_interval(correct))
print(accuracy_interval(np.tile(correct, 4)))
print(accuracy_interval(np.ones(50, dtype=int)))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
write_lines = WRITE_OUT.splitlines()
assert write_lines[2] == "(1.0, 1.0, 1.0)", WRITE_OUT
WRITE_NO_ROOT = WRITE_SOLUTION.replace("    se = np.sqrt(p * (1 - p) / len(correct))", "    se = p * (1 - p) / len(correct)")
assert out(WRITE_NO_ROOT) != WRITE_OUT

# --- the build -----------------------------------------------------------------------------------

BUILD_SOLUTION = "import numpy as np\n\n\n" + FUNCTIONS + '''

def accuracy_interval(correct, z=1.96):
    p = correct.mean()
    se = np.sqrt(p * (1 - p) / len(correct))
    return float(p - z * se), float(p + z * se)


def paired_bootstrap(rng, correct_a, correct_b, draws=2000):
    diff = correct_a - correct_b
    means = np.array([rng.choice(diff, size=len(diff)).mean() for _ in range(draws)])
    low, high = np.percentile(means, [2.5, 97.5])
    return float(diff.mean()), float(low), float(high)


''' + DATA + '''
pred_a = (score_a > 1.0).astype(int)
pred_b = (score_b > 0.6).astype(int)
for name, pred in (("A", pred_a), ("B", pred_b)):
    print(name, confusion(y, pred), np.round(metrics(*confusion(y, pred)), 3))
correct_a = (pred_a == y).astype(int)
correct_b = (pred_b == y).astype(int)
print("interval for A", np.round(accuracy_interval(correct_a), 3))
print("A minus B", np.round(paired_bootstrap(rng, correct_a, correct_b), 3))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT.splitlines()[0].startswith("A (") and BUILD_OUT.splitlines()[3].startswith("A minus B ["), BUILD_OUT
BUILD_SWAPPED = BUILD_SOLUTION.replace("    precision = tp / (tp + fp)\n    recall = tp / (tp + fn)", "    precision = tp / (tp + fn)\n    recall = tp / (tp + fp)")
BUILD_NO_ROOT = BUILD_SOLUTION.replace("    se = np.sqrt(p * (1 - p) / len(correct))", "    se = p * (1 - p) / len(correct)")
BUILD_UNPAIRED = BUILD_SOLUTION.replace(
    "    diff = correct_a - correct_b\n    means = np.array([rng.choice(diff, size=len(diff)).mean() for _ in range(draws)])",
    "    diff = correct_a - correct_b\n    means = np.array([rng.choice(correct_a, size=len(diff)).mean() - rng.choice(correct_b, size=len(diff)).mean() for _ in range(draws)])",
)
for wrong in (BUILD_SWAPPED, BUILD_NO_ROOT, BUILD_UNPAIRED):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug --------------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def metrics(tp, fp, fn, tn):
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)
    return accuracy, precision, recall, f1


def accuracy_interval(accuracy, n, z=1.96):
    se = np.sqrt(accuracy * (1 - accuracy) / n)
    return accuracy - z * se, accuracy + z * se


accuracy, precision, recall, f1 = metrics(30, 10, 20, 140)
print("metrics", round(accuracy, 3), round(precision, 3), round(recall, 3), round(f1, 3))
low, high = accuracy_interval(accuracy, 200)
print("interval", round(float(low), 3), round(float(high), 3))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("    f1 = 2 * precision * recall / (precision + recall)", "    f1 = (precision + recall) / 2").replace(
    "    se = np.sqrt(accuracy * (1 - accuracy) / n)", "    se = np.sqrt(accuracy * (1 - accuracy)) / n"
)
DEBUG_F1_ONLY = DEBUG_SOLUTION.replace("    se = np.sqrt(accuracy * (1 - accuracy) / n)", "    se = np.sqrt(accuracy * (1 - accuracy)) / n")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == "metrics 0.85 0.75 0.6 0.667\ninterval 0.801 0.899\n", DEBUG_OUT
assert out(DEBUG_F1_ONLY) != DEBUG_OUT

# --- predict items ------------------------------------------------------------------------------------

PREDICT_TABLE = '''tp, fp, fn, tn = 8, 2, 4, 86
print((tp + tn) / (tp + fp + fn + tn))
print(tp / (tp + fp), round(tp / (tp + fn), 3))
print(round((tn + fn) / (tp + fp + fn + tn), 2))
'''
PREDICT_TABLE_OUT = out(PREDICT_TABLE)
print("predict table:\n" + PREDICT_TABLE_OUT)
assert PREDICT_TABLE_OUT == "0.94\n0.8 0.667\n0.9\n", PREDICT_TABLE_OUT

REVIEW_SE = '''import numpy as np

for n in (50, 200, 800):
    se = np.sqrt(0.9 * 0.1 / n)
    print(n, round(float(se), 3), round(float(1.96 * se), 3))
'''
REVIEW_SE_OUT = out(REVIEW_SE)
print("review se:\n" + REVIEW_SE_OUT)
assert REVIEW_SE_OUT == "50 0.042 0.083\n200 0.021 0.042\n800 0.011 0.021\n", REVIEW_SE_OUT

REVIEW_CODE_STARTER = ""
REVIEW_CODE_SOLUTION = '''def precision_recall(tp, fp, fn):
    return tp / (tp + fp), tp / (tp + fn)


print(precision_recall(8, 2, 4))
print(precision_recall(30, 0, 70))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "(0.8, 0.6666666666666666)\n(1.0, 0.3)\n", REVIEW_CODE_OUT

ZERO_PHRASE = "includes zero, so these 200 examples don't establish that A is better" if INCLUDES_ZERO else "stays above zero, so even with the sampling noise A is better on this test set"

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.prob.evaluating-models
kind: topic
status: ready
title: "Evaluating a model with statistics"
summary: "Train, validation and test splits, the confusion matrix and the metrics built from it, confidence intervals on an accuracy, and comparing two models fairly."
prerequisites: [ml.prob.sampling-and-confidence, ml.calc.loss-functions]
packages: [numpy]
estimated_minutes: 60
rev: 1
objectives:
  - "Split data into train, validation and test sets, and say what each is for and what leaks between them."
  - "Build a confusion matrix and compute accuracy, precision, recall and F1 from it."
  - "Put a confidence interval on an accuracy, and say when a test set is too small to tell."
  - "Compare two models on the same test set, and say whether the difference is real."
# Linked, never copied or embedded: Google's Machine Learning Crash Course is
# CC BY 4.0; Wikipedia is CC BY-SA 4.0; NumPy's documentation is under the
# NumPy licence (BSD-3-Clause).
resources:
  - title: "Google Machine Learning Crash Course: Classification, the pages on thresholds, the confusion matrix, and accuracy, recall, precision and related metrics"
    url: https://developers.google.com/machine-learning/crash-course/classification
    type: reading
    use: link
    license: CC BY 4.0
  - title: "Wikipedia: Precision and recall (the Introduction and Definition sections)"
    url: https://en.wikipedia.org/wiki/Precision_and_recall
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "numpy.percentile (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.percentile.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-judging-two-classifiers
  - parsons-precision-and-recall
  - mcq-ninety-seven-percent-accurate
  - predict-a-confusion-matrix
  - mcq-what-each-split-is-for
  - mcq-why-paired
  - fill-the-four-metrics
  - write-accuracy-interval
prove:
  build: build-an-evaluation-report
  debug: debug-metrics-report
  explain:
    prompt: |
      Your team's new model scores 0.91 accuracy on the test set against the old model's 0.89, on the same 200 examples, and the team wants to ship it. In your own words: what are the train, validation and test splits for, and what would have gone wrong if the new model's threshold had been tuned on the test set? Why can accuracy alone mislead, and what question do precision and recall each answer? How sure can you be about 0.91 from 200 examples? And how would you decide whether 0.91 really beats 0.89 on the same examples?
    rubric:
      - id: splits
        required: true
        description: "Train fits the weights; validation chooses what the training can't (thresholds, learning rates, when to stop); test is touched once, to report. Tuning anything on the test set leaks it into the model's choices, so the reported number is optimistic and no longer an estimate of performance on new data."
      - id: metrics
        required: true
        description: "Accuracy counts every example alike, so on a rare class a model that always says no scores high; precision answers 'of the ones flagged, how many were right?' and recall 'of the real ones, how many were found?', from the confusion matrix's true and false positives and negatives; F1 combines them."
      - id: interval
        required: true
        description: "An accuracy from 200 examples has standard error sqrt(0.91 × 0.09 / 200), about 0.02, so the interval is roughly 0.87 to 0.95; the two models' intervals overlap heavily."
      - id: compare
        required: true
        description: "Because both models were scored on the same examples, compare them paired: take each example's difference in correctness, bootstrap the mean difference, and see whether the interval excludes zero; two points on 200 examples is about one standard error and usually doesn't, so the honest answer is 'not established; test on more data before shipping on this evidence'."
    model_answer: |
      The three splits keep three jobs apart. The training set fits the model's weights. The validation set chooses the things training can't choose for itself: the classification threshold, the learning rate, how long to train, which of several models to keep. The test set is touched once, at the end, to report a number that estimates how the model will do on data it has never seen. If the new model's threshold had been tuned on the test set, the test set would have leaked into the model's choices: the reported 0.91 would be the best of many tries on those particular 200 examples, optimistic by construction, and no longer an estimate of anything about new data. Accuracy alone can mislead because it counts every example the same way; if only one example in ten is positive, a model that always says no is 90 percent accurate and useless. The confusion matrix splits the results into true and false positives and negatives, and from it precision answers "of the examples the model flagged, how many really were positive?" while recall answers "of the examples that really were positive, how many did the model find?". F1 combines the two so that neither can hide the other. As for how sure 0.91 is: it is a sample mean of 200 zeros and ones, so its standard error is the square root of 0.91 times 0.09 over 200, about 0.02, and the 95 percent interval runs from about 0.87 to 0.95. The old model's interval, around 0.89, overlaps it almost entirely. To compare them properly I'd use the fact that both were scored on the same 200 examples: for each example, take the new model's correctness minus the old one's, bootstrap the mean of those differences, and see whether the interval excludes zero. A two-point difference on 200 examples is about one standard error and usually doesn't, so the honest conclusion is that the improvement isn't established yet, and the right next step is a bigger test set, not a launch.
review_pool:
  - review-predict-standard-errors-of-an-accuracy
  - review-mcq-which-metric
  - review-mcq-two-points-apart
  - review-mcq-validation-and-test
  - review-precision-recall
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: splits
    description: "Say what the train, validation and test splits are for, and what leaks when the test set is used for choices"
  - id: metrics
    description: "Build a confusion matrix and compute accuracy, precision, recall and F1, and say when accuracy misleads"
  - id: interval
    description: "Put a confidence interval on an accuracy and say when a test set is too small to tell"
  - id: compare
    description: "Compare two models on the same test set with a paired bootstrap, and say whether the difference is established"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

A model is only as good as the number you can honestly report for it, and this topic is how to earn that number. Three **splits** keep fitting, choosing and reporting apart; the **confusion matrix** turns a classifier's answers into four counts and the metrics that come from them, because accuracy alone can hide a useless model; the last topic's standard error puts an interval on an accuracy; and a **paired bootstrap** says whether one model really beats another on the same examples. The worked example judges two classifiers on 200 held-out examples with every tool in the module.

The main resource is **Google's Machine Learning Crash Course, the classification pages** on thresholds, the confusion matrix, and accuracy, recall and precision; about 30 minutes of reading with small interactive exercises. Wikipedia's _Precision and recall_ has the definitions and the standard picture. Watch for:

- **Four counts** behind every classification metric.
- **Which mistake costs more** decides which metric to watch.
- **The threshold is a choice**, made on validation data.

</Intro>

<Resource index={{0}} />

<Recap>

- **Three splits.** **Train** fits the weights. **Validation** chooses what training can't: the threshold, the learning rate, when to stop, which model to keep. **Test** is touched once, to report. Using the test set for any choice is **leakage**: the number becomes the best of many tries on those examples and stops estimating performance on new data. In the worked example, the threshold chosen on validation data gave a test accuracy of {VAL_LINE.split()[1]}; the one chosen on the test set itself gave {TEST_LINE.split()[1]}, a number that flatters.
- **The confusion matrix** splits a classifier's answers into **true positives** (flagged, and right), **false positives** (flagged, but wrong), **false negatives** (missed) and **true negatives** (correctly left alone). Every metric is built from those four counts.
- **Accuracy** is `(tp + tn) / n`, and it misleads on a rare class: the worked example's data is 30 percent positive, so "always no" scores {BASELINE} without learning anything. **Precision** `tp / (tp + fp)` asks "of the ones flagged, how many were right?"; **recall** `tp / (tp + fn)` asks "of the real ones, how many were found?"; **F1** is their harmonic mean, `2pr / (p + r)`, low if either is low. Which mistake costs more decides which to watch: a screening test wants recall, a spam filter wants precision.
- **Model A against model B:** A scores {A.split("[")[1].rstrip("]")} on accuracy, precision, recall and F1, B scores {B.split("[")[1].rstrip("]")}.
- **An interval on an accuracy.** An accuracy is the mean of `n` zeros and ones, so its standard error is `sqrt(p(1 - p) / n)`: for A, {INTERVAL.split()[1]}, and the 95 percent interval is {INTERVAL.split("[")[1].rstrip("]")}. On 200 examples, two models two points apart are about one standard error apart: not yet distinguishable.
- **Comparing two models on the same examples:** don't compare two intervals; compare the models **paired**. For each example take A's correctness minus B's, bootstrap the mean of those differences, and read the interval. In the worked example the mean difference is {DIFF_LINE.split()[0]} with an interval of {DIFF_LINE.split("[")[1].rstrip("]")}, which {ZERO_PHRASE}. Pairing removes the noise the two models share (the hard examples are hard for both).
- **When a test set is too small to tell,** the interval says so: the fix is more test data, not a different metric.
- **In machine learning:** every leaderboard number is a sample mean with a standard error nobody printed; "we tuned on the test set" is the commonest way a published result fails to replicate; and a model's threshold is a product decision about which mistake is dearer, set on validation data and reported on test data.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-precision-and-recall.yaml",
    '''id: parsons-precision-and-recall
type: parsons
rev: 1
prompt: |
  A classifier flagged 10 examples, 8 of them rightly, and missed 4 real ones. Put the lines in order to print its precision and recall, `0.8 0.667`. One line is a decoy that doesn't belong.
lines:
  - 'tp, fp, fn = 8, 2, 4'
  - 'precision = tp / (tp + fp)'
  - 'recall = tp / (tp + fn)'
  - 'print(precision, round(recall, 3))'
distractors:
  - 'recall = tp / (tp + fp)'
explanation: |
  Precision divides the true positives by everything the model **flagged** (true plus false positives): 8 of 10. Recall divides them by everything that was **really positive** (true positives plus the ones missed): 8 of 12. The decoy computes precision twice; the two questions differ in what goes in the denominator.
skills: [metrics]
''',
)

write(
    "recall/mcq-ninety-seven-percent-accurate.yaml",
    '''id: mcq-ninety-seven-percent-accurate
type: mcq
rev: 1
prompt: |
  A model that screens for a condition 3 percent of people have reports 97 percent accuracy. What do you need to know before being impressed?
choices:
  - 'Nothing; 97 percent is excellent for any problem'
  - 'Its recall and precision: a model that says "no" to everyone is also 97 percent accurate, so accuracy alone says nothing about whether it finds the 3 percent'
  - 'Its training accuracy, which is the number that matters'
  - 'Whether it used a neural network'
answer: 1
explanation: |
  With a rare positive class, accuracy is dominated by the easy negatives: always-no gets 97 of every 100 right and finds nobody. Recall says how many of the real cases it catches, precision how many of its alarms are real, and the confusion matrix gives both. The training accuracy is the one number that is never the answer.
skills: [metrics]
''',
)

write(
    "recall/predict-a-confusion-matrix.yaml",
    f'''id: predict-a-confusion-matrix
type: predict_output
rev: 1
prompt: |
  Four counts from a confusion matrix, and the numbers built from them. What does the program print?
code: |
{block(PREDICT_TABLE)}expected_output: |
{block(PREDICT_TABLE_OUT)}explanation: |
  Accuracy is the 94 right answers out of 100. Precision is 8 of the 10 flagged; recall is 8 of the 12 that were real. The last line is the accuracy of a model that says "no" to everyone: 90 of 100, only four points below the real model, which is what a rare class does to accuracy.
skills: [metrics]
''',
)

write(
    "recall/mcq-what-each-split-is-for.yaml",
    '''id: mcq-what-each-split-is-for
type: mcq
rev: 1
prompt: |
  You try ten classification thresholds and keep the one with the best accuracy on the test set, then report that accuracy. What has gone wrong?
choices:
  - 'Nothing: the test set is for measuring accuracy, and that''s what it measured'
  - 'The threshold should have been chosen on the training set instead'
  - 'The test set was used to make a choice, so it leaked into the model: the reported number is the best of ten tries on those examples and overstates what new data will show; the threshold belongs on the validation set, and the test set is touched once'
  - 'Ten thresholds is too few; a hundred would make the test accuracy reliable'
answer: 2
explanation: |
  Any choice made by looking at the test set turns it into training data for that choice. The best of ten tries on a fixed set is biased upwards, more so with more tries, and the worked example shows a threshold chosen on the test set flattering the result. Choices go on the validation split; the training set would overfit the threshold to data the model has already seen.
skills: [splits]
''',
)

write(
    "recall/mcq-why-paired.yaml",
    '''id: mcq-why-paired
type: mcq
rev: 1
prompt: |
  Two models were scored on the same 200 test examples. Why compare them through the per-example differences in correctness, rather than through the two accuracies' separate intervals?
choices:
  - 'Because the two separate intervals are always identical for the same test set'
  - 'Because the hard examples are hard for both models: that shared noise cancels in the per-example differences, so the paired comparison is sharper, while two overlapping intervals settle nothing either way'
  - 'Because the bootstrap only works on differences'
  - 'There is no reason; comparing the two intervals is just as good'
answer: 1
explanation: |
  Each model''s accuracy wobbles with which examples happened to land in the test set, and both models wobble together. Pairing (A''s correctness minus B''s on each example) removes that shared wobble and asks only where the models disagree. Two separate intervals that overlap don''t prove the models equal; the paired interval, including or excluding zero, is the question actually asked.
skills: [compare]
''',
)

write(
    "recall/review-mcq-validation-and-test.yaml",
    '''id: review-mcq-validation-and-test
type: mcq
rev: 1
prompt: |
  You have 1,000 labelled examples, three candidate models to choose between, and you must report the winner''s accuracy. How do you split the data, and which number do you report?
choices:
  - 'Train on all 1,000, pick the model with the best training accuracy, report that'
  - 'Train on 800, pick the best of the three on the other 200, report its accuracy on those 200'
  - 'Train on, say, 600; choose among the three on a validation set of 200; report the chosen model''s accuracy on a test set of 200 that no choice ever touched'
  - 'Split in half; train on one half and report the accuracy on the same half'
answer: 2
explanation: |
  Fitting, choosing and reporting are three jobs, and each needs data the previous job never saw. Picking the best of three on 200 examples and reporting that same number is the best of three tries, optimistic by construction; the test set exists so that the final number is an estimate of new data, which it stops being the moment it is used to choose anything.
skills: [splits]
''',
)

write(
    "recall/review-predict-standard-errors-of-an-accuracy.yaml",
    f'''id: review-predict-standard-errors-of-an-accuracy
type: predict_output
rev: 1
prompt: |
  The standard error of an accuracy of 0.9 at three test-set sizes, and the half-width of its 95 percent interval. What does the program print?
code: |
{block(REVIEW_SE)}expected_output: |
{block(REVIEW_SE_OUT)}explanation: |
  An accuracy is a mean of zeros and ones, with standard error `sqrt(p(1 - p) / n)`. On 50 examples an accuracy of 0.9 is really "somewhere between 0.82 and 0.98"; it takes 800 examples to pin it within two points. Quadrupling the test set halves the width each time.
skills: [interval]
''',
)

write(
    "recall/review-mcq-which-metric.yaml",
    '''id: review-mcq-which-metric
type: mcq
rev: 1
prompt: |
  Two classifiers: one screens blood samples for a serious disease that will be confirmed by a second test; the other decides which emails to hide as spam. Which metric matters most for each?
choices:
  - 'Accuracy for both; it''s the standard metric'
  - 'Recall for the screen (missing a case is the costly mistake, and the second test will catch false alarms); precision for the spam filter (hiding a real email is the costly mistake)'
  - 'Precision for the screen and recall for the spam filter'
  - 'F1 for both, always'
answer: 1
explanation: |
  Ask which mistake costs more. For the screen, a missed case (a false negative) can be fatal while a false alarm costs one more test, so recall is the number to protect. For the spam filter, a hidden real email (a false positive) is worse than a spam that slips through, so precision is. F1 is a compromise for when both matter about equally.
skills: [metrics]
''',
)

write(
    "recall/review-mcq-two-points-apart.yaml",
    '''id: review-mcq-two-points-apart
type: mcq
rev: 1
prompt: |
  Model A scores 0.91 and model B 0.89 on the same 200 test examples. What is the right conclusion, and the right next step?
choices:
  - 'A is better by two points; ship it'
  - 'B is better, because 0.89 is more honest'
  - 'The two intervals (each about plus or minus 0.04) overlap, so the models are proven equal'
  - 'The difference is about one standard error, so it isn''t established; compare them paired on the same examples with a bootstrap of the per-example difference, and if the interval still includes zero, get more test data before deciding'
answer: 3
explanation: |
  Each accuracy has a standard error near 0.02 on 200 examples, so two points is noise-sized. Overlapping intervals don''t prove equality either; they say the data can''t tell. The sharpest test uses the pairing: the same examples scored by both models, differenced per example and bootstrapped, which removes the noise the two models share. If that interval includes zero, the honest answer is "more data".
skills: [compare, interval]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-judging-two-classifiers/exercise.yaml",
    f'''id: example-judging-two-classifiers
stage: worked_example
rev: 1
title: "Judging two classifiers"
prompt: |
  This program scores two classifiers on 200 held-out examples: their confusion matrices and metrics, the always-no baseline, an interval on an accuracy, a threshold chosen honestly and dishonestly, and a paired bootstrap of the difference between them. Press **Run**, then read how each part works.
steps:
  - label: "The four counts, and the metrics from them"
    lines: "4-17"
    note: "`confusion` counts true positives (flagged and right), false positives (flagged but wrong), false negatives (missed) and true negatives (correctly left alone). `metrics` turns them into accuracy, precision (`tp / (tp + fp)`: of the flagged, how many were right), recall (`tp / (tp + fn)`: of the real ones, how many were found) and F1, their harmonic mean."
  - label: "Two models' scores on the same examples"
    lines: "20-26"
    note: "Two hundred labels, 30 percent positive, and each model's score for each example: a seeded stand-in for two real models, A a little sharper than B. A second set of 200 is the validation data. Each model's threshold turns scores into yes-or-no predictions."
  - label: "The report, and the baseline"
    lines: "28-33"
    note: "A: {A.split("(")[1].split(")")[0]} as true positives, false positives, false negatives, true negatives, giving {A.split("[")[1].rstrip("]")} for accuracy, precision, recall and F1. B: {B.split("[")[1].rstrip("]")}. The baseline that says no to everyone scores {BASELINE} on accuracy, which is why accuracy alone is never the whole story on an unbalanced class."
  - label: "How sure is A's accuracy?"
    lines: "35-38"
    note: "The accuracy is the mean of 200 zeros and ones, so the last topic applies: standard error `sqrt(p(1 - p) / n)` = {INTERVAL.split()[1]}, interval {INTERVAL.split("[")[1].rstrip("]")}. Four points either way, from 200 examples."
  - label: "A threshold chosen honestly, and not"
    lines: "40-44"
    note: "Forty-one thresholds tried. Chosen on the **validation** set, the best is {VAL_LINE.split()[0]}, and it scores {VAL_LINE.split()[1]} on the test set. Chosen on the **test** set itself, the best is {TEST_LINE.split()[0]} and scores {TEST_LINE.split()[1]}: the best of forty-one tries on those very examples, a number that flatters. That is what leakage looks like, and why choices go on validation data."
  - label: "Is A really better than B?"
    lines: "46-48"
    note: "Both models were scored on the same examples, so compare them **paired**: for each example, A's correctness minus B's. The mean difference is {DIFF_LINE.split()[0]}; bootstrapping it 2,000 times gives an interval of {DIFF_LINE.split("[")[1].rstrip("]")}, which {ZERO_PHRASE}. Comparing two separate intervals would have thrown away the pairing and the noise the two models share."
''',
)
write("exercises/example-judging-two-classifiers/solution.py", EXAMPLE)
write(
    "exercises/example-judging-two-classifiers/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints two models' reports, the baseline, an interval, two thresholds and the paired comparison."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-the-four-metrics/exercise.yaml",
    f'''id: fill-the-four-metrics
stage: fill_in
rev: 1
title: "The four metrics from four counts"
prompt: |
  `metrics(tp, fp, fn, tn)` should return accuracy, precision, recall and F1, rounded to 3 places. Precision divides the true positives by everything flagged; recall divides them by everything that was really positive. Replace each `...` so the program prints a decent classifier, one that never raises a false alarm but misses most cases, and one that flags everything:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "Everything flagged is the true positives plus the false positives."
  - "Everything really positive is the true positives plus the false negatives (the missed ones)."
skills: [metrics]
''',
)
write("exercises/fill-the-four-metrics/starter.py", FILL_STARTER)
write("exercises/fill-the-four-metrics/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-the-four-metrics/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three classifiers' metrics."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_perfect_and_a_balanced_classifier():
    """A perfect classifier scores 1 on everything; 10 true positives, 10 false positives and 30 misses give precision 0.5 and recall 0.25."""
    metrics = function("metrics")
    assert metrics(20, 0, 0, 80) == (1.0, 1.0, 1.0, 1.0)
    assert metrics(10, 10, 30, 50)[1:3] == (0.5, 0.25)
''',
)
write("exercises/fill-the-four-metrics/wrong/swapped.py", FILL_SWAPPED)
write(
    "exercises/fill-the-four-metrics/wrong/typed-in.py",
    "def metrics(tp, fp, fn, tn):\n    return (0.94, 0.8, 0.667, 0.727)\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-accuracy-interval/exercise.yaml",
    f'''id: write-accuracy-interval
stage: write
rev: 1
title: "An interval on an accuracy"
prompt: |
  Write `accuracy_interval(correct, z=1.96)`, which takes an array of 1s (right) and 0s (wrong), and returns the accuracy, the low end and the high end of its 95 percent interval, each rounded to 3 places: the standard error of an accuracy `p` on `n` examples is `sqrt(p * (1 - p) / n)`. Then print it for the starter's 200 results, for the same results repeated four times, and for 50 results that are all right:

  ```
{block(WRITE_OUT)}  ```

  Four times the data, half the width; and a perfect score on 50 examples has an interval of zero width, which is the formula's weakness on the edges, not the truth.
hints:
  - "`correct.mean()` is the accuracy."
  - "`len(correct)` is `n`; the square root covers the whole fraction."
skills: [interval]
''',
)
write("exercises/write-accuracy-interval/starter.py", WRITE_STARTER)
write("exercises/write-accuracy-interval/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-accuracy-interval/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three intervals."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_known_case():
    """An accuracy of 0.9 on 100 examples has a standard error of 0.03 and an interval of 0.841 to 0.959."""
    accuracy_interval = function("accuracy_interval")
    correct = np.array([1] * 90 + [0] * 10)
    assert accuracy_interval(correct) == (0.9, 0.841, 0.959)
''',
)
write("exercises/write-accuracy-interval/wrong/no-root.py", WRITE_NO_ROOT)
write(
    "exercises/write-accuracy-interval/wrong/typed-in.py",
    WRITE_STARTER + "\n\ndef accuracy_interval(correct, z=1.96):\n    return (1.0, 1.0, 1.0)\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -------------------------------------------------------------------------------------

write(
    "exercises/build-an-evaluation-report/exercise.yaml",
    f'''id: build-an-evaluation-report
stage: build
rev: 1
title: "An evaluation report"
prompt: |
  Starting from a blank editor, write the tools an honest evaluation needs:

  - `confusion(y, pred)`: the counts `(tp, fp, fn, tn)` as plain ints, from arrays of true labels and predictions (1s and 0s).
  - `metrics(tp, fp, fn, tn)`: accuracy, precision, recall and F1, as a tuple of floats.
  - `accuracy_interval(correct, z=1.96)`: the 95 percent interval for an accuracy from an array of 1s and 0s, as a pair of floats.
  - `paired_bootstrap(rng, correct_a, correct_b, draws=2000)`: the mean of the per-example differences `correct_a - correct_b`, and the 2.5th and 97.5th percentiles of that mean over `draws` resamples **of the differences** with replacement, as three floats.

  Then, with the data below (two models' scores on 200 held-out examples, generated from a seeded generator), print each model's confusion counts and metrics rounded to 3, the interval for A's accuracy, and the paired comparison, rounded to 3:

  ```python
{block(DATA)}  pred_a = (score_a > 1.0).astype(int)
  pred_b = (score_b > 0.6).astype(int)
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks use confusion matrices with known metrics, an accuracy with a known interval, and two identical models whose difference must come out as exactly zero.
skills: [metrics, interval, compare]
''',
)
write("exercises/build-an-evaluation-report/starter.py", "")
write("exercises/build-an-evaluation-report/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-an-evaluation-report/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints both reports, the interval and the paired comparison."""
    assert run() == {BUILD_OUT!r}


def test_confusion_and_metrics():
    """Hand-made labels give the four counts, and 8, 2, 4, 86 give accuracy 0.94, precision 0.8, recall 2/3."""
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
    """Two identical models differ by exactly zero with a zero-width interval; a model that is right where the other is wrong on a fifth of examples differs by 0.2."""
    paired_bootstrap = function("paired_bootstrap")
    rng = np.random.default_rng(0)
    correct = (rng.random(100) < 0.8).astype(int)
    assert paired_bootstrap(rng, correct, correct) == (0.0, 0.0, 0.0)
    better = correct.copy()
    better[correct == 0] = 1
    mean, low, high = paired_bootstrap(rng, better, correct)
    assert abs(mean - (1 - correct.mean())) < 1e-12 and 0 < low <= mean <= high
''',
)
write("exercises/build-an-evaluation-report/wrong/swapped.py", BUILD_SWAPPED)
write("exercises/build-an-evaluation-report/wrong/no-root.py", BUILD_NO_ROOT)
write("exercises/build-an-evaluation-report/wrong/unpaired.py", BUILD_UNPAIRED)
write(
    "exercises/build-an-evaluation-report/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def confusion(y, pred):\n    return (0, 0, 0, 0)\n\n\n"
    + "def metrics(tp, fp, fn, tn):\n    return (0.0, 0.0, 0.0, 0.0)\n\n\n"
    + "def accuracy_interval(correct, z=1.96):\n    return (0.0, 1.0)\n\n\n"
    + "def paired_bootstrap(rng, correct_a, correct_b, draws=2000):\n    return (0.0, 0.0, 0.0)\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-metrics-report/exercise.yaml",
    f'''id: debug-metrics-report
stage: debug
rev: 1
title: "A report that averages the wrong way"
prompt: |
  This program turns four counts into the four metrics and puts an interval on the accuracy, and should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the F1 comes out as 0.675, the plain average of precision and recall, where F1 is their **harmonic** mean, `2pr / (p + r)`, which punishes a low member. Fix that, and the interval is far too narrow: the standard error divides by `n` outside the square root, where the whole fraction `p(1 - p) / n` belongs **under** it.
skills: [metrics, interval]
''',
)
write("exercises/debug-metrics-report/starter.py", DEBUG_STARTER)
write("exercises/debug-metrics-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-metrics-report/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the four metrics and the interval."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_f1_and_the_interval():
    """Precision 1 and recall 0.25 give F1 0.4, not 0.625; an accuracy of 0.9 on 100 examples spans 0.841 to 0.959."""
    metrics = function("metrics")
    accuracy_interval = function("accuracy_interval")
    assert abs(metrics(10, 0, 30, 60)[3] - 0.4) < 1e-12
    low, high = accuracy_interval(0.9, 100)
    assert abs(low - 0.8412) < 0.001 and abs(high - 0.9588) < 0.001
''',
)
write("exercises/debug-metrics-report/wrong/f1-only.py", DEBUG_F1_ONLY)
write(
    "exercises/debug-metrics-report/wrong/typed-in.py",
    "import numpy as np\n\n\ndef metrics(tp, fp, fn, tn):\n    return 0.85, 0.75, 0.6, 0.667\n\n\ndef accuracy_interval(accuracy, n, z=1.96):\n    return 0.801, 0.899\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise ---------------------------------------------------------------------

write(
    "exercises/review-precision-recall/exercise.yaml",
    f'''id: review-precision-recall
stage: review_code
rev: 1
title: "Precision and recall, from memory"
prompt: |
  Write `precision_recall(tp, fp, fn)`, which returns the precision and the recall as a pair, and print it for 8 true positives, 2 false positives and 4 misses, and for 30, 0 and 70:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [metrics]
''',
)
write("exercises/review-precision-recall/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-precision-recall/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-precision-recall/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two pairs."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_counts():
    """Flagging everything gives precision below 1 and recall 1; never flagging anything correctly gives precision 0."""
    precision_recall = function("precision_recall")
    assert precision_recall(20, 80, 0) == (0.2, 1.0)
    assert precision_recall(0, 5, 10) == (0.0, 0.0)
''',
)
write(
    "exercises/review-precision-recall/wrong/swapped.py",
    '''def precision_recall(tp, fp, fn):
    return tp / (tp + fn), tp / (tp + fp)


print(precision_recall(8, 2, 4))
print(precision_recall(30, 0, 70))
''',
)
write(
    "exercises/review-precision-recall/wrong/typed-in.py",
    "def precision_recall(tp, fp, fn):\n    return (0.8, 0.6666666666666666)\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.prob.evaluating-models written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
