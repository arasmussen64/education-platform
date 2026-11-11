"""Writes the topic ml.prob.expectation-and-variance (Module 5's second
topic). Run from the repository root under uv (python -m uv run python
<this file>), so every program's expected output is captured from CPython
rather than typed in. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.prob.expectation-and-variance")


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

faces = np.arange(1, 7)
p = np.full(6, 1 / 6)
mean = (faces * p).sum()
variance = ((faces - mean) ** 2 * p).sum()
print(mean, round(float(variance), 4), round(float(np.sqrt(variance)), 3))

rng = np.random.default_rng(2)
rolls = rng.integers(1, 7, size=100000)
print(round(float(rolls.mean()), 3), round(float(rolls.var()), 3))
for n in (10, 100, 1000, 10000, 100000):
    print(n, round(float(rolls[:n].mean()), 3))

two_dice = rolls[:50000] + rolls[50000:]
print(round(float(two_dice.mean()), 3), round(float(two_dice.var()), 3))
one_die_doubled = 2 * rolls
print(round(float(one_die_doubled.mean()), 3), round(float(one_die_doubled.var()), 3))

heights = rng.normal(170, 10, size=5)
print(np.round(heights, 1))
print(np.round((heights - 170) / 10, 2))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
lines = EXAMPLE_OUT.splitlines()
assert lines[0] == "3.5 2.9167 1.708", EXAMPLE_OUT
assert abs(float(lines[1].split()[0]) - 3.5) < 0.01 and abs(float(lines[1].split()[1]) - 2.917) < 0.03, lines[1]
assert abs(float(lines[-4].split()[1]) - 5.83) < 0.06 and abs(float(lines[-3].split()[1]) - 11.67) < 0.1, EXAMPLE_OUT
assert "e-" not in EXAMPLE_OUT and "e+" not in EXAMPLE_OUT
RUNNING = {int(line.split()[0]): line.split()[1] for line in lines[2:7]}
TWO_DICE = lines[-4].split()
DOUBLED = lines[-3].split()
SAMPLE_VAR = lines[1].split()[1]

# --- the fill-in -----------------------------------------------------------------------

FILL_HEAD = '''import numpy as np


def expectation(values, probs):
    return (values * PROBS).sum()


def variance(values, probs):
    mu = expectation(values, probs)
    return ((values - mu) ** POWER * probs).sum()


die = np.arange(1, 7)
fair = np.full(6, 1 / 6)
print(expectation(die, fair), round(float(variance(die, fair)), 4))
coin = np.array([0.0, 1.0])
print(expectation(coin, np.array([0.7, 0.3])), round(float(variance(coin, np.array([0.7, 0.3]))), 4))
loaded = np.array([0.5, 0.1, 0.1, 0.1, 0.1, 0.1])
print(round(float(expectation(die, loaded)), 4), round(float(variance(die, loaded)), 4))
'''
FILL_SOLUTION = FILL_HEAD.replace("PROBS", "probs").replace("POWER", "2")
FILL_STARTER = FILL_HEAD.replace("PROBS", "...").replace("POWER", "...")
FILL_NO_SQUARE = FILL_SOLUTION.replace("((values - mu) ** 2 * probs)", "((values - mu) * probs)")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT == "3.5 2.9167\n0.3 0.21\n2.5 3.25\n", FILL_OUT
assert out(FILL_NO_SQUARE) != FILL_OUT

# --- the write -----------------------------------------------------------------------------

WRITE_STARTER = "import numpy as np\n"
WRITE_SOLUTION = WRITE_STARTER + '''

def standardize(x, mean, sd):
    return (x - mean) / sd


print(standardize(75, 60, 10), standardize(80, 70, 20))
print(np.round(standardize(np.array([150.0, 170.0, 195.0]), 170, 10), 1))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT == "1.5 0.5\n[-2.   0.   2.5]\n", WRITE_OUT

# --- the build --------------------------------------------------------------------------------

BUILD_SOLUTION = '''import math

import numpy as np


def moments(values, probs):
    mean = float((values * probs).sum())
    variance = float(((values - mean) ** 2 * probs).sum())
    return mean, variance


def sum_of_independent(means, variances):
    return float(sum(means)), float(sum(variances))


def running_means(sample):
    return np.cumsum(sample) / np.arange(1, len(sample) + 1)


def standardize(x, mean, sd):
    return (x - mean) / sd


die = np.arange(1, 7)
fair = np.full(6, 1 / 6)
mean, variance = moments(die, fair)
print("one die", mean, round(variance, 4))
total_mean, total_variance = sum_of_independent([mean] * 10, [variance] * 10)
print("ten dice", total_mean, round(total_variance, 4))
rng = np.random.default_rng(2)
means = running_means(rng.integers(1, 7, size=10000))
print("running", np.round(means[[9, 99, 999, 9999]], 3))
print("z", standardize(np.array([160.0, 190.0]), 170, 10))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT.startswith("one die 3.5 2.9167\nten dice 35.0 29.1667\nrunning [") and BUILD_OUT.endswith("z [-1.  2.]\n"), BUILD_OUT
BUILD_NO_SQUARE = BUILD_SOLUTION.replace("((values - mean) ** 2 * probs)", "(np.abs(values - mean) * probs)")
BUILD_SD_ADDS = BUILD_SOLUTION.replace("    return float(sum(means)), float(sum(variances))", "    return float(sum(means)), float(sum(math.sqrt(v) for v in variances) ** 2)")
BUILD_NOT_RUNNING = BUILD_SOLUTION.replace("    return np.cumsum(sample) / np.arange(1, len(sample) + 1)", "    return np.cumsum(sample) / len(sample)")
for wrong in (BUILD_NO_SQUARE, BUILD_SD_ADDS, BUILD_NOT_RUNNING):
    assert out(wrong) != BUILD_OUT

# --- the debug -----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def summary(values, probs):
    mean = (values * probs).sum()
    variance = ((values - mean) ** 2 * probs).sum()
    sd = np.sqrt(variance)
    return float(mean), float(variance), float(sd)


die = np.arange(1, 7)
mean, variance, sd = summary(die, np.full(6, 1 / 6))
print("die", mean, round(variance, 4), round(sd, 3))
prize = np.array([0.0, 10.0, 100.0])
mean, variance, sd = summary(prize, np.array([0.89, 0.1, 0.01]))
print("prize", mean, round(variance, 2), round(sd, 3))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("    variance = ((values - mean) ** 2 * probs).sum()", "    variance = ((values - mean) * probs).sum()").replace(
    "    sd = np.sqrt(variance)", "    sd = variance / 2"
)
DEBUG_SQUARE_ONLY = DEBUG_SOLUTION.replace("    sd = np.sqrt(variance)", "    sd = variance / 2")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == "die 3.5 2.9167 1.708\nprize 2.0 106.0 10.296\n", DEBUG_OUT
assert out(DEBUG_SQUARE_ONLY) != DEBUG_OUT
assert out(DEBUG_STARTER).startswith("die 3.5 0.0 0.0") or out(DEBUG_STARTER).startswith("die 3.5 -0.0"), out(DEBUG_STARTER)

# --- predict items ---------------------------------------------------------------------------------

PREDICT_LINEAR = '''import numpy as np

x = np.array([0.0, 1.0, 2.0])
p = np.array([0.5, 0.3, 0.2])
mean = (x * p).sum()
var = ((x - mean) ** 2 * p).sum()
print(round(float(mean), 4), round(float(var), 4))
y = 3 * x + 2
print(round(float((y * p).sum()), 4), round(float(((y - (y * p).sum()) ** 2 * p).sum()), 4))
'''
PREDICT_LINEAR_OUT = out(PREDICT_LINEAR)
print("predict linear:\n" + PREDICT_LINEAR_OUT)
assert PREDICT_LINEAR_OUT == "0.7 0.61\n4.1 5.49\n", PREDICT_LINEAR_OUT

REVIEW_BERNOULLI = '''import numpy as np

for p in (0.1, 0.5, 0.9):
    values = np.array([0.0, 1.0])
    probs = np.array([1 - p, p])
    mean = (values * probs).sum()
    print(p, round(float(mean), 2), round(float(((values - mean) ** 2 * probs).sum()), 2))
'''
REVIEW_BERNOULLI_OUT = out(REVIEW_BERNOULLI)
print("review bernoulli:\n" + REVIEW_BERNOULLI_OUT)
assert REVIEW_BERNOULLI_OUT == "0.1 0.1 0.09\n0.5 0.5 0.25\n0.9 0.9 0.09\n", REVIEW_BERNOULLI_OUT

REVIEW_CODE_STARTER = '''import numpy as np

values = np.array([0.0, 10.0, 100.0])
probs = np.array([0.89, 0.1, 0.01])
'''
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def expectation(values, probs):
    return float((values * probs).sum())


print(expectation(values, probs))
print(expectation(np.arange(1, 7), np.full(6, 1 / 6)))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "2.0\n3.5\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.prob.expectation-and-variance
kind: topic
status: ready
title: "Expectation and variance"
summary: "The mean of a random variable, its spread, the rules they follow, and the law of large numbers watched in a simulation."
prerequisites: [ml.prob.distributions]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Compute the expected value and the variance of a discrete distribution from its table."
  - "Use linearity of expectation, and the rule for the variance of a sum of independent variables."
  - "Watch sample means settle on the expectation as the sample grows, and say what the law of large numbers promises."
  - "Standardize a value with the mean and the standard deviation, and read the result."
# Linked, never copied or embedded: OpenStax is CC BY 4.0; StatQuest's videos
# are under the standard YouTube licence; NumPy's documentation is under the
# NumPy licence (BSD-3-Clause).
resources:
  - title: "OpenStax Introductory Statistics 2e: section 4.2 (Mean or Expected Value and Standard Deviation) and section 6.1 (The Standard Normal Distribution, for z-scores)"
    url: https://openstax.org/details/books/introductory-statistics-2e
    type: reading
    use: link
    license: CC BY 4.0
  - title: "StatQuest: Expected Values, Main Ideas!!! (Josh Starmer)"
    url: https://www.youtube.com/watch?v=KLs_7b7SKi4
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "numpy.cumsum (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.cumsum.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-a-die-in-expectation
  - parsons-expected-prize
  - mcq-expected-profit
  - predict-linearity
  - mcq-gamblers-fallacy
  - fill-expectation-and-variance
  - write-standardize
prove:
  build: build-moments-and-running-means
  debug: debug-spread-report
  explain:
    prompt: |
      A teammate says two things: "the expected number of heads in 100 flips is 50, so I expect to see exactly 50", and "if I average two independent noisy sensors, the noise doubles". In your own words: what does an expected value promise, and what doesn't it? What does the law of large numbers say, and what is the gambler's fallacy? Why does averaging two independent readings reduce the variance rather than double it? And what does a z-score of 2 mean?
    rubric:
      - id: expectation
        required: true
        description: "The expected value is the long-run average of many draws, each value weighted by its probability; a single draw needn't equal it (exactly 50 heads has chance about 0.08), and the standard deviation (5 here) says how far a draw typically lands from it."
      - id: law
        required: true
        description: "As the number of draws grows, the sample mean settles on the expected value; it does so by swamping early luck, not by compensating for it, so after ten heads the next flip is still a half: expecting tails to 'catch up' is the gambler's fallacy."
      - id: independence
        required: true
        description: "Variances of independent variables add, so the sum of two readings has twice the variance; the average divides by 2, which divides the variance by 4, leaving half the variance (standard deviation over root 2): averaging independent noise shrinks it. Doubling one reading would quadruple the variance, which is the case the teammate has in mind."
      - id: z-score
        required: false
        description: "A z-score is how many standard deviations a value sits from the mean; 2 means two standard deviations above, which for a normal is beyond about 97.7 percent of values, and it lets values on different scales be compared."
    model_answer: |
      An expected value is the average you'd get over a great many draws: each value times its probability, added up. For 100 flips that's 50, but it promises nothing about one run; getting exactly 50 happens only about 8 percent of the time, and the standard deviation, 5 here, says a run typically lands within a handful of 50. The law of large numbers says that as the number of draws grows, the sample's mean settles on the expected value, and it settles by swamping: ten early heads are a drop in a million flips, not a debt the coin pays back. Each flip is still a half, whatever came before, and expecting tails to catch up is the gambler's fallacy. For the sensors: when independent variables are added, their variances add, so the sum of two readings has twice the variance of one. Averaging divides the sum by 2, and dividing a variable by 2 divides its variance by 4, so the average has half the variance of a single reading, a standard deviation smaller by root 2. The noise shrinks, which is why averaging repeated measurements works. What the teammate is picturing is doubling one reading, which does quadruple the variance, because the same noise is counted twice rather than two independent noises partly cancelling. A z-score is a value's distance from the mean measured in standard deviations: 2 means two standard deviations above the mean, which for a normal is higher than about 97.7 percent of values, and it lets a score on one scale be compared with a score on another.
review_pool:
  - review-predict-bernoulli-moments
  - review-mcq-two-dice-or-one-doubled
  - review-mcq-which-score-is-better
  - review-expectation
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: expectation
    description: "Compute an expected value from a distribution's table and read it as a long-run average"
  - id: variance
    description: "Compute a variance and a standard deviation from a table, and apply the rules for scaling and for sums of independent variables"
  - id: law
    description: "Say what the law of large numbers promises, watch it in a simulation, and name the gambler's fallacy"
  - id: standardize
    description: "Standardize a value with the mean and the standard deviation, and read a z-score"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

The last topic gave a random variable a table of chances. This one boils the table down to two numbers: the **expected value**, where the draws land on average, and the **variance**, how far they spread. Those two obey simple rules (expectations add; variances of independent things add; scaling by `a` scales the variance by `a²`) that explain why averaging noisy measurements works and why a long run settles down, which is the **law of large numbers**, watched here in a simulation rather than taken on trust.

The main resource is **OpenStax _Introductory Statistics 2e_, section 4.2**, the mean and standard deviation of a discrete random variable, with section 6.1's first pages for z-scores; about 25 minutes. StatQuest's video on expected values is the short picture version. Watch for:

- **Each value times its probability, summed:** the expected value, which is a long-run average and not a prediction of one draw.
- **The standard deviation of a table**, built the same way from squared distances.
- **A z-score** as "how many standard deviations from the mean".

</Intro>

<Resource index={{0}} />

<Recap>

- **Expected value** (the mean of a random variable): each value times its probability, added up: `(values * probs).sum()`. A fair die: 3.5. A Bernoulli(`p`): `p`. A binomial(`n`, `p`): `n * p`. It is the long-run average of many draws, not what one draw will be (no die shows 3.5).
- **Variance** is the expected squared distance from the mean, `((values - mean) ** 2 * probs).sum()`, and the **standard deviation** is its square root, back in the variable's own units. A die: variance 2.9167, standard deviation 1.708. A Bernoulli(`p`): `p * (1 - p)`, largest at `p = 0.5`. A binomial: `n * p * (1 - p)`.
- **A sample's mean and variance** (`rolls.mean()`, `rolls.var()`) estimate the table's: 100,000 rolls gave {lines[1].split()[0]} and {SAMPLE_VAR}.
- **The law of large numbers:** as the number of draws grows, the sample mean settles on the expected value. The running mean of the rolls was {RUNNING[10]} after 10, {RUNNING[100]} after 100, {RUNNING[1000]} after 1,000 and {RUNNING[100000]} after 100,000. It settles by **swamping** early luck, not by making up for it: after ten heads the next flip is still a half, and expecting tails to "catch up" is the **gambler's fallacy**.
- **Linearity.** `E[aX + b] = a E[X] + b`, and `E[X + Y] = E[X] + E[Y]` always, independent or not. Ten dice have an expected total of 35.
- **Scaling and adding variances.** `Var[aX + b] = a² Var[X]`: doubling one die doubles its mean (7) and **quadruples** its variance ({DOUBLED[1]} in the sample, against 2.9167). `Var[X + Y] = Var[X] + Var[Y]` when `X` and `Y` are **independent**: two different dice have mean 7 and variance about 5.83 ({TWO_DICE[1]} in the sample), which is why "two dice" and "one die doubled" are different random variables with the same mean.
- **Why averaging helps.** The mean of `n` independent copies has variance `Var[X] / n`, so its standard deviation shrinks like `1 / sqrt(n)`: four measurements halve the noise, a hundred cut it to a tenth. (The next topics give this shrinking spread a name, the standard error.)
- **Standardizing:** `z = (x - mean) / sd` is how many standard deviations a value sits from the mean. A height of 190 with mean 170 and spread 10 is `z = 2`; a 75 on a test with mean 60 and spread 10 (`z = 1.5`) beats an 80 on a test with mean 70 and spread 20 (`z = 0.5`). For a normal, `z = 2` is above about 97.7 percent of values.
- **In machine learning:** a loss is an expected value estimated by a sample mean; a mini-batch's gradient is an average whose noise shrinks like `1 / sqrt(batch size)`; features are standardized before training so every one is on the same scale; and the gambler's fallacy is the mistake behind "the model has been wrong three times, so it's due to be right".

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-expected-prize.yaml",
    '''id: parsons-expected-prize
type: parsons
rev: 1
prompt: |
  A lottery ticket pays 100 with chance 0.01 and nothing otherwise. Put the lines in order to print the expected prize, `1.0`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'values = np.array([100.0, 0.0])'
  - 'probs = np.array([0.01, 0.99])'
  - 'print((values * probs).sum())'
distractors:
  - 'print(values.mean())'
explanation: |
  The expected value weights each outcome by its probability: `100 * 0.01 + 0 * 0.99 = 1.0`, the long-run average per ticket, and the most such a ticket is worth paying. The decoy averages the two outcomes as if they were equally likely and prints 50.0.
skills: [expectation]
''',
)

write(
    "recall/mcq-expected-profit.yaml",
    '''id: mcq-expected-profit
type: mcq
rev: 1
prompt: |
  A game costs 3 to play and pays 10 with chance 0.2, otherwise nothing. What is the expected profit per play, and should you play many times?
choices:
  - '`+7`: you win 10 and paid 3'
  - '`-1`: `10 * 0.2 - 3`; over many plays you lose about 1 per play, so no'
  - '`+2`: `10 * 0.2`, the cost doesn''t count'
  - '`0.2`: the chance of winning'
answer: 1
explanation: |
  The expected payout is `10 * 0.2 = 2`, and every play costs 3, so the expected profit is `-1`. Over many plays the law of large numbers makes the average loss settle near 1 per play; a lucky early streak doesn't change that. Expected profit is the number to look at before playing anything repeatedly.
skills: [expectation, law]
''',
)

write(
    "recall/predict-linearity.yaml",
    f'''id: predict-linearity
type: predict_output
rev: 1
prompt: |
  A three-value table, then the same variable scaled and shifted. What does the program print?
code: |
{block(PREDICT_LINEAR)}expected_output: |
{block(PREDICT_LINEAR_OUT)}explanation: |
  The mean is `0 * 0.5 + 1 * 0.3 + 2 * 0.2 = 0.7`, and the variance is the probability-weighted squared distance from it, 0.61. For `y = 3x + 2` the mean is `3 * 0.7 + 2 = 4.1` (linearity) and the variance is `9 * 0.61 = 5.49`: the shift by 2 moves every value equally and changes no spread, and scaling by 3 scales the variance by `3² = 9`.
skills: [variance, expectation]
''',
)

write(
    "recall/mcq-gamblers-fallacy.yaml",
    '''id: mcq-gamblers-fallacy
type: mcq
rev: 1
prompt: |
  A fair coin has just landed heads ten times in a row. The law of large numbers says the fraction of heads tends to a half in the long run. So the next flip is more likely to be tails?
choices:
  - 'Yes: tails are owed, so the fraction can get back to a half'
  - 'Yes, slightly: the law adjusts the odds a little after a streak'
  - 'Only if the coin is fair; a loaded coin wouldn''t need to catch up'
  - 'No: each flip is still a half; the fraction tends to a half because ten heads become a drop in a million flips, not because later flips compensate'
answer: 3
explanation: |
  The law of large numbers works by swamping, not by correcting. A million further flips at a half each bury the ten-head streak in the fraction without any flip remembering it. Believing the coin owes tails is the gambler's fallacy, and it has the same shape as "the model has been wrong three times, so it's due to be right".
skills: [law]
''',
)

write(
    "recall/review-predict-bernoulli-moments.yaml",
    f'''id: review-predict-bernoulli-moments
type: predict_output
rev: 1
prompt: |
  The mean and variance of a Bernoulli variable at three values of `p`. What does the program print?
code: |
{block(REVIEW_BERNOULLI)}expected_output: |
{block(REVIEW_BERNOULLI_OUT)}explanation: |
  A Bernoulli's mean is `p` (0 times `1 - p` plus 1 times `p`), and its variance is `p * (1 - p)`: 0.09 at 0.1 and at 0.9, 0.25 at 0.5. The spread is largest when the outcome is most uncertain, and the same at `p` and `1 - p`.
skills: [expectation, variance]
''',
)

write(
    "recall/review-mcq-two-dice-or-one-doubled.yaml",
    '''id: review-mcq-two-dice-or-one-doubled
type: mcq
rev: 1
prompt: |
  `X` is one fair die (mean 3.5, variance about 2.92). Compare the total of two different dice with twice one die, `2X`.
choices:
  - 'Both have mean 7 and variance about 5.83'
  - 'Both have mean 7; two dice have variance about 5.83 (independent variances add) while `2X` has about 11.67 (scaling by 2 multiplies the variance by 4)'
  - 'Two dice have mean 7; `2X` has mean 3.5, since it''s still one die'
  - 'Both have mean 7 and variance about 11.67'
answer: 1
explanation: |
  Expectations add either way, so both means are 7. Variances add only for independent variables: two dice give `2.92 + 2.92`. Doubling one die doesn't add an independent second roll; it scales one roll by 2, and `Var[2X] = 4 Var[X]`. Same mean, different spread: a 2 and a 12 are far likelier with one die doubled.
skills: [variance]
''',
)

write(
    "recall/review-mcq-which-score-is-better.yaml",
    '''id: review-mcq-which-score-is-better
type: mcq
rev: 1
prompt: |
  You scored 82 on a test with mean 70 and standard deviation 8, and a friend scored 90 on a test with mean 80 and standard deviation 20. Who did better relative to their class?
choices:
  - 'You: a z-score of 1.5 against 0.5'
  - 'Your friend: 90 is a higher score'
  - 'Your friend: 10 above the mean beats 12 above the mean once you allow for the harder test'
  - 'It can''t be compared without the number of students'
answer: 0
explanation: |
  Standardize both: `(82 - 70) / 8 = 1.5` standard deviations above your class, `(90 - 80) / 20 = 0.5` above theirs. A z-score puts scores on different scales on one footing, and 1.5 is further above the typical student than 0.5. The raw scores and the number of students don't enter.
skills: [standardize]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-die-in-expectation/exercise.yaml",
    f'''id: example-a-die-in-expectation
stage: worked_example
rev: 1
title: "A die, in expectation"
prompt: |
  This program computes a die's expected value and variance from its table, checks them against a hundred thousand rolls, watches the running mean settle, compares two dice with one die doubled, and standardizes five heights. Press **Run**, then read how each part works.
steps:
  - label: "The table's two numbers"
    lines: "3-7"
    note: "Six faces, each with probability one sixth. The expected value is each face times its probability, summed: 3.5, which no roll ever shows. The variance is the probability-weighted squared distance from 3.5, 2.9167, and the standard deviation is its square root, 1.708 pips."
  - label: "A sample agrees"
    lines: "9-11"
    note: "A hundred thousand rolls from a seeded generator. Their mean and variance (`rolls.mean()`, `rolls.var()`) land within a few thousandths of the table's numbers: statistics of a sample estimating the parameters of the distribution it came from."
  - label: "The law of large numbers, watched"
    lines: "12-13"
    note: "The running mean after 10, 100, 1,000, 10,000 and 100,000 rolls: {RUNNING[10]}, {RUNNING[100]}, {RUNNING[1000]}, {RUNNING[10000]}, {RUNNING[100000]}. It settles on 3.5 by swamping the early rolls, not by compensating for them."
  - label: "Two dice against one die doubled"
    lines: "15-18"
    note: "Both have mean 7. The total of two **independent** dice has variance about 5.83, the two variances added ({TWO_DICE[1]} in the sample). One die doubled has variance about 11.67, four times one die ({DOUBLED[1]} in the sample): scaling by 2 scales the variance by 2 squared. Same mean, different random variable."
  - label: "Standardizing"
    lines: "20-22"
    note: "Five heights from a normal with mean 170 and spread 10, and each one's z-score, `(x - 170) / 10`: how many standard deviations it sits from the mean. A z-score compares values on different scales, and is what feature scaling does to every column before training."
''',
)
write("exercises/example-a-die-in-expectation/solution.py", EXAMPLE)
write(
    "exercises/example-a-die-in-expectation/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the die's moments, a sample's, the running mean, two dice against one doubled, and five z-scores."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-expectation-and-variance/exercise.yaml",
    f'''id: fill-expectation-and-variance
stage: fill_in
rev: 1
title: "Expectation and variance from a table"
prompt: |
  `expectation(values, probs)` should weight each value by its probability and add; `variance(values, probs)` should do the same with the squared distances from the mean. Replace each `...` so the program prints a fair die, a coin that lands heads 30 percent of the time, and a loaded die that shows 1 half the time:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The weights are the probabilities: `values * probs`."
  - "Distances from the mean are squared before they're weighted."
skills: [expectation, variance]
''',
)
write("exercises/fill-expectation-and-variance/starter.py", FILL_STARTER)
write("exercises/fill-expectation-and-variance/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-expectation-and-variance/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three tables' moments."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_certain_value_and_a_binomial():
    """A variable that is always 4 has mean 4 and variance 0; the table of two fair flips has mean 1 and variance 0.5."""
    expectation = function("expectation")
    variance = function("variance")
    assert expectation(np.array([4.0]), np.array([1.0])) == 4 and variance(np.array([4.0]), np.array([1.0])) == 0
    flips = np.array([0.0, 1.0, 2.0])
    probs = np.array([0.25, 0.5, 0.25])
    assert abs(expectation(flips, probs) - 1) < 1e-12 and abs(variance(flips, probs) - 0.5) < 1e-12
''',
)
write("exercises/fill-expectation-and-variance/wrong/no-square.py", FILL_NO_SQUARE)
write(
    "exercises/fill-expectation-and-variance/wrong/typed-in.py",
    "import numpy as np\n\n\ndef expectation(values, probs):\n    return 3.5\n\n\ndef variance(values, probs):\n    return 2.9167\n\n\n"
    + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-standardize/exercise.yaml",
    f'''id: write-standardize
stage: write
rev: 1
title: "Standardize a value"
prompt: |
  Write `standardize(x, mean, sd)`, which returns how many standard deviations `x` sits from the mean, `(x - mean) / sd`, for a number or an array. Then print the z-scores of a 75 on a test with mean 60 and spread 10 and an 80 on a test with mean 70 and spread 20, on one line, and the z-scores of heights 150, 170 and 195 against mean 170 and spread 10, rounded to 1 place:

  ```
{block(WRITE_OUT)}  ```

  The 75 is the better score: 1.5 standard deviations above its class against 0.5.
hints:
  - "Subtract the mean first, then divide by the standard deviation."
  - "Arithmetic on an array happens entry by entry, so the same line serves a number and an array."
skills: [standardize]
''',
)
write("exercises/write-standardize/starter.py", WRITE_STARTER)
write("exercises/write-standardize/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-standardize/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the two test scores' z-scores and the three heights'."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_properties():
    """The mean standardizes to 0, a value one spread above to 1, and an array keeps its shape."""
    standardize = function("standardize")
    assert standardize(70, 70, 8) == 0 and standardize(78, 70, 8) == 1
    z = standardize(np.array([[1.0, 2.0], [3.0, 4.0]]), 2.5, 0.5)
    assert z.shape == (2, 2) and z.tolist() == [[-3.0, -1.0], [1.0, 3.0]]
''',
)
write(
    "exercises/write-standardize/wrong/divides-first.py",
    WRITE_STARTER + '''

def standardize(x, mean, sd):
    return x / sd - mean


print(standardize(75, 60, 10), standardize(80, 70, 20))
print(np.round(standardize(np.array([150.0, 170.0, 195.0]), 170, 10), 1))
''',
)
write(
    "exercises/write-standardize/wrong/typed-in.py",
    WRITE_STARTER + "\n\ndef standardize(x, mean, sd):\n    return 1.5\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof --------------------------------------------------------------------------------------

write(
    "exercises/build-moments-and-running-means/exercise.yaml",
    f'''id: build-moments-and-running-means
stage: build
rev: 1
title: "Moments, sums and running means"
prompt: |
  Starting from a blank editor, write four tools:

  - `moments(values, probs)`: the expected value and the variance of a table, as a pair of floats.
  - `sum_of_independent(means, variances)`: the mean and the variance of a sum of independent variables with those means and variances, as a pair of floats (means add; so do variances).
  - `running_means(sample)`: an array whose entry `i` is the mean of the first `i + 1` entries of `sample` (`np.cumsum` divided by the counts 1, 2, 3, ...).
  - `standardize(x, mean, sd)`: the z-score of `x`, for a number or an array.

  Then print a fair die's moments (variance rounded to 4), the mean and variance of the total of ten dice (variance rounded to 4), the running mean of 10,000 rolls from `np.random.default_rng(2)` after 10, 100, 1,000 and 10,000 rolls (rounded to 3), and the z-scores of heights 160 and 190 against mean 170 and spread 10:

  ```
{block(BUILD_OUT)}  ```

  The checks use other tables whose answers are known exactly.
skills: [expectation, variance, law, standardize]
''',
)
write("exercises/build-moments-and-running-means/starter.py", "")
write("exercises/build-moments-and-running-means/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-moments-and-running-means/test_exercise.py",
    f'''import math

import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the die, the ten dice, the running means and the z-scores."""
    assert run() == {BUILD_OUT!r}


def test_moments_of_known_tables():
    """A Bernoulli(0.3) has moments (0.3, 0.21); a binomial(10, 0.3) table has (3, 2.1)."""
    moments = function("moments")
    mean, variance = moments(np.array([0.0, 1.0]), np.array([0.7, 0.3]))
    assert abs(mean - 0.3) < 1e-12 and abs(variance - 0.21) < 1e-12
    ks = np.arange(11)
    probs = np.array([math.comb(10, k) * 0.3**k * 0.7 ** (10 - k) for k in ks])
    mean, variance = moments(ks, probs)
    assert abs(mean - 3.0) < 1e-9 and abs(variance - 2.1) < 1e-9


def test_sum_of_independent():
    """Means add and variances add, not standard deviations: three variables with variance 4 give variance 12."""
    sum_of_independent = function("sum_of_independent")
    assert sum_of_independent([1.0, 2.0, 3.0], [4.0, 4.0, 4.0]) == (6.0, 12.0)


def test_running_means():
    """The running means of [2, 4, 6] are [2, 3, 4]."""
    running_means = function("running_means")
    assert running_means(np.array([2.0, 4.0, 6.0])).tolist() == [2.0, 3.0, 4.0]


def test_standardize():
    """The mean standardizes to 0 and one spread above to 1."""
    standardize = function("standardize")
    assert standardize(50, 50, 5) == 0 and standardize(55, 50, 5) == 1
''',
)
write("exercises/build-moments-and-running-means/wrong/no-square.py", BUILD_NO_SQUARE)
write("exercises/build-moments-and-running-means/wrong/sds-add.py", BUILD_SD_ADDS)
write("exercises/build-moments-and-running-means/wrong/not-running.py", BUILD_NOT_RUNNING)
write(
    "exercises/build-moments-and-running-means/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def moments(values, probs):\n    return 3.5, 2.9167\n\n\n"
    + "def sum_of_independent(means, variances):\n    return 35.0, 29.1667\n\n\n"
    + "def running_means(sample):\n    return np.zeros(len(sample)) + 3.5\n\n\n"
    + "def standardize(x, mean, sd):\n    return np.array([-1.0, 2.0])\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-spread-report/exercise.yaml",
    f'''id: debug-spread-report
stage: debug
rev: 1
title: "A spread that comes out zero"
prompt: |
  `summary(values, probs)` should return a table's mean, variance and standard deviation, and the program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the variance prints as 0.0 (or -0.0) for both tables, because the distances from the mean are weighted without being **squared**, and weighted distances from the mean always add to zero. Fix that, and the standard deviation is still wrong: it is the **square root** of the variance, not half of it.
skills: [variance]
''',
)
write("exercises/debug-spread-report/starter.py", DEBUG_STARTER)
write("exercises/debug-spread-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-spread-report/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the die's and the prize's mean, variance and standard deviation."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_two_fair_flips():
    """The table of heads in two fair flips has mean 1, variance 0.5 and standard deviation root 0.5."""
    summary = function("summary")
    mean, variance, sd = summary(np.array([0.0, 1.0, 2.0]), np.array([0.25, 0.5, 0.25]))
    assert abs(mean - 1) < 1e-12 and abs(variance - 0.5) < 1e-12 and abs(sd - 0.5**0.5) < 1e-12
''',
)
write("exercises/debug-spread-report/wrong/square-only.py", DEBUG_SQUARE_ONLY)
write(
    "exercises/debug-spread-report/wrong/typed-in.py",
    "import numpy as np\n\n\ndef summary(values, probs):\n    return 3.5, 2.9167, 1.708\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise -----------------------------------------------------------------------

write(
    "exercises/review-expectation/exercise.yaml",
    f'''id: review-expectation
stage: review_code
rev: 1
title: "An expected value, from memory"
prompt: |
  Write `expectation(values, probs)`, the expected value of a table as a float, and print it for the starter's prize table and for a fair die:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [expectation]
''',
)
write("exercises/review-expectation/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-expectation/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-expectation/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints 2.0 and 3.5."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_tables():
    """A Bernoulli(0.25) has expectation 0.25; a certain 7 has expectation 7."""
    expectation = function("expectation")
    assert abs(expectation(np.array([0.0, 1.0]), np.array([0.75, 0.25])) - 0.25) < 1e-12
    assert expectation(np.array([7.0]), np.array([1.0])) == 7
''',
)
write(
    "exercises/review-expectation/wrong/plain-mean.py",
    REVIEW_CODE_STARTER + '''

def expectation(values, probs):
    return float(values.mean())


print(expectation(values, probs))
print(expectation(np.arange(1, 7), np.full(6, 1 / 6)))
''',
)
write(
    "exercises/review-expectation/wrong/typed-in.py",
    REVIEW_CODE_STARTER + "\n\ndef expectation(values, probs):\n    return 2.0\n\n\nprint(2.0)\nprint(3.5)\n",
)

print("ml.prob.expectation-and-variance written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
