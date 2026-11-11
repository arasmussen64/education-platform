"""Writes the topic ml.prob.distributions (Module 5's first topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Pyodide's NumPy is the same release, and its seeded generator was checked to
give the same draws (2026-11-10). Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.prob.distributions")


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

EXAMPLE = '''import math

import numpy as np

rng = np.random.default_rng(1)

flips = rng.random(10) < 0.3
print(flips.astype(int), flips.sum())

heads = rng.binomial(10, 0.3, size=100000)
counts = np.bincount(heads, minlength=11)
print(counts[:5])
for k in range(5):
    simulated = counts[k] / len(heads)
    exact = math.comb(10, k) * 0.3**k * 0.7 ** (10 - k)
    print(k, round(float(simulated), 3), round(exact, 3), "#" * round(exact * 50))

u = rng.uniform(0, 1, size=100000)
print(round(float(np.mean(u < 0.25)), 3), round(float(np.mean(u == 0.25)), 3))

heights = rng.normal(170, 10, size=100000)
print(round(float(heights.mean()), 1), round(float(heights.std()), 1))
for width in (1, 2, 3):
    inside = np.mean(np.abs(heights - 170) < width * 10)
    print(width, round(float(inside), 3))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
lines = EXAMPLE_OUT.splitlines()
assert lines[-3].startswith("1 0.68") and lines[-2].startswith("2 0.95") and lines[-1].startswith("3 0.99"), EXAMPLE_OUT
assert "e-" not in EXAMPLE_OUT and "e+" not in EXAMPLE_OUT
PMF_ROWS = lines[2:7]
for row in PMF_ROWS:
    k, simulated, exact = row.split()[:3]
    assert abs(float(simulated) - float(exact)) <= 0.003, row
UNIFORM = lines[7]
assert UNIFORM.endswith(" 0.0"), UNIFORM
MEAN_STD = lines[8]
assert MEAN_STD == "170.0 10.0", MEAN_STD
RULE = [line.split()[1] for line in lines[-3:]]  # the simulated 68-95-99.7 fractions
RULE_TEXT = f"{RULE[0]}, {RULE[1]} and {RULE[2]}"

# --- the fill-in -----------------------------------------------------------------------

FILL_HEAD = '''import math


def binomial_pmf(k, n, p):
    """The chance of exactly k yeses in n tries, each a yes with chance p."""
    return math.comb(n, k) * p**K * (1 - p) ** (n - REST)


for k in range(11):
    print(k, round(binomial_pmf(k, 10, 0.3), 3), "#" * round(binomial_pmf(k, 10, 0.3) * 50))
print(round(sum(binomial_pmf(k, 10, 0.3) for k in range(11)), 6))
'''
FILL_SOLUTION = FILL_HEAD.replace("p**K", "p**k").replace("(n - REST)", "(n - k)")
FILL_STARTER = FILL_HEAD.replace("p**K", "p**...").replace("(n - REST)", "(n - ...)")
FILL_NO_COMB = FILL_SOLUTION.replace("math.comb(n, k) * ", "")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT.endswith("1.0\n") and FILL_OUT.startswith("0 0.028 #\n1 0.121 ######\n"), FILL_OUT
assert out(FILL_NO_COMB) != FILL_OUT

# --- the write ----------------------------------------------------------------------------

WRITE_STARTER = '''import numpy as np

rng = np.random.default_rng(3)
'''
WRITE_SOLUTION = WRITE_STARTER + '''

def histogram(sample, bins):
    counts, edges = np.histogram(sample, bins=bins)
    for count, left, right in zip(counts, edges[:-1], edges[1:]):
        print(f"{left:6.1f} to {right:6.1f} {'#' * round(count / len(sample) * 100)}")


histogram(rng.normal(0, 1, size=10000), bins=np.arange(-4, 5, 1.0))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert len(WRITE_OUT.splitlines()) == 8 and WRITE_OUT.splitlines()[3].startswith("  -1.0 to    0.0 ###################"), WRITE_OUT

# --- the build -------------------------------------------------------------------------------

BUILD_SOLUTION = '''import math

import numpy as np


def binomial_pmf(k, n, p):
    return math.comb(n, k) * p**k * (1 - p) ** (n - k)


def empirical_pmf(sample, n):
    counts = np.bincount(sample, minlength=n + 1)
    return counts / len(sample)


def largest_gap(sample, n, p):
    simulated = empirical_pmf(sample, n)
    exact = np.array([binomial_pmf(k, n, p) for k in range(n + 1)])
    return float(np.abs(simulated - exact).max())


def within(sample, center, spread):
    return [float(np.mean(np.abs(sample - center) < width * spread)) for width in (1, 2, 3)]


rng = np.random.default_rng(1)
heads = rng.binomial(10, 0.3, size=100000)
print("pmf", np.round(empirical_pmf(heads, 10)[:4], 3))
print("largest gap below 0.003", largest_gap(heads, 10, 0.3) < 0.003)
heights = rng.normal(170, 10, size=100000)
print("within 1, 2, 3 spreads", np.round(within(heights, 170, 10), 3))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT.splitlines()[1] == "largest gap below 0.003 True", BUILD_OUT
assert BUILD_OUT.splitlines()[2].startswith("within 1, 2, 3 spreads [0.68"), BUILD_OUT
BUILD_NO_COMB = BUILD_SOLUTION.replace("    return math.comb(n, k) * p**k * (1 - p) ** (n - k)", "    return p**k * (1 - p) ** (n - k)")
BUILD_DIVIDES_BY_BINS = BUILD_SOLUTION.replace("    return counts / len(sample)", "    return counts / len(counts)")
BUILD_WITHIN_LE = BUILD_SOLUTION.replace("np.abs(sample - center) < width * spread", "np.abs(sample - center) < spread")
for wrong in (BUILD_NO_COMB, BUILD_DIVIDES_BY_BINS, BUILD_WITHIN_LE):
    assert out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import math

import numpy as np


def roll(rng, size):
    return rng.integers(1, 7, size=size)


def sixes_pmf(k):
    return math.comb(4, k) * (1 / 6) ** k * (5 / 6) ** (4 - k)


rng = np.random.default_rng(5)
rolls = roll(rng, 60000)
counts = np.bincount(rolls, minlength=7)[1:]
print("faces", np.round(counts / len(rolls), 3))

sixes = rng.binomial(4, 1 / 6, size=60000)
for k in range(5):
    print(k, round(float(np.mean(sixes == k)), 3), round(sixes_pmf(k), 3))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("rng.integers(1, 7, size=size)", "rng.integers(1, 6, size=size)").replace(
    "(1 / 6) ** k * (5 / 6) ** (4 - k)", "(1 / 6) ** k * (5 / 6) ** k"
)
DEBUG_RANGE_ONLY = DEBUG_SOLUTION.replace("(1 / 6) ** k * (5 / 6) ** (4 - k)", "(1 / 6) ** k * (5 / 6) ** k")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
faces = DEBUG_OUT.splitlines()[0]
assert faces.startswith("faces [0.16") and "0.   " not in faces and faces.count("0.1") == 6, faces
assert out(DEBUG_RANGE_ONLY) != DEBUG_OUT
assert out(DEBUG_STARTER).splitlines()[0].endswith("0.   ]"), out(DEBUG_STARTER)

# --- predict items --------------------------------------------------------------------------------

PREDICT_PMF = '''import math

n, p = 3, 0.5
for k in range(4):
    print(k, math.comb(n, k), math.comb(n, k) * p**k * (1 - p) ** (n - k))
'''
PREDICT_PMF_OUT = out(PREDICT_PMF)
print("predict pmf:\n" + PREDICT_PMF_OUT)
assert PREDICT_PMF_OUT == "0 1 0.125\n1 3 0.375\n2 3 0.375\n3 1 0.125\n", PREDICT_PMF_OUT

PREDICT_BINCOUNT = '''import numpy as np

heads = np.array([2, 0, 2, 1, 2, 3])
counts = np.bincount(heads, minlength=4)
print(counts)
print(np.round(counts / len(heads), 2))
print(counts.sum() == len(heads))
'''
PREDICT_BINCOUNT_OUT = out(PREDICT_BINCOUNT)
print("predict bincount:\n" + PREDICT_BINCOUNT_OUT)
assert PREDICT_BINCOUNT_OUT == "[1 1 3 1]\n[0.17 0.17 0.5  0.17]\nTrue\n", PREDICT_BINCOUNT_OUT

REVIEW_CODE_STARTER = '''import numpy as np

rng = np.random.default_rng(2)
'''
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def bernoulli(rng, p, size):
    return (rng.random(size) < p).astype(int)


draws = bernoulli(rng, 0.3, 100000)
print(draws[:8], round(float(draws.mean()), 2))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT.endswith(" 0.3\n"), REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.prob.distributions
kind: topic
status: ready
title: "Random variables and distributions"
summary: "A random variable as a number with chances attached: Bernoulli, binomial, uniform and normal, simulated with NumPy and drawn as text histograms."
prerequisites: [ml.math.probability-and-statistics, ml.la.numpy-arrays]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Name the Bernoulli, binomial, uniform and normal distributions, and say what each one models."
  - "Simulate draws from each with np.random.default_rng and a seed."
  - "Turn a sample into a histogram and compare it with the formula."
  - "Read a probability as an area under a density, and say why a single value has probability zero."
# Linked, never copied or embedded: OpenStax is CC BY 4.0; StatQuest's videos
# are under the standard YouTube licence; NumPy's documentation is under the
# NumPy licence (BSD-3-Clause).
resources:
  - title: "OpenStax Introductory Statistics 2e: chapter 4 (Discrete Random Variables, sections 4.1 to 4.3), section 5.2 (The Uniform Distribution) and chapter 6 (The Normal Distribution, sections 6.1 and 6.2)"
    url: https://openstax.org/details/books/introductory-statistics-2e
    type: reading
    use: link
    license: CC BY 4.0
  - title: "StatQuest: The Main Ideas behind Probability Distributions (Josh Starmer)"
    url: https://www.youtube.com/watch?v=oI3hZJqXJuc
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "numpy.random.Generator (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/random/generator.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-four-distributions-simulated
  - parsons-count-the-heads
  - mcq-which-distribution
  - predict-a-small-pmf
  - mcq-why-a-value-has-no-probability
  - fill-binomial-pmf
  - write-text-histogram
prove:
  build: build-check-a-simulation
  debug: debug-dice-report
  explain:
    prompt: |
      A teammate has read that a model's output is "a Bernoulli random variable" and that its errors "look normal", and asks what any of that means. In your own words: what is a random variable, and what is its distribution? What do the Bernoulli, binomial, uniform and normal distributions each model, with one everyday example apiece? Why does a single exact value of a normal random variable have probability zero, and what does have a probability? And what is a seed for when you simulate?
    rubric:
      - id: variable
        required: true
        description: "A random variable is a number whose value chance decides (a flip, a count, a measurement); its distribution says which values it can take and how likely each is, as a table of probabilities for a discrete one or a density curve for a continuous one."
      - id: four
        required: true
        description: "Bernoulli: one yes-or-no with chance p (one email is spam or not); binomial: the count of yeses in n independent tries with the same p (spam among 20 emails); uniform: any value in a range equally likely (a random point on a line); normal: the bell curve that sums of many small effects make (heights, measurement errors)."
      - id: density
        required: true
        description: "A continuous variable has infinitely many values, so the chance of exactly one of them is zero; probability is the area under the density between two values, which is why questions about it are about ranges."
      - id: seed
        required: false
        description: "A seed fixes the generator's starting point so a simulation repeats exactly, which makes a result checkable and a bug reproducible; different seeds give different samples from the same distribution."
    model_answer: |
      A random variable is a number that chance decides: whether one email is spam, how many of twenty are, how tall the next person through the door is. Its distribution is the list of values it can take and how likely each one is. For a variable that takes separate values, like a count, that's a table: each value with its probability, adding up to one. For a variable that can take any value in a range, like a height, it's a curve called a density, and probability is area under the curve. The four in this topic cover most of what a model meets. Bernoulli is one yes-or-no with a chance p of yes, like one email being spam. Binomial is the count of yeses in n independent tries with the same p, like how many of twenty emails are spam; its table comes from counting the ways and multiplying the chances. Uniform is any value in a range being equally likely, like a random point on a line between 0 and 1. Normal is the bell curve, the shape you get when many small independent effects add up, which is why heights and measurement errors look like it and why a model's errors often do. A single exact value of a normal variable has probability zero because there are infinitely many values and the total probability is one; what has a probability is a range, the area under the curve between two values, which is why every question about a continuous variable is about being between, below or above something. A seed fixes where the random generator starts, so running the simulation again gives exactly the same draws: that's what makes a printed result checkable and a bug repeatable. Change the seed and you get a different sample from the same distribution, which should tell the same story.
review_pool:
  - review-predict-bincount
  - review-mcq-bernoulli-or-binomial
  - review-mcq-area-not-height
  - review-bernoulli
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: name
    description: "Name the Bernoulli, binomial, uniform and normal distributions and what each one models"
  - id: simulate
    description: "Simulate draws from a distribution with a seeded generator"
  - id: histogram
    description: "Turn a sample into counts or a histogram and compare it with the formula"
  - id: density
    description: "Read probability as area under a density, and know a single value has none"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Module 1 counted chances with dice and a table of 1,000 people. This module is the probability and statistics that make a model's numbers mean something, and it starts with the objects everything else is built from: a **random variable**, a number that chance decides, and its **distribution**, the list of values it can take and how likely each is. Four distributions cover most of what a model meets, and every one of them can be simulated in a line of NumPy, which is how this topic checks every claim it makes.

The main resource is **OpenStax _Introductory Statistics 2e_**: chapter 4 on discrete random variables (sections 4.1 to 4.3, the binomial above all), section 5.2 on the uniform distribution, and chapter 6 on the normal (sections 6.1 and 6.2); about 40 minutes, skimming the worked examples. StatQuest's short video on probability distributions is the picture version. Watch for:

- **A table for counts, a curve for measurements:** probability mass for discrete, probability density for continuous.
- **The binomial's formula** counts the ways and multiplies the chances.
- **The 68-95-99.7 rule** for the normal: how much sits within one, two and three standard deviations.

</Intro>

<Resource index={{0}} />

<Recap>

- **A random variable** is a number whose value chance decides: a flip (0 or 1), a count of heads, a height. **Discrete** ones take separate values (counts); **continuous** ones take any value in a range (measurements). Its **distribution** says which values are possible and how likely each is.
- **A seeded generator.** `rng = np.random.default_rng(1)` makes a random-number generator that starts from the **seed** 1, so every run produces the same draws: a simulation you can check, and a bug you can repeat. Change the seed for a fresh sample. Pyodide and CPython give the same draws for the same seed.
- **Bernoulli(p):** one yes-or-no with chance `p` of yes. Simulate it with `rng.random(size) < p`, which is `True` with chance `p`. One email being spam; one patient testing positive.
- **Binomial(n, p):** the number of yeses in `n` independent tries, each with chance `p`. `rng.binomial(n, p, size)`. Its **probability mass function** (PMF), the table of chances for each count `k`, is `math.comb(n, k) * p**k * (1 - p)**(n - k)`: the number of ways to pick which tries are yeses, times the chance of one such pattern. For `n = 10, p = 0.3`: 0.028 for no heads, 0.121 for one, 0.233 for two, 0.267 for three (the most likely), and the whole table sums to 1.
- **Checking a simulation against the table:** `np.bincount(sample, minlength=n + 1) / len(sample)` is the fraction of draws at each value, the **empirical** PMF. With 100,000 draws it matches the formula to about three decimals. A **histogram** is the same idea for measurements: `np.histogram(sample, bins)` counts how many fall in each **bin** (interval), and a row of `#` per bin draws it as text.
- **Uniform(a, b):** any value between `a` and `b` equally likely; `rng.uniform(a, b, size)`. The chance of being below 0.25 on `[0, 1]` is 0.25; the chance of being **exactly** 0.25 is 0.
- **Density, not mass.** A continuous variable has infinitely many values, so a single one has probability zero. Its distribution is a **density** curve, and probability is the **area** under it between two values: all questions about a continuous variable are about ranges. The density's height is not a probability (it can be above 1).
- **Normal(μ, σ):** the bell curve with mean `μ` and standard deviation `σ`, the shape sums of many small independent effects make: heights, measurement errors, a model's errors. `rng.normal(mu, sigma, size)`. The **68-95-99.7 rule:** about 68 percent of draws lie within one `σ` of the mean, 95 within two, 99.7 within three ({RULE_TEXT} in the worked example's 100,000 draws).
- **In machine learning:** a classifier's output is the `p` of a Bernoulli; a count of errors in a test set is binomial; the normal is what least squares assumes about the errors (next topics make that exact), and the uniform is where random starting weights come from.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-count-the-heads.yaml",
    '''id: parsons-count-the-heads
type: parsons
rev: 1
prompt: |
  Put the lines in order to simulate 1,000 flips of a coin that lands heads with chance 0.6, using a seeded generator, and print the fraction of heads rounded to 2 places. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'rng = np.random.default_rng(0)'
  - 'flips = rng.random(1000) < 0.6'
  - 'print(round(float(flips.mean()), 2))'
distractors:
  - 'flips = rng.random(1000) < 1000'
explanation: |
  `rng.random(1000)` is a thousand numbers spread evenly between 0 and 1, so each is below 0.6 with chance 0.6: a thousand Bernoulli draws. Their mean is the fraction of heads, close to 0.6. The decoy compares with 1000, which every draw is below, so it would print 1.0: a coin that always lands heads.
skills: [simulate]
''',
)

write(
    "recall/mcq-which-distribution.yaml",
    '''id: mcq-which-distribution
type: mcq
rev: 1
prompt: |
  Out of 50 emails, each independently spam with chance 0.2, how many are spam? Which distribution models that count?
choices:
  - 'Normal, because 50 is a large number'
  - 'Uniform between 0 and 50, since any count is possible'
  - 'Binomial with `n = 50` and `p = 0.2`'
  - 'Bernoulli with `p = 0.2`'
answer: 2
explanation: |
  A count of yeses in a fixed number of independent tries with the same chance is binomial: 50 tries, chance 0.2 each. A single email is Bernoulli; the count of them is not. The counts aren't equally likely (10 is far likelier than 50), so not uniform; and while the binomial's shape is close to a bell here, it is a table of 51 probabilities, not a density.
skills: [name]
''',
)

write(
    "recall/predict-a-small-pmf.yaml",
    f'''id: predict-a-small-pmf
type: predict_output
rev: 1
prompt: |
  The binomial table for three fair flips, by the formula. What does the program print?
code: |
{block(PREDICT_PMF)}expected_output: |
{block(PREDICT_PMF_OUT)}explanation: |
  `math.comb(3, k)` counts the ways to choose which `k` of the three flips are heads: 1, 3, 3, 1. Each particular pattern of three flips has chance `0.5 ** 3 = 0.125`, so the table is the ways times 0.125: one head and two heads are three times as likely as none or all. The four probabilities add up to 1.
skills: [histogram]
''',
)

write(
    "recall/mcq-why-a-value-has-no-probability.yaml",
    '''id: mcq-why-a-value-has-no-probability
type: mcq
rev: 1
prompt: |
  Heights are modelled as normal with mean 170 and standard deviation 10. What is the probability that the next person is **exactly** 175.0 cm tall, and what does have a probability?
choices:
  - 'The density''s height at 175, which is about 0.035; a single value does have a probability'
  - 'Zero, because 175 is more than half a standard deviation from the mean'
  - 'About 0.68, by the 68-95-99.7 rule'
  - 'Zero: there are infinitely many possible heights, so one exact value has none; a range such as 174.5 to 175.5 has a probability, the area under the density between them'
answer: 3
explanation: |
  For a continuous variable, probability is area under the density, and the area over a single point is zero, whatever the density's height there. The question with an answer is about a range: between 174.5 and 175.5 the area is about 0.035, which is what a ruler that reads to the nearest centimetre is really asking. The 68 percent is the chance of being within one standard deviation, 160 to 180.
skills: [density]
''',
)

write(
    "recall/review-predict-bincount.yaml",
    f'''id: review-predict-bincount
type: predict_output
rev: 1
prompt: |
  Six simulated counts of heads, tallied. What does the program print?
code: |
{block(PREDICT_BINCOUNT)}expected_output: |
{block(PREDICT_BINCOUNT_OUT)}explanation: |
  `np.bincount` counts how often each value appears, from 0 up: one 0, one 1, three 2s and one 3 (`minlength=4` keeps a slot for every count up to 3 even when it's empty). Dividing by the number of draws turns the tally into an empirical PMF, which always sums to 1, and the tally itself sums to the number of draws.
skills: [histogram]
''',
)

write(
    "recall/review-mcq-bernoulli-or-binomial.yaml",
    '''id: review-mcq-bernoulli-or-binomial
type: mcq
rev: 1
prompt: |
  A test is positive for 8 percent of healthy people. Which is Bernoulli and which is binomial?
choices:
  - 'Whether one healthy person tests positive is Bernoulli with `p = 0.08`; how many of 200 healthy people test positive is binomial with `n = 200`, `p = 0.08`'
  - 'Both are Bernoulli, because each test is a yes or a no'
  - 'Both are binomial, because there is a probability involved'
  - 'One person is binomial with `n = 1`; 200 people is normal'
answer: 0
explanation: |
  One yes-or-no is Bernoulli; a count of yeses over a fixed number of independent tries is binomial. (A Bernoulli is a binomial with `n = 1`, which is why the second half of the last choice is the only thing wrong with it: 200 is still a count, so binomial, even though its shape is near a bell.)
skills: [name]
''',
)

write(
    "recall/review-mcq-area-not-height.yaml",
    '''id: review-mcq-area-not-height
type: mcq
rev: 1
prompt: |
  A density curve for a uniform variable on `[0, 0.5]` is flat at height 2. Is that a mistake?
choices:
  - 'Yes: a probability can''t be above 1'
  - 'No: a density''s height isn''t a probability; the area under it is, and a flat 2 over a width of 0.5 gives an area of exactly 1'
  - 'Yes: a uniform density is always at height 1'
  - 'No, but only because the variable is discrete'
answer: 1
explanation: |
  Probability is area under a density, and the total area must be 1. Over a range of width 0.5 that takes a height of 2. Heights above 1 are normal for narrow distributions; it's areas that stay between 0 and 1. The variable is continuous, which is exactly why there's a density and not a table.
skills: [density]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-four-distributions-simulated/exercise.yaml",
    f'''id: example-four-distributions-simulated
stage: worked_example
rev: 1
title: "Four distributions, simulated"
prompt: |
  This program simulates a Bernoulli, a binomial, a uniform and a normal random variable with a seeded generator, and checks each against what the formulas say. Press **Run**, then read how each part works.
steps:
  - label: "A seeded generator and ten Bernoulli flips"
    lines: "5-8"
    note: "`default_rng(1)` is a random-number generator started from the seed 1, so it gives the same draws every run, in the browser and anywhere else. `rng.random(10)` is ten numbers spread evenly between 0 and 1, and each is below 0.3 with chance 0.3: ten Bernoulli draws, shown as 0s and 1s, with their count."
  - label: "A binomial, against its formula"
    lines: "10-16"
    note: "`rng.binomial(10, 0.3, size=100000)` is a hundred thousand counts of heads in ten flips. `np.bincount` tallies how many counts were 0, 1, 2, and so on; divided by the number of draws, that's the **empirical** PMF. Beside it, the formula: the number of ways to choose which `k` flips are heads, times the chance of one such pattern. They agree to about three decimals, and the row of `#` draws the table: three heads is the most likely."
  - label: "A uniform, and a value with no probability"
    lines: "18-19"
    note: "`rng.uniform(0, 1, ...)` is any value between 0 and 1, equally likely. A quarter of the draws are below 0.25, and **none** is exactly 0.25: a continuous variable has infinitely many values, so one exact value has probability zero, and only ranges have probabilities."
  - label: "A normal, and the 68-95-99.7 rule"
    lines: "21-25"
    note: "`rng.normal(170, 10, ...)` draws heights from a bell curve with mean 170 and standard deviation 10; the sample's own mean and standard deviation come out as 170.0 and 10.0. The fraction within one, two and three standard deviations of the mean is {RULE_TEXT}: the 68-95-99.7 rule that every normal obeys, whatever its mean and spread."
''',
)
write("exercises/example-four-distributions-simulated/solution.py", EXAMPLE)
write(
    "exercises/example-four-distributions-simulated/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints ten flips, a binomial table against its formula, a uniform check and the 68-95-99.7 rule."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-binomial-pmf/exercise.yaml",
    f'''id: fill-binomial-pmf
stage: fill_in
rev: 1
title: "The binomial's table"
prompt: |
  `binomial_pmf(k, n, p)` should return the chance of exactly `k` yeses in `n` independent tries that each succeed with chance `p`: the number of ways to choose which tries succeed, times `p` for each success, times `1 - p` for each failure. Replace each `...` so the program prints the table for ten flips at 0.3 and shows it sums to 1:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "Each of the `k` successes contributes a factor of `p`: `p**k`."
  - "The failures are the other `n - k` tries."
skills: [histogram, name]
''',
)
write("exercises/fill-binomial-pmf/starter.py", FILL_STARTER)
write("exercises/fill-binomial-pmf/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-binomial-pmf/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the eleven rows and the total 1.0."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_known_values():
    """Three fair flips: no heads 0.125, one head 0.375; a certain try gives 1 for k = n and 0 otherwise."""
    binomial_pmf = function("binomial_pmf")
    assert abs(binomial_pmf(0, 3, 0.5) - 0.125) < 1e-12
    assert abs(binomial_pmf(1, 3, 0.5) - 0.375) < 1e-12
    assert binomial_pmf(5, 5, 1.0) == 1 and binomial_pmf(4, 5, 1.0) == 0
''',
)
write("exercises/fill-binomial-pmf/wrong/no-ways.py", FILL_NO_COMB)
write(
    "exercises/fill-binomial-pmf/wrong/typed-in.py",
    "import math\n\n\ndef binomial_pmf(k, n, p):\n    return 0.028 if k == 0 else 0.121\n\n\n"
    + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-text-histogram/exercise.yaml",
    f'''id: write-text-histogram
stage: write
rev: 1
title: "A histogram in text"
prompt: |
  Write `histogram(sample, bins)`, which counts the sample into the bins with `np.histogram(sample, bins=bins)` and prints one line per bin: the bin's left and right edges, each formatted `6.1f`, then a space and one `#` for every percent of the sample in that bin (`round(count / len(sample) * 100)`). Then draw 10,000 standard normal draws from the starter's generator into the bins `np.arange(-4, 5, 1.0)`:

  ```
{block(WRITE_OUT)}  ```

  The bell shape is the normal distribution; the two middle bins hold about 34 percent each, which is the 68 in the 68-95-99.7 rule.
hints:
  - "`np.histogram` returns the counts and the bin edges; there is one more edge than there are counts, so pair `edges[:-1]` with `edges[1:]`."
  - "An f-string can format a number: `f\\"{{left:6.1f}}\\"`."
skills: [histogram, simulate]
''',
)
write("exercises/write-text-histogram/starter.py", WRITE_STARTER)
write("exercises/write-text-histogram/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-text-histogram/test_exercise.py",
    f'''import numpy as np

from checks import function, printed, run


def test_the_output():
    """Prints eight bins with a bell of hashes."""
    out = run()
    assert out == {WRITE_OUT!r}, f"Your program printed:\\n{{out}}"


def test_a_known_sample():
    """Two bins over a sample that splits 75 to 25 print 75 and 25 hashes."""
    histogram = function("histogram")
    sample = np.array([0.1, 0.2, 0.3, 0.6, 0.4, 0.2, 0.9, 0.3])
    out = printed(histogram, sample, np.array([0.0, 0.5, 1.0]))
    assert out == "   0.0 to    0.5 " + "#" * 75 + "\\n   0.5 to    1.0 " + "#" * 25 + "\\n", out
''',
)
write(
    "exercises/write-text-histogram/wrong/counts-not-percent.py",
    WRITE_SOLUTION.replace("'#' * round(count / len(sample) * 100)", "'#' * round(count / 100)"),
)
write(
    "exercises/write-text-histogram/wrong/typed-in.py",
    WRITE_STARTER + "\n\ndef histogram(sample, bins):\n    pass\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof --------------------------------------------------------------------------------

write(
    "exercises/build-check-a-simulation/exercise.yaml",
    f'''id: build-check-a-simulation
stage: build
rev: 1
title: "Check a simulation against the formulas"
prompt: |
  Starting from a blank editor, write the tools that check a simulation against what the formulas say:

  - `binomial_pmf(k, n, p)`: the chance of exactly `k` yeses in `n` tries.
  - `empirical_pmf(sample, n)`: the fraction of the draws at each value from 0 to `n`, as an array of `n + 1` numbers (use `np.bincount` with `minlength=n + 1`).
  - `largest_gap(sample, n, p)`: the largest absolute difference between the empirical PMF of `sample` and the formula's, over all values.
  - `within(sample, center, spread)`: the fractions of `sample` that lie within 1, 2 and 3 spreads of `center`, as a list of three floats.

  Then, with `rng = np.random.default_rng(1)`, draw 100,000 binomial counts for `n = 10, p = 0.3` and 100,000 normal draws with mean 170 and spread 10 (in that order), and print the first four entries of the empirical PMF rounded to 3, whether the largest gap is below 0.003, and the three fractions rounded to 3:

  ```
{block(BUILD_OUT)}  ```

  The checks call your functions on other samples whose answers are known exactly.
skills: [simulate, histogram, density]
''',
)
write("exercises/build-check-a-simulation/starter.py", "")
write("exercises/build-check-a-simulation/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-check-a-simulation/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the empirical PMF's start, the gap check and the three fractions."""
    assert run() == {BUILD_OUT!r}


def test_binomial_pmf():
    """Three fair flips give 0.125, 0.375, 0.375, 0.125, and every table sums to 1."""
    binomial_pmf = function("binomial_pmf")
    assert np.allclose([binomial_pmf(k, 3, 0.5) for k in range(4)], [0.125, 0.375, 0.375, 0.125])
    assert abs(sum(binomial_pmf(k, 7, 0.2) for k in range(8)) - 1) < 1e-12


def test_empirical_pmf_and_gap():
    """A hand-made sample gives exact fractions, including an empty slot, and its gap from a formula is what it should be."""
    empirical_pmf = function("empirical_pmf")
    largest_gap = function("largest_gap")
    sample = np.array([0, 1, 1, 2, 2, 2, 2, 0])
    assert np.allclose(empirical_pmf(sample, 3), [0.25, 0.25, 0.5, 0.0])
    # Against n = 3, p = 0.5 the formula is [0.125, 0.375, 0.375, 0.125]; the largest gap is 0.5 - 0.375.
    assert abs(largest_gap(sample, 3, 0.5) - 0.125) < 1e-12


def test_within():
    """Values 0 to 9 around a center of 4.5 with spread 2: 4 of 10 within one spread, 8 within two, all within three."""
    within = function("within")
    assert within(np.arange(10.0), 4.5, 2.0) == [0.4, 0.8, 1.0]
''',
)
write("exercises/build-check-a-simulation/wrong/no-ways.py", BUILD_NO_COMB)
write("exercises/build-check-a-simulation/wrong/divides-by-bins.py", BUILD_DIVIDES_BY_BINS)
write("exercises/build-check-a-simulation/wrong/one-spread-only.py", BUILD_WITHIN_LE)
write(
    "exercises/build-check-a-simulation/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def binomial_pmf(k, n, p):\n    return 0.25\n\n\n"
    + "def empirical_pmf(sample, n):\n    return np.zeros(n + 1) + 0.25\n\n\n"
    + "def largest_gap(sample, n, p):\n    return 0.0\n\n\n"
    + "def within(sample, center, spread):\n    return [0.683, 0.954, 0.997]\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-dice-report/exercise.yaml",
    f'''id: debug-dice-report
stage: debug
rev: 1
title: "A dice simulation that can't roll a six"
prompt: |
  This program simulates 60,000 rolls of a die and the number of sixes in four rolls, and should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the first line shows the die never lands on 6, because `rng.integers(low, high)` stops **before** `high`, so `roll` must ask for `integers(1, 7)`. Fix that, and `sixes_pmf` still disagrees with the simulation from `k = 1` on: the chance of a pattern with `k` sixes is `(1/6)` for each six and `(5/6)` for each of the **other** `4 - k` rolls, not for `k` of them.
skills: [simulate, histogram]
''',
)
write("exercises/debug-dice-report/starter.py", DEBUG_STARTER)
write("exercises/debug-dice-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-dice-report/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the six faces' fractions and the table of sixes in four rolls."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_die_has_six_faces():
    """roll produces every face from 1 to 6 and nothing else."""
    roll = function("roll")
    faces = set(np.unique(roll(np.random.default_rng(0), 10000)).tolist())
    assert faces == {{1, 2, 3, 4, 5, 6}}


def test_the_table_sums_to_one():
    """sixes_pmf's five entries sum to 1, and one six in four rolls has chance 0.386."""
    sixes_pmf = function("sixes_pmf")
    assert abs(sum(sixes_pmf(k) for k in range(5)) - 1) < 1e-12
    assert abs(sixes_pmf(1) - 0.3858) < 0.001
''',
)
write("exercises/debug-dice-report/wrong/range-only.py", DEBUG_RANGE_ONLY)
write(
    "exercises/debug-dice-report/wrong/typed-in.py",
    "import numpy as np\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise ------------------------------------------------------------------

write(
    "exercises/review-bernoulli/exercise.yaml",
    f'''id: review-bernoulli
stage: review_code
rev: 1
title: "Bernoulli draws, from memory"
prompt: |
  Write `bernoulli(rng, p, size)`, which returns `size` draws of 0 or 1 (as integers) that are 1 with chance `p`, using the generator's `random`. Then print the first eight of 100,000 draws at `p = 0.3` from the starter's generator and their mean rounded to 2 places:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [simulate]
''',
)
write("exercises/review-bernoulli/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-bernoulli/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-bernoulli/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints eight draws and a mean of 0.3."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_edges_and_values():
    """p = 0 gives all zeros, p = 1 all ones, and the draws are only 0s and 1s."""
    bernoulli = function("bernoulli")
    rng = np.random.default_rng(9)
    assert bernoulli(rng, 0.0, 50).sum() == 0
    assert bernoulli(rng, 1.0, 50).sum() == 50
    draws = bernoulli(rng, 0.5, 1000)
    assert set(np.unique(draws).tolist()) <= {{0, 1}}
''',
)
write(
    "exercises/review-bernoulli/wrong/always-half.py",
    REVIEW_CODE_STARTER + '''

def bernoulli(rng, p, size):
    return (rng.random(size) < 0.5).astype(int)


draws = bernoulli(rng, 0.3, 100000)
print(draws[:8], round(float(draws.mean()), 2))
''',
)
write(
    "exercises/review-bernoulli/wrong/typed-in.py",
    REVIEW_CODE_STARTER + "\n\ndef bernoulli(rng, p, size):\n    return np.zeros(size, dtype=int)\n\n\n" + f"print({REVIEW_CODE_OUT.strip()!r})\n",
)

print("ml.prob.distributions written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
