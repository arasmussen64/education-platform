"""Writes the topic ml.prob.sampling-and-confidence (Module 5's fifth topic).
Run from the repository root under uv (python -m uv run python <this file>),
so every program's expected output is captured from CPython rather than
typed in. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.prob.sampling-and-confidence")


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


# --- the worked example ------------------------------------------------------------------

EXAMPLE = '''import numpy as np

rng = np.random.default_rng(8)
population = rng.exponential(10, size=200000)
print(round(float(population.mean()), 2), round(float(population.std()), 2), round(float(np.median(population)), 2))

for n in (2, 10, 50):
    means = rng.exponential(10, size=(20000, n)).mean(axis=1)
    print(n, round(float(means.mean()), 2), round(float(means.std()), 2), round(10 / np.sqrt(n), 2))

means = rng.exponential(10, size=(20000, 50)).mean(axis=1)
counts, edges = np.histogram(means, bins=np.arange(5, 15.5, 1.0))
for count, left in zip(counts, edges[:-1]):
    print(f"{left:5.1f} {'#' * round(count / 200)}")

sample = rng.exponential(10, size=50)
mean = sample.mean()
se = sample.std(ddof=1) / np.sqrt(len(sample))
print(round(float(mean), 2), round(float(se), 2), round(float(mean - 1.96 * se), 2), round(float(mean + 1.96 * se), 2))

covered = 0
for trial in range(2000):
    s = rng.exponential(10, size=50)
    half = 1.96 * s.std(ddof=1) / np.sqrt(50)
    covered += abs(s.mean() - 10) < half
print(covered / 2000)

medians = np.array([np.median(rng.choice(sample, size=50)) for _ in range(2000)])
print(round(float(np.median(sample)), 2), np.round(np.percentile(medians, [2.5, 97.5]), 2))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
lines = EXAMPLE_OUT.splitlines()
pop_mean, pop_std, pop_median = (float(v) for v in lines[0].split())
assert abs(pop_mean - 10) < 0.1 and abs(pop_std - 10) < 0.1 and abs(pop_median - 6.93) < 0.1, lines[0]
SE_ROWS = {int(line.split()[0]): line.split()[1:] for line in lines[1:4]}
for n, (m, s, theory) in SE_ROWS.items():
    assert abs(float(m) - 10) < 0.15 and abs(float(s) - float(theory)) < 0.1 * float(theory), (n, m, s, theory)
HIST = lines[4:14]
assert len(HIST) == 10 and max(len(h) for h in HIST) == max(len(HIST[4]), len(HIST[5])), HIST
CI = lines[14].split()
COVERAGE = lines[15]
assert 0.90 <= float(COVERAGE) <= 0.97, COVERAGE
BOOT = lines[16]
assert "e-" not in EXAMPLE_OUT and "e+" not in EXAMPLE_OUT
assert out(EXAMPLE.replace("default_rng(8)", "default_rng(8)")) == EXAMPLE_OUT

# --- the fill-in ------------------------------------------------------------------------------

FILL_HEAD = '''import numpy as np


def standard_error(sample):
    return sample.std(ddof=1) / np.sqrt(LEN)


def confidence_interval(sample, z=1.96):
    mean = sample.mean()
    half = Z * standard_error(sample)
    return round(float(mean - half), 2), round(float(mean + half), 2)


scores = np.array([72.0, 85.0, 90.0, 66.0, 78.0, 81.0, 95.0, 70.0, 88.0, 75.0])
print(round(float(standard_error(scores)), 3))
print(confidence_interval(scores))
print(confidence_interval(np.tile(scores, 4)))
'''
FILL_SOLUTION = FILL_HEAD.replace("np.sqrt(LEN)", "np.sqrt(len(sample))").replace("half = Z *", "half = z *")
FILL_STARTER = FILL_HEAD.replace("np.sqrt(LEN)", "np.sqrt(...)").replace("half = Z *", "half = ... *")
FILL_DIVIDES_BY_N = FILL_SOLUTION.replace("    return sample.std(ddof=1) / np.sqrt(len(sample))", "    return sample.std(ddof=1) / len(sample)")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
fill_lines = FILL_OUT.splitlines()
FILL_SE = fill_lines[0]
assert len(fill_lines) == 3 and 2.9 < float(FILL_SE) < 3.1, FILL_OUT
low, high = (float(v) for v in fill_lines[1].strip("()").split(", "))
assert low < 80.0 < high and abs((high - low) - 2 * 1.96 * float(FILL_SE)) < 0.02, FILL_OUT
low4, high4 = (float(v) for v in fill_lines[2].strip("()").split(", "))
assert 0.45 < (high4 - low4) / (high - low) < 0.5, FILL_OUT  # about half: ddof=1 shifts it a little
assert out(FILL_DIVIDES_BY_N) != FILL_OUT

# --- the write -----------------------------------------------------------------------------------

WRITE_STARTER = '''import numpy as np

rng = np.random.default_rng(11)
sample = rng.exponential(10, size=40)
'''
WRITE_SOLUTION = WRITE_STARTER + '''

def bootstrap_interval(rng, sample, statistic, draws=2000):
    values = np.array([statistic(rng.choice(sample, size=len(sample))) for _ in range(draws)])
    low, high = np.percentile(values, [2.5, 97.5])
    return round(float(low), 2), round(float(high), 2)


print(round(float(np.median(sample)), 2), bootstrap_interval(rng, sample, np.median))
print(round(float(sample.mean()), 2), bootstrap_interval(rng, sample, np.mean))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
for line in WRITE_OUT.splitlines():
    value, low, high = float(line.split()[0]), float(line.split("(")[1].split(",")[0]), float(line.split(", ")[1].rstrip(")"))
    assert low < value < high, line
WRITE_NO_REPLACEMENT = WRITE_SOLUTION.replace("rng.choice(sample, size=len(sample))", "rng.choice(sample, size=len(sample), replace=False)")
assert out(WRITE_NO_REPLACEMENT) != WRITE_OUT

# --- the build -----------------------------------------------------------------------------------------

BUILD_SOLUTION = '''import numpy as np


def standard_error(sample):
    return float(sample.std(ddof=1) / np.sqrt(len(sample)))


def confidence_interval(sample, z=1.96):
    half = z * standard_error(sample)
    return float(sample.mean() - half), float(sample.mean() + half)


def coverage(rng, draw, truth, n, trials):
    hits = 0
    for trial in range(trials):
        low, high = confidence_interval(draw(rng, n))
        hits += low < truth < high
    return hits / trials


def bootstrap_interval(rng, sample, statistic, draws=2000):
    values = np.array([statistic(rng.choice(sample, size=len(sample))) for _ in range(draws)])
    low, high = np.percentile(values, [2.5, 97.5])
    return float(low), float(high)


rng = np.random.default_rng(8)
sample = rng.exponential(10, size=50)
print("standard error", round(standard_error(sample), 3))
print("interval", np.round(confidence_interval(sample), 2))
print("coverage", coverage(rng, lambda rng, n: rng.exponential(10, size=n), 10, 50, 2000))
print("median", round(float(np.median(sample)), 2), np.round(bootstrap_interval(rng, sample, np.median), 2))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
build_coverage = float(BUILD_OUT.splitlines()[2].split()[1])
assert 0.90 <= build_coverage <= 0.97, BUILD_OUT
BUILD_DIVIDES_BY_N = BUILD_SOLUTION.replace("    return float(sample.std(ddof=1) / np.sqrt(len(sample)))", "    return float(sample.std(ddof=1) / len(sample))")
BUILD_ONE_SE = BUILD_SOLUTION.replace("    half = z * standard_error(sample)", "    half = standard_error(sample)")
BUILD_NO_REPLACEMENT = BUILD_SOLUTION.replace("rng.choice(sample, size=len(sample))", "rng.choice(sample, size=len(sample), replace=False)")
for wrong in (BUILD_DIVIDES_BY_N, BUILD_ONE_SE, BUILD_NO_REPLACEMENT):
    assert out(wrong) != BUILD_OUT

# --- the debug -------------------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def interval(sample, z=1.96):
    se = sample.std(ddof=1) / np.sqrt(len(sample))
    return sample.mean() - z * se, sample.mean() + z * se


rng = np.random.default_rng(3)
sample = rng.normal(100, 15, size=36)
low, high = interval(sample)
print("interval", round(float(low), 1), round(float(high), 1))

hits = 0
for trial in range(1000):
    low, high = interval(rng.normal(100, 15, size=36))
    hits += low < 100 < high
print("coverage", hits / 1000)
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("    se = sample.std(ddof=1) / np.sqrt(len(sample))", "    se = sample.std(ddof=1) / len(sample)").replace(
    "    return sample.mean() - z * se, sample.mean() + z * se", "    return sample.mean() - se, sample.mean() + se"
)
DEBUG_ROOT_ONLY = DEBUG_SOLUTION.replace("    return sample.mean() - z * se, sample.mean() + z * se", "    return sample.mean() - se, sample.mean() + se")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER) + "--- one bug left prints:\n" + out(DEBUG_ROOT_ONLY))
debug_coverage = float(DEBUG_OUT.splitlines()[1].split()[1])
assert 0.92 <= debug_coverage <= 0.98, DEBUG_OUT
one_left = float(out(DEBUG_ROOT_ONLY).splitlines()[1].split()[1])
assert 0.6 <= one_left <= 0.75, one_left
buggy = float(out(DEBUG_STARTER).splitlines()[1].split()[1])
assert buggy < 0.3, buggy

# --- predict items ------------------------------------------------------------------------------------------

PREDICT_SE = '''import numpy as np

sigma = 10
for n in (4, 25, 100, 400):
    print(n, sigma / np.sqrt(n))
'''
PREDICT_SE_OUT = out(PREDICT_SE)
print("predict se:\n" + PREDICT_SE_OUT)
assert PREDICT_SE_OUT == "4 5.0\n25 2.0\n100 1.0\n400 0.5\n", PREDICT_SE_OUT

REVIEW_WIDTH = '''import numpy as np

se = 2.0
for z in (1.0, 1.96, 2.58):
    print(z, round(2 * z * se, 2))
print(round(1.96 * 2.0 / np.sqrt(4), 2))
'''
REVIEW_WIDTH_OUT = out(REVIEW_WIDTH)
print("review width:\n" + REVIEW_WIDTH_OUT)
assert REVIEW_WIDTH_OUT == "1.0 4.0\n1.96 7.84\n2.58 10.32\n1.96\n", REVIEW_WIDTH_OUT

REVIEW_CODE_STARTER = '''import numpy as np

scores = np.array([72.0, 85.0, 90.0, 66.0, 78.0, 81.0, 95.0, 70.0, 88.0, 75.0])
'''
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def standard_error(sample):
    return float(sample.std(ddof=1) / np.sqrt(len(sample)))


print(round(standard_error(scores), 3))
print(round(standard_error(np.tile(scores, 4)), 3))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT.splitlines()[0] == FILL_SE, (REVIEW_CODE_OUT, FILL_SE)

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.prob.sampling-and-confidence
kind: topic
status: ready
title: "Sampling and confidence"
summary: "The sampling distribution of a mean, the standard error, the central limit theorem seen by simulation, confidence intervals, and the bootstrap."
prerequisites: [ml.prob.expectation-and-variance]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Simulate many samples and watch their means form a normal shape, whatever the population looks like."
  - "Compute a standard error, and say what shrinks it."
  - "Build a confidence interval for a mean, and say what it does and doesn't promise."
  - "Bootstrap an interval for a statistic that has no formula."
# Linked, never copied or embedded: 3Blue1Brown's and StatQuest's videos are
# under the standard YouTube licence; OpenStax is CC BY 4.0.
resources:
  - title: "3Blue1Brown: Probability (Grant Sanderson), the lesson But what is the Central Limit Theorem?"
    url: https://www.3blue1brown.com/topics/probability
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "OpenStax Introductory Statistics 2e: chapter 7 (The Central Limit Theorem, sections 7.1 and 7.2) and section 8.1 (A Single Population Mean Using the Normal Distribution)"
    url: https://openstax.org/details/books/introductory-statistics-2e
    type: reading
    use: link
    license: CC BY 4.0
  - title: "StatQuest: Bootstrapping Main Ideas!!! (Josh Starmer)"
    url: https://www.youtube.com/watch?v=Xz0x-8-cgaQ
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
practice:
  - example-the-means-of-many-samples
  - parsons-an-interval-from-a-sample
  - mcq-what-shrinks-the-standard-error
  - predict-standard-errors
  - mcq-what-ninety-five-percent-promises
  - mcq-why-a-normal-for-an-average
  - fill-standard-error-and-interval
  - write-bootstrap-interval
prove:
  build: build-intervals-and-coverage
  debug: debug-an-interval-that-is-too-narrow
  explain:
    prompt: |
      A teammate measured a model's accuracy at 0.84 on 100 held-out examples and reports "84 percent accurate". In your own words: why is that number uncertain, and what is its standard error? What interval would you put around it, and what does "95 percent confidence" promise, and not promise? Why does the central limit theorem let you use a normal for the average even though each example scores a 0 or a 1? And when would you reach for the bootstrap instead?
    rubric:
      - id: standard-error
        required: true
        description: "The 0.84 is one sample's mean; another 100 examples would give a different one. Its spread over repeated samples is the standard error, the population spread over root n: for a proportion, sqrt(0.84 * 0.16 / 100), about 0.037; four times the data would halve it."
      - id: interval
        required: true
        description: "About 0.84 plus or minus 1.96 standard errors, roughly 0.77 to 0.91. Ninety-five percent confidence means the procedure (sample, compute the interval) captures the true accuracy in about 95 of 100 repetitions; it doesn't mean 95 percent of examples are inside, or that this one interval has a 95 percent chance in any simple sense, or that the true value is near the middle."
      - id: clt
        required: true
        description: "The average of many independent draws is approximately normal whatever each draw's distribution, with mean the population mean and spread sigma over root n; each 0-or-1 score is far from normal, but the mean of 100 of them is close enough, which is why the normal's 1.96 applies."
      - id: bootstrap
        required: false
        description: "When the statistic has no standard-error formula (a median, an F1 score, the difference between two models): resample the data with replacement many times, recompute the statistic each time, and take the middle 95 percent of the results."
    model_answer: |
      The 0.84 is the mean of one sample of 100 scores, and a different 100 examples would give a different mean, so the number carries uncertainty from the sampling itself. How much it would vary across repeated samples is its standard error: the population spread divided by the square root of the sample size. For a proportion the spread is the square root of p times one minus p, so the standard error is the square root of 0.84 times 0.16 over 100, about 0.037. Four hundred examples would halve it; the square root is why more data helps slowly. The 95 percent interval is the estimate plus or minus 1.96 standard errors, about 0.77 to 0.91. What 95 percent confidence promises is about the procedure: if you took many samples of 100 and built an interval from each, about 95 of every 100 intervals would contain the model's true accuracy. It doesn't say 95 percent of the examples fall in the interval, and it doesn't make the true value likelier near the middle than near the edges. The central limit theorem is what lets me use a normal at all. Each example scores a 0 or a 1, nothing like a bell curve, but the average of a hundred independent scores is close to normal with mean equal to the true accuracy and spread equal to the standard error, and that's where the 1.96 comes from. When the statistic has no standard-error formula, a median, an F1 score, or the difference in accuracy between two models on the same examples, I'd bootstrap: resample the hundred examples with replacement a couple of thousand times, recompute the statistic each time, and take the 2.5th and 97.5th percentiles of the results as the interval.
review_pool:
  - review-predict-interval-widths
  - review-mcq-what-becomes-normal
  - review-mcq-with-replacement
  - review-standard-error
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: clt
    description: "Simulate the sampling distribution of a mean and say what the central limit theorem promises"
  - id: standard-error
    description: "Compute a standard error and say what shrinks it"
  - id: interval
    description: "Build a confidence interval for a mean and say what 95 percent confidence does and doesn't promise"
  - id: bootstrap
    description: "Bootstrap an interval for a statistic that has no formula"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Every number a model is judged by (an accuracy, a mean error, a median latency) is computed from a **sample**, and a different sample would give a different number. This topic is about how different: the spread of a statistic over repeated samples, called its **standard error**; the surprising fact that averages are nearly normal whatever the data looks like, the **central limit theorem**; the **confidence interval** that turns a standard error into a range with a promise attached; and the **bootstrap**, which gets an interval for any statistic by resampling. All of it is watched in simulation, with a deliberately lopsided population.

The main resource is **3Blue1Brown's _But what is the Central Limit Theorem?_**, 30 minutes that build the bell curve out of a Galton board; OpenStax _Introductory Statistics 2e_ chapter 7 and section 8.1 have the standard error and the interval as text; and StatQuest's _Bootstrapping Main Ideas_ is ten minutes on resampling. Watch for:

- **The sampling distribution:** not the data's shape, but the shape of a statistic over many samples.
- **`σ / sqrt(n)`:** the average of `n` draws is less spread than one draw, by the square root.
- **What "95 percent" is a property of:** the procedure, repeated.

</Intro>

<Resource index={{0}} />

<Recap>

- **Population and sample.** The population is everything you could have measured; the sample is what you did. A **statistic** (a mean, a median) computed from a sample is a random variable: draw a different sample and it changes. Its distribution over repeated samples is its **sampling distribution**.
- **The worked example's population is lopsided on purpose:** exponential waiting times with mean 10, spread 10 and median {pop_median}, nothing like a bell. The means of 20,000 samples of size 2, 10 and 50 all average 10, and their spreads are {SE_ROWS[2][1]}, {SE_ROWS[10][1]} and {SE_ROWS[50][1]}: the population's spread divided by `sqrt(n)` ({SE_ROWS[2][2]}, {SE_ROWS[10][2]}, {SE_ROWS[50][2]}).
- **The standard error** of a mean is that spread, `σ / sqrt(n)`. From one sample it's estimated as `sample.std(ddof=1) / sqrt(n)`: the sample's standard deviation with `n - 1` (the convention when a sample stands in for the population it came from; the last topic's `n` was the maximum-likelihood fit to the sample itself). Four times the data halves it; a less variable population shrinks it too.
- **The central limit theorem:** the mean of `n` independent draws is approximately normal, with mean the population's mean and spread `σ / sqrt(n)`, **whatever the population's shape**, once `n` is moderately large. The histogram of means of 50 lopsided draws is a bell centred on 10. That's why the normal's numbers (1.96 for 95 percent) apply to averages of anything, including a model's 0-or-1 scores.
- **A confidence interval** for a mean: `mean ± 1.96 * standard error`. The worked example's sample of 50 gave {CI[0]} with standard error {CI[1]}, so the interval {CI[2]} to {CI[3]}. The 1.96 is the normal's 95 percent width; 2.58 gives 99 percent, 1 gives 68.
- **What 95 percent promises:** repeat the whole procedure (draw a sample, compute the interval) many times, and about 95 percent of the intervals contain the true mean. In the worked example, 2,000 repetitions covered the true mean of 10 a fraction {COVERAGE} of the time (a little under 0.95: the population is lopsided and 50 is not huge). It does **not** mean that 95 percent of the data lies in the interval, nor that the true value is likelier near the middle.
- **The bootstrap** gets an interval for a statistic with no formula (a median, an F1 score, a difference between two models): resample the sample **with replacement** to the same size, recompute the statistic, repeat a couple of thousand times, and take the 2.5th and 97.5th percentiles. The sample's median was {BOOT.split()[0]}, with a bootstrap interval of {BOOT.split("[")[1].rstrip("]")}. Resampling without replacement would give the same sample back every time and an interval of zero width.
- **In machine learning:** an accuracy on 100 examples has a standard error near 0.04, so two models 2 points apart are not yet distinguishable; held-out loss curves wiggle for the same reason; and every metric a paper reports without an interval is a sample mean reported without its standard error. The evaluation topic builds on this.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-an-interval-from-a-sample.yaml",
    '''id: parsons-an-interval-from-a-sample
type: parsons
rev: 1
prompt: |
  Put the lines in order to print a 95 percent confidence interval for the mean of a sample of 25 values with mean 50 and sample standard deviation 10, `(46.08, 53.92)`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'mean, sd, n = 50.0, 10.0, 25'
  - 'se = sd / np.sqrt(n)'
  - 'print((round(mean - 1.96 * se, 2), round(mean + 1.96 * se, 2)))'
distractors:
  - 'se = sd / n'
explanation: |
  The standard error divides the sample's spread by the **square root** of the sample size: `10 / 5 = 2`, so the interval is `50 ± 1.96 * 2`. The decoy divides by `n` itself, giving 0.4, an interval five times too narrow, which would make the estimate look far more certain than it is.
skills: [standard-error, interval]
''',
)

write(
    "recall/mcq-what-shrinks-the-standard-error.yaml",
    '''id: mcq-what-shrinks-the-standard-error
type: mcq
rev: 1
prompt: |
  A mean computed from 100 measurements has a standard error of 2. How many measurements would bring it down to 1?
choices:
  - '200: twice the data, half the error'
  - '400: the standard error shrinks with the square root of the sample size, so halving it takes four times the data'
  - '101: one more measurement is enough once you have 100'
  - 'It can''t be brought down; the standard error depends only on the population'
answer: 1
explanation: |
  The standard error is `σ / sqrt(n)`, so it falls with the square root of `n`: 200 measurements give `2 / sqrt(2) = 1.41`, and 400 give 1. More data helps, slowly. The other lever is a less variable population, which is why careful measurement beats more measurement when both are possible.
skills: [standard-error]
''',
)

write(
    "recall/predict-standard-errors.yaml",
    f'''id: predict-standard-errors
type: predict_output
rev: 1
prompt: |
  The standard error of a mean for a population with spread 10, at four sample sizes. What does the program print?
code: |
{block(PREDICT_SE)}expected_output: |
{block(PREDICT_SE_OUT)}explanation: |
  `10 / sqrt(4) = 5`, then 2, 1 and 0.5: each time the sample is four times larger, the standard error halves. Going from 4 to 400 measurements, a hundred times the data, buys a factor of ten.
skills: [standard-error]
''',
)

write(
    "recall/mcq-what-ninety-five-percent-promises.yaml",
    '''id: mcq-what-ninety-five-percent-promises
type: mcq
rev: 1
prompt: |
  A 95 percent confidence interval for a model''s mean error is 1.2 to 1.8. Which statement is what the 95 percent promises?
choices:
  - '95 percent of the individual errors lie between 1.2 and 1.8'
  - 'The sample mean has a 95 percent chance of lying in the interval'
  - 'A larger sample would give a wider interval, since there would be more data to cover'
  - 'If you repeated the sampling many times and built an interval each time, about 95 percent of those intervals would contain the true mean error'
answer: 3
explanation: |
  Confidence is a property of the procedure, checked in the worked example by repeating it 2,000 times and counting. The individual errors are far more spread than the interval for their mean; the sample mean is always exactly in the middle, so it''s a certainty, not a 95 percent chance; and a larger sample narrows the interval, because the standard error shrinks.
skills: [interval]
''',
)

write(
    "recall/mcq-why-a-normal-for-an-average.yaml",
    '''id: mcq-why-a-normal-for-an-average
type: mcq
rev: 1
prompt: |
  Each held-out example scores a 0 (wrong) or a 1 (right), nothing like a bell curve. Why can you still use the normal's 1.96 to put an interval around the model's accuracy on 100 examples?
choices:
  - 'Because 0s and 1s are symmetric around a half'
  - 'You can''t; intervals need normal data'
  - 'Because the central limit theorem says the mean of many independent draws is approximately normal, with spread `σ / sqrt(n)`, whatever each draw''s distribution is; the accuracy is a mean of 100 draws'
  - 'Because 100 is more than 30, and any sample larger than 30 is normal'
answer: 2
explanation: |
  The theorem is about the average, not the data. Each score is a Bernoulli draw, and the mean of 100 of them is close to a normal centred on the true accuracy with spread `sqrt(p(1 - p) / 100)`, which is why the interval formula applies. The data never becomes normal, and 30 is a rule of thumb for when the approximation is usually good enough, not a law.
skills: [clt]
''',
)

write(
    "recall/review-predict-interval-widths.yaml",
    f'''id: review-predict-interval-widths
type: predict_output
rev: 1
prompt: |
  The width of an interval at three confidence levels, then a standard error after quadrupling the sample. What does the program print?
code: |
{block(REVIEW_WIDTH)}expected_output: |
{block(REVIEW_WIDTH_OUT)}explanation: |
  An interval runs `z` standard errors each side of the mean, so its width is `2 * z * se`: 1 standard error each way is the normal''s 68 percent, 1.96 is 95 percent and 2.58 is 99 percent; more confidence costs width. The last line halves the standard error by quadrupling the sample.
skills: [interval, standard-error]
''',
)

write(
    "recall/review-mcq-what-becomes-normal.yaml",
    '''id: review-mcq-what-becomes-normal
type: mcq
rev: 1
prompt: |
  Waiting times at a counter are lopsided: most are short, a few are very long. You take many samples of 50 waits and compute each sample''s mean. What does the central limit theorem say?
choices:
  - 'The waiting times themselves become normal once you have enough of them'
  - 'The sample means are approximately normal around the true mean, with spread `σ / sqrt(50)`, even though the waits are lopsided'
  - 'Nothing, because the theorem needs a normal population to start from'
  - 'The sample medians are normal but the sample means are not'
answer: 1
explanation: |
  The theorem is about averages, not about the data: the population keeps its lopsided shape however much of it you collect, while the means of samples of 50 pile up in a bell centred on the true mean. That''s why one interval formula serves waiting times, 0-or-1 accuracies and everything else, once the sample is moderately large.
skills: [clt]
''',
)

write(
    "recall/review-mcq-with-replacement.yaml",
    '''id: review-mcq-with-replacement
type: mcq
rev: 1
prompt: |
  To bootstrap an interval for a sample''s median, you resample the sample 2,000 times. Why must the resampling be **with replacement**, to the same size as the sample?
choices:
  - 'Because without replacement every resample would be the whole sample in a different order, the median would never change, and the interval would have zero width'
  - 'Because with replacement is faster'
  - 'Because the median only exists for resamples that repeat values'
  - 'It needn''t be; sampling a smaller subset without replacement works the same'
answer: 0
explanation: |
  The bootstrap pretends the sample is the population and draws new samples from it; drawing with replacement means some values appear twice and some not at all, which is what makes each resample different and lets the spread of the recomputed statistic stand in for its real sampling spread. A smaller subset without replacement would give a spread that''s too large.
skills: [bootstrap]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-the-means-of-many-samples/exercise.yaml",
    f'''id: example-the-means-of-many-samples
stage: worked_example
rev: 1
title: "The means of many samples"
prompt: |
  This program draws from a lopsided population, watches the means of many samples turn into a bell with a spread that shrinks like one over the square root of the sample size, builds a confidence interval and checks how often the procedure covers the truth, and bootstraps an interval for a median. Press **Run**, then read how each part works.
steps:
  - label: "A lopsided population"
    lines: "3-5"
    note: "Exponential waiting times: mean 10, spread 10, and a median of {pop_median}, well below the mean because a few waits are very long. Nothing about it is normal."
  - label: "Means of samples of 2, 10 and 50"
    lines: "7-9"
    note: "Twenty thousand samples of each size, and the mean of each. The means average 10 whatever the size, but their spread falls: {SE_ROWS[2][1]}, {SE_ROWS[10][1]}, {SE_ROWS[50][1]}, matching `10 / sqrt(n)` ({SE_ROWS[2][2]}, {SE_ROWS[10][2]}, {SE_ROWS[50][2]}). That spread is the **standard error** of the mean."
  - label: "The central limit theorem, drawn"
    lines: "11-14"
    note: "A histogram of the means of 50 draws: a bell centred on 10, from a population that was anything but. Averages of enough independent draws are approximately normal whatever the draws look like."
  - label: "One sample, one interval"
    lines: "16-19"
    note: "Fifty waits, mean {CI[0]}. The standard error is estimated from the sample itself, its standard deviation (with `ddof=1`, dividing by `n - 1`) over `sqrt(50)`: {CI[1]}. The 95 percent interval is 1.96 standard errors each side: {CI[2]} to {CI[3]}, which here contains the true 10."
  - label: "What 95 percent means"
    lines: "21-26"
    note: "Repeat the whole procedure 2,000 times and count how often the interval contains the true mean: {COVERAGE}. A little under 0.95, because the population is lopsided and 50 is not huge, but that fraction is what the confidence level is a claim about: the procedure, not any one interval."
  - label: "A bootstrap interval for the median"
    lines: "28-29"
    note: "There's no simple standard-error formula for a median, so resample the 50 waits **with replacement** 2,000 times, take each resample's median, and read off the 2.5th and 97.5th percentiles: {BOOT.split()[0]} with an interval of {BOOT.split("[")[1].rstrip("]")}. The same recipe gives an interval for any statistic you can compute."
''',
)
write("exercises/example-the-means-of-many-samples/solution.py", EXAMPLE)
write(
    "exercises/example-the-means-of-many-samples/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the population, three standard errors, a histogram of means, an interval, its coverage and a bootstrap interval."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-standard-error-and-interval/exercise.yaml",
    f'''id: fill-standard-error-and-interval
stage: fill_in
rev: 1
title: "A standard error and an interval"
prompt: |
  `standard_error(sample)` should divide the sample's standard deviation (with `ddof=1`) by the square root of the sample size, and `confidence_interval` should reach `z` standard errors each side of the mean. Replace each `...` so the program prints the standard error of ten test scores, their 95 percent interval, and the interval for the same scores repeated four times:

  ```
{block(FILL_OUT)}  ```

  Four times the data, about half the width. The program fails until every `...` is replaced.
hints:
  - "The sample size is `len(sample)`, and it goes under a square root."
  - "The half-width is `z` times the standard error."
skills: [standard-error, interval]
''',
)
write("exercises/fill-standard-error-and-interval/starter.py", FILL_STARTER)
write("exercises/fill-standard-error-and-interval/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-standard-error-and-interval/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the standard error and the two intervals."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_known_values():
    """[2, 4, 4, 4, 5, 5, 7, 9] has sample standard deviation 2.138 and standard error 0.756; z = 1 gives an interval one standard error wide each way."""
    standard_error = function("standard_error")
    confidence_interval = function("confidence_interval")
    sample = np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert abs(standard_error(sample) - 0.756) < 0.001
    low, high = confidence_interval(sample, z=1)
    assert abs(low - 4.24) < 0.01 and abs(high - 5.76) < 0.01
''',
)
write("exercises/fill-standard-error-and-interval/wrong/divides-by-n.py", FILL_DIVIDES_BY_N)
write(
    "exercises/fill-standard-error-and-interval/wrong/typed-in.py",
    "import numpy as np\n\n\ndef standard_error(sample):\n    return 2.957\n\n\ndef confidence_interval(sample, z=1.96):\n    return (74.2, 85.8)\n\n\n"
    + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-bootstrap-interval/exercise.yaml",
    f'''id: write-bootstrap-interval
stage: write
rev: 1
title: "A bootstrap interval"
prompt: |
  Write `bootstrap_interval(rng, sample, statistic, draws=2000)`, which resamples `sample` with replacement to its own size `draws` times using `rng.choice`, applies `statistic` to each resample, and returns the 2.5th and 97.5th percentiles of the results (`np.percentile`) as a pair of floats rounded to 2 places. Then print the starter sample's median with its bootstrap interval, and its mean with its bootstrap interval:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`rng.choice(sample, size=len(sample))` resamples with replacement by default."
  - "Build the array of 2,000 statistics first, then take both percentiles in one call: `np.percentile(values, [2.5, 97.5])`."
skills: [bootstrap]
''',
)
write("exercises/write-bootstrap-interval/starter.py", WRITE_STARTER)
write("exercises/write-bootstrap-interval/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-bootstrap-interval/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the median and the mean, each with a bootstrap interval."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_properties():
    """The interval brackets the statistic, has positive width, and a constant sample gives a zero-width interval at the constant."""
    bootstrap_interval = function("bootstrap_interval")
    rng = np.random.default_rng(0)
    sample = rng.normal(50, 5, size=30)
    low, high = bootstrap_interval(rng, sample, np.mean)
    assert low < sample.mean() < high and high - low > 1
    assert bootstrap_interval(rng, np.full(10, 7.0), np.median) == (7.0, 7.0)
''',
)
write("exercises/write-bootstrap-interval/wrong/without-replacement.py", WRITE_NO_REPLACEMENT)
write(
    "exercises/write-bootstrap-interval/wrong/typed-in.py",
    WRITE_STARTER + "\n\ndef bootstrap_interval(rng, sample, statistic, draws=2000):\n    return (0.0, 0.0)\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -------------------------------------------------------------------------------------------

write(
    "exercises/build-intervals-and-coverage/exercise.yaml",
    f'''id: build-intervals-and-coverage
stage: build
rev: 1
title: "Intervals, and how often they're right"
prompt: |
  Starting from a blank editor, write the tools that put an honest range around a sample statistic:

  - `standard_error(sample)`: the sample's standard deviation with `ddof=1` over the square root of its size, as a float.
  - `confidence_interval(sample, z=1.96)`: the mean minus and plus `z` standard errors, as a pair of floats.
  - `coverage(rng, draw, truth, n, trials)`: `draw(rng, n)` returns a fresh sample of size `n`; build the 95 percent interval for each of `trials` samples and return the fraction of intervals that contain `truth` (strictly inside).
  - `bootstrap_interval(rng, sample, statistic, draws=2000)`: resample with replacement to the sample's size `draws` times, apply `statistic`, and return the 2.5th and 97.5th percentiles as a pair of floats.

  Then, with `rng = np.random.default_rng(8)` and a sample of 50 exponential waits with mean 10 (`rng.exponential(10, size=50)`), print the standard error rounded to 3, the interval rounded to 2, the coverage over 2,000 fresh samples of 50 from the same population (`lambda rng, n: rng.exponential(10, size=n)`, truth 10), and the sample's median with its bootstrap interval rounded to 2:

  ```
{block(BUILD_OUT)}  ```

  The checks use samples with known standard errors, a normal population whose coverage must come out near 0.95, and a constant sample.
skills: [standard-error, interval, clt, bootstrap]
''',
)
write("exercises/build-intervals-and-coverage/starter.py", "")
write("exercises/build-intervals-and-coverage/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-intervals-and-coverage/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the standard error, the interval, the coverage and the bootstrap interval."""
    assert run() == {BUILD_OUT!r}


def test_standard_error_and_interval():
    """[2, 4, 4, 4, 5, 5, 7, 9] has standard error 0.756; its z = 2 interval is the mean plus or minus 1.512."""
    standard_error = function("standard_error")
    confidence_interval = function("confidence_interval")
    sample = np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert abs(standard_error(sample) - 0.756) < 0.001
    low, high = confidence_interval(sample, z=2)
    assert abs(low - (5 - 1.512)) < 0.002 and abs(high - (5 + 1.512)) < 0.002


def test_coverage_of_a_normal_population():
    """For samples of 30 from a normal, the 95 percent interval covers the true mean between 92 and 98 percent of the time."""
    coverage = function("coverage")
    rng = np.random.default_rng(1)
    fraction = coverage(rng, lambda rng, n: rng.normal(5, 2, size=n), 5, 30, 1000)
    assert 0.92 <= fraction <= 0.98


def test_bootstrap():
    """A constant sample gives a zero-width interval; a spread-out one brackets its mean."""
    bootstrap_interval = function("bootstrap_interval")
    rng = np.random.default_rng(2)
    assert bootstrap_interval(rng, np.full(12, 3.0), np.mean) == (3.0, 3.0)
    sample = rng.normal(0, 1, size=40)
    low, high = bootstrap_interval(rng, sample, np.mean)
    assert low < sample.mean() < high
''',
)
write("exercises/build-intervals-and-coverage/wrong/divides-by-n.py", BUILD_DIVIDES_BY_N)
write("exercises/build-intervals-and-coverage/wrong/one-standard-error.py", BUILD_ONE_SE)
write("exercises/build-intervals-and-coverage/wrong/without-replacement.py", BUILD_NO_REPLACEMENT)
write(
    "exercises/build-intervals-and-coverage/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def standard_error(sample):\n    return 1.0\n\n\n"
    + "def confidence_interval(sample, z=1.96):\n    return (8.0, 12.0)\n\n\n"
    + "def coverage(rng, draw, truth, n, trials):\n    return 0.95\n\n\n"
    + "def bootstrap_interval(rng, sample, statistic, draws=2000):\n    return (5.0, 9.0)\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-an-interval-that-is-too-narrow/exercise.yaml",
    f'''id: debug-an-interval-that-is-too-narrow
stage: debug
rev: 1
title: "An interval that is far too sure of itself"
prompt: |
  This program builds a 95 percent interval for the mean of 36 scores from a population with mean 100 and spread 15, then checks the procedure's coverage over 1,000 fresh samples. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the coverage is tiny, because the standard error divides by `n` instead of its **square root**, making the interval six times too narrow. Fix that, and the coverage lands near 0.68 rather than 0.95: the interval reaches one standard error each side, where 95 percent needs `z = 1.96` of them.
skills: [standard-error, interval]
''',
)
write("exercises/debug-an-interval-that-is-too-narrow/starter.py", DEBUG_STARTER)
write("exercises/debug-an-interval-that-is-too-narrow/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-an-interval-that-is-too-narrow/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the interval and the coverage."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_interval_on_a_known_sample():
    """For [2, 4, 4, 4, 5, 5, 7, 9] the interval is 5 plus or minus 1.96 times 0.756."""
    interval = function("interval")
    low, high = interval(np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]))
    assert abs(low - (5 - 1.96 * 0.756)) < 0.002 and abs(high - (5 + 1.96 * 0.756)) < 0.002
''',
)
write("exercises/debug-an-interval-that-is-too-narrow/wrong/root-only.py", DEBUG_ROOT_ONLY)
write(
    "exercises/debug-an-interval-that-is-too-narrow/wrong/typed-in.py",
    "import numpy as np\n\n\ndef interval(sample, z=1.96):\n    return 95.0, 105.0\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise -------------------------------------------------------------------------

write(
    "exercises/review-standard-error/exercise.yaml",
    f'''id: review-standard-error
stage: review_code
rev: 1
title: "A standard error, from memory"
prompt: |
  Write `standard_error(sample)`, the sample's standard deviation with `ddof=1` over the square root of its size, as a float, and print it rounded to 3 places for the starter's ten scores and for the same scores repeated four times:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [standard-error]
''',
)
write("exercises/review-standard-error/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-standard-error/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-standard-error/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the two standard errors."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_a_known_sample():
    """[2, 4, 4, 4, 5, 5, 7, 9] has standard error 0.756."""
    standard_error = function("standard_error")
    assert abs(standard_error(np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])) - 0.756) < 0.001
''',
)
write(
    "exercises/review-standard-error/wrong/population-sd.py",
    REVIEW_CODE_STARTER + '''

def standard_error(sample):
    return float(sample.std() / np.sqrt(len(sample)))


print(round(standard_error(scores), 3))
print(round(standard_error(np.tile(scores, 4)), 3))
''',
)
write(
    "exercises/review-standard-error/wrong/typed-in.py",
    REVIEW_CODE_STARTER + "\n\ndef standard_error(sample):\n    return 2.957\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.prob.sampling-and-confidence written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
