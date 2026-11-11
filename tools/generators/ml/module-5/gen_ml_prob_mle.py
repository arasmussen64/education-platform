"""Writes the topic ml.prob.maximum-likelihood (Module 5's fourth topic). Run
from the repository root under uv (python -m uv run python <this file>), so
every program's expected output is captured from CPython rather than typed
in. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.prob.maximum-likelihood")


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

heads, flips = 6, 8
ps = np.linspace(0.01, 0.99, 99)
likelihood = ps**heads * (1 - ps) ** (flips - heads)
print(round(float(ps[likelihood.argmax()]), 2), round(float(likelihood.max()), 5))
log_likelihood = heads * np.log(ps) + (flips - heads) * np.log(1 - ps)
print(round(float(ps[log_likelihood.argmax()]), 2), heads / flips)

p = 0.5
for step in range(200):
    slope = heads / p - (flips - heads) / (1 - p)
    p = p + 0.01 * slope
print(round(p, 4))

rng = np.random.default_rng(6)
x = rng.normal(170, 10, size=1000)
mus = np.linspace(165, 175, 101)
ll = np.array([-((x - mu) ** 2).sum() / (2 * 10**2) for mu in mus])
print(round(float(mus[ll.argmax()]), 1), round(float(x.mean()), 1))
print(round(float(np.sqrt(((x - x.mean()) ** 2).mean())), 2), round(float(x.std()), 2))

y = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])
print(round(float(np.prod(np.where(y == 1, p_hat, 1 - p_hat))), 4))
print(round(float(-np.sum(y * np.log(p_hat) + (1 - y) * np.log(1 - p_hat))), 4), round(-np.log(0.3024), 4))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
lines = EXAMPLE_OUT.splitlines()
assert lines[0].startswith("0.75 ") and lines[1] == "0.75 0.75" and lines[2] == "0.75", EXAMPLE_OUT
assert lines[3].split()[0] == lines[3].split()[1] and lines[4].split()[0] == lines[4].split()[1], EXAMPLE_OUT
assert lines[5] == "0.3024" and lines[6] == "1.196 1.196", EXAMPLE_OUT
assert "e-" not in EXAMPLE_OUT
MU_HAT = lines[3].split()[0]
SIGMA_HAT = lines[4].split()[0]
LMAX = lines[0].split()[1]
NLL = lines[6].split()[0]  # minus the log of 0.3024, which is the cross-entropy sum

# --- the fill-in --------------------------------------------------------------------------

FILL_HEAD = '''import numpy as np


def negative_log_likelihood(p, heads, flips):
    return -(heads * np.log(p) + (flips - heads) * np.log(1 - P))


def fit_coin(heads, flips, rate=0.01, steps=500):
    p = 0.5
    for step in range(steps):
        slope = -heads / p + (flips - heads) / (1 - p)
        p = p - rate * SLOPE
    return p


print(round(negative_log_likelihood(0.75, 6, 8), 4), round(negative_log_likelihood(0.5, 6, 8), 4))
print(round(fit_coin(6, 8), 4), round(fit_coin(3, 10), 4), round(fit_coin(50, 100), 4))
'''
FILL_SOLUTION = FILL_HEAD.replace("np.log(1 - P)", "np.log(1 - p)").replace("rate * SLOPE", "rate * slope")
FILL_STARTER = FILL_HEAD.replace("np.log(1 - P)", "np.log(1 - ...)").replace("rate * SLOPE", "rate * ...")
FILL_ASCENT = FILL_SOLUTION.replace("        p = p - rate * slope", "        p = p + rate * slope")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT == "4.4987 5.5452\n0.75 0.3 0.5\n", FILL_OUT
crash_or_wrong = subprocess.run([sys.executable, "-c", FILL_ASCENT], capture_output=True, text=True)
assert crash_or_wrong.returncode != 0 or crash_or_wrong.stdout != FILL_OUT

# --- the write ------------------------------------------------------------------------------

WRITE_STARTER = '''import numpy as np

rng = np.random.default_rng(6)
x = rng.normal(170, 10, size=1000)
'''
WRITE_SOLUTION = WRITE_STARTER + '''

def mle_normal(x):
    mu = x.mean()
    sigma = np.sqrt(((x - mu) ** 2).mean())
    return float(mu), float(sigma)


mu, sigma = mle_normal(x)
print(round(mu, 2), round(sigma, 2))
print(round(mu, 2) == round(float(x.mean()), 2), round(sigma, 2) == round(float(x.std()), 2))
print(mle_normal(np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT.splitlines()[1] == "True True" and WRITE_OUT.splitlines()[2] == "(5.0, 2.0)", WRITE_OUT

# --- the build --------------------------------------------------------------------------------

BUILD_SOLUTION = '''import numpy as np


def log_likelihood_coin(p, heads, flips):
    return heads * np.log(p) + (flips - heads) * np.log(1 - p)


def mle_coin(heads, flips):
    ps = np.linspace(0.001, 0.999, 999)
    return float(ps[log_likelihood_coin(ps, heads, flips).argmax()])


def nll_bernoulli(p_hat, y):
    return float(-np.sum(y * np.log(p_hat) + (1 - y) * np.log(1 - p_hat)))


def nll_normal(x, mu, sigma):
    return float(len(x) * np.log(sigma) + ((x - mu) ** 2).sum() / (2 * sigma**2))


print("coin", mle_coin(6, 8), mle_coin(3, 10))
y = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])
print("labels", round(nll_bernoulli(p_hat, y), 4), round(float(-np.log(np.prod(np.where(y == 1, p_hat, 1 - p_hat)))), 4))
x = np.array([168.0, 171.0, 174.0, 167.0, 170.0])
print("normal", [round(nll_normal(x, mu, 3.0), 3) for mu in (168.0, 170.0, 172.0)])
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT.startswith("coin 0.75 0.3\nlabels 1.196 1.196\nnormal ["), BUILD_OUT
normal_values = [float(v) for v in BUILD_OUT.splitlines()[2][len("normal [") : -1].split(", ")]
assert normal_values[1] < normal_values[0] and normal_values[1] < normal_values[2], normal_values
BUILD_NO_TAILS = BUILD_SOLUTION.replace("    return heads * np.log(p) + (flips - heads) * np.log(1 - p)", "    return heads * np.log(p)")
BUILD_SIGN = BUILD_SOLUTION.replace("    return float(-np.sum(y * np.log(p_hat) + (1 - y) * np.log(1 - p_hat)))", "    return float(np.sum(y * np.log(p_hat) + (1 - y) * np.log(1 - p_hat)))")
BUILD_NO_SIGMA_TERM = BUILD_SOLUTION.replace("    return float(len(x) * np.log(sigma) + ((x - mu) ** 2).sum() / (2 * sigma**2))", "    return float(((x - mu) ** 2).sum() / 2)")
for wrong in (BUILD_NO_TAILS, BUILD_SIGN, BUILD_NO_SIGMA_TERM):
    assert out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def coin_likelihood(ps, heads, flips):
    return ps**heads * (1 - ps) ** (flips - heads)


def normal_log_likelihood(mus, x, sigma):
    return np.array([-((x - mu) ** 2).sum() / (2 * sigma**2) for mu in mus])


ps = np.linspace(0.01, 0.99, 99)
print("coin", round(float(ps[coin_likelihood(ps, 6, 8).argmax()]), 2))
rng = np.random.default_rng(6)
x = rng.normal(170, 10, size=1000)
mus = np.linspace(165, 175, 101)
print("normal", round(float(mus[normal_log_likelihood(mus, x, 10).argmax()]), 1))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("    return ps**heads * (1 - ps) ** (flips - heads)", "    return ps**flips").replace(
    "    return np.array([-((x - mu) ** 2).sum() / (2 * sigma**2) for mu in mus])",
    "    return np.array([((x - mu) ** 2).sum() / (2 * sigma**2) for mu in mus])",
)
DEBUG_COIN_ONLY = DEBUG_SOLUTION.replace(
    "    return np.array([-((x - mu) ** 2).sum() / (2 * sigma**2) for mu in mus])",
    "    return np.array([((x - mu) ** 2).sum() / (2 * sigma**2) for mu in mus])",
)
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == f"coin 0.75\nnormal {MU_HAT}\n", (DEBUG_OUT, MU_HAT)
assert out(DEBUG_STARTER) == "coin 0.99\nnormal 165.0\n" or out(DEBUG_STARTER) == "coin 0.99\nnormal 175.0\n", out(DEBUG_STARTER)
assert out(DEBUG_COIN_ONLY) != DEBUG_OUT

# --- predict items -------------------------------------------------------------------------------

PREDICT_LIKELIHOOD = '''for p in (0.5, 0.9, 1.0):
    print(p, round(p**2, 2), round(p**2 * (1 - p), 3))
'''
PREDICT_LIKELIHOOD_OUT = out(PREDICT_LIKELIHOOD)
print("predict likelihood:\n" + PREDICT_LIKELIHOOD_OUT)
assert PREDICT_LIKELIHOOD_OUT == "0.5 0.25 0.125\n0.9 0.81 0.081\n1.0 1.0 0.0\n", PREDICT_LIKELIHOOD_OUT

REVIEW_SEQUENCE = '''import numpy as np

flips = np.array([1, 1, 0, 1])
for p in (0.5, 0.75):
    likelihood = np.prod(np.where(flips == 1, p, 1 - p))
    print(p, round(float(likelihood), 4), round(float(np.log(likelihood)), 4))
'''
REVIEW_SEQUENCE_OUT = out(REVIEW_SEQUENCE)
print("review sequence:\n" + REVIEW_SEQUENCE_OUT)
assert REVIEW_SEQUENCE_OUT == "0.5 0.0625 -2.7726\n0.75 0.1055 -2.2493\n", REVIEW_SEQUENCE_OUT

REVIEW_CODE_STARTER = "import numpy as np\n"
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def mle_coin(heads, flips):
    ps = np.linspace(0.001, 0.999, 999)
    log_likelihood = heads * np.log(ps) + (flips - heads) * np.log(1 - ps)
    return float(ps[log_likelihood.argmax()])


print(mle_coin(6, 8), mle_coin(3, 10), mle_coin(1, 1000))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "0.75 0.3 0.001\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.prob.maximum-likelihood
kind: topic
status: ready
title: "Maximum likelihood"
summary: "The likelihood of data under a model, why logs turn it into a sum, fitting a coin and a normal by maximizing it, and why least squares and cross-entropy are maximum likelihood in disguise."
prerequisites: [ml.prob.expectation-and-variance, ml.calc.loss-functions]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Write the likelihood of a dataset under a model with a parameter."
  - "Take the log, and find the maximum by calculus and by gradient descent."
  - "Fit a coin's bias and a normal's mean and spread by maximum likelihood, and check against the sample statistics."
  - "Say why least squares and cross-entropy are maximum-likelihood losses."
# Linked, never copied or embedded: StatQuest's videos are under the standard
# YouTube licence; Wikipedia is CC BY-SA 4.0; NumPy's documentation is under
# the NumPy licence (BSD-3-Clause).
resources:
  - title: "StatQuest: Maximum Likelihood, clearly explained!!! (Josh Starmer)"
    url: https://www.youtube.com/watch?v=XepXtl9YKwc
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "Wikipedia: Maximum likelihood estimation (the sections Principles and Examples)"
    url: https://en.wikipedia.org/wiki/Maximum_likelihood_estimation
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "numpy.argmax (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.argmax.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-a-coin-and-a-normal-by-likelihood
  - parsons-log-likelihood-of-a-coin
  - mcq-what-a-likelihood-is
  - predict-two-heads
  - mcq-why-the-log
  - mcq-what-cross-entropy-assumes
  - fill-fit-a-coin-by-descent
  - write-mle-normal
prove:
  build: build-likelihoods-and-losses
  debug: debug-likelihood-report
  explain:
    prompt: |
      A teammate asks why the loss for a regression is squared error and the loss for a classifier is cross-entropy: "who decided that?" In your own words: what is a likelihood, and what does maximum likelihood choose? Why work with the log of it? Show why minimizing squared error is the same as maximizing the likelihood when the errors are normal, and why cross-entropy is the negative log-likelihood of the labels. And what is each loss assuming about the data?
    rubric:
      - id: likelihood
        required: true
        description: "The likelihood is the probability of the data you saw, read as a function of the model's parameter; maximum likelihood picks the parameter under which the data was most probable (6 heads in 8 flips: p = 0.75)."
      - id: log
        required: true
        description: "The log is increasing, so it has the same maximizer; it turns a product of many small probabilities into a sum that neither underflows nor needs the product rule to differentiate; the negative log-likelihood is a loss to minimize."
      - id: squared-error
        required: true
        description: "If each y is the model's prediction plus normal noise with spread sigma, the log-likelihood of the data is a constant minus the sum of squared errors over 2 sigma squared, so maximizing it is minimizing the sum of squared errors: least squares is maximum likelihood under normal errors."
      - id: cross-entropy
        required: true
        description: "If each label is a Bernoulli with the model's p, the probability of the labels is the product of p for the ones and 1 - p for the zeros, whose negative log is exactly the cross-entropy: minimizing it maximizes the likelihood of the labels. Squared error assumes normal noise, cross-entropy assumes independent Bernoulli labels; when the assumption is wrong, so is the loss."
    model_answer: |
      A likelihood is the probability of the data you actually saw, written as a function of the thing you don't know. Six heads in eight flips has probability p to the sixth times one minus p squared, and reading that as a function of p is the likelihood of p. Maximum likelihood chooses the parameter under which the data was most probable: 0.75 here, which is where the derivative is zero and where a grid search peaks. We work with the log because the log is increasing, so it has the same maximizer, and because it turns a product of many small probabilities, which would underflow to zero and be a nightmare to differentiate, into a sum of logs, which does neither. Minus the log-likelihood is then a loss to minimize, and that is where the two losses come from. Suppose each regression target is the model's prediction plus normal noise with spread sigma. The probability density of one observation is proportional to exp of minus the squared error over two sigma squared, so the log-likelihood of all of them is a constant minus the sum of squared errors over two sigma squared. Making that as large as possible is making the sum of squared errors as small as possible: least squares is maximum likelihood under normal errors. Now suppose each label is a Bernoulli with the model's probability p. The probability of the labels you saw is the product of p for every one and one minus p for every zero, and minus its log is minus the sum of y log p plus one minus y log one minus p, which is the cross-entropy exactly. So each loss is a statement about the data: squared error says the noise is normal with the same spread everywhere, cross-entropy says the labels are independent coin flips with the model's probabilities. Nobody decided; the assumption did, and when the assumption is wrong, say heavy-tailed noise, the loss is the wrong one too.
review_pool:
  - review-predict-a-sequence
  - review-mcq-likelihood-is-not-probability-of-p
  - review-mcq-divide-by-n
  - review-mcq-what-squared-error-assumes
  - review-mle-coin
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: likelihood
    description: "Write the likelihood and the log-likelihood of data under a model with a parameter"
  - id: maximize
    description: "Find the maximum-likelihood parameter by a grid, by calculus or by descent on the negative log-likelihood"
  - id: fit
    description: "Fit a coin's bias and a normal's mean and spread by maximum likelihood, and check against the sample statistics"
  - id: losses
    description: "Say why least squares and cross-entropy are negative log-likelihoods, and what each assumes"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Module 4 handed you two losses and said "use these". This topic says where they came from. A model with a parameter gives every possible dataset a probability; the **likelihood** is that probability for the data you actually saw, read as a function of the parameter; and **maximum likelihood** picks the parameter that made your data most probable. Taking logs turns the product into a sum, and minus that sum is a loss: squared error when the noise is normal, cross-entropy when the labels are coin flips. The losses were never arbitrary.

The main resource is **StatQuest's _Maximum Likelihood, clearly explained_**, seven minutes that slide a normal curve across some data until it fits best; then the _Principles_ and _Examples_ sections of Wikipedia's article for the same idea with the formulas, about 20 minutes. Watch for:

- **The data is fixed and the parameter moves:** a likelihood is not the probability of the parameter.
- **The log turns products into sums** and leaves the maximizer where it was.
- **The normal's best mean is the sample mean**, and its best spread divides by `n`.

</Intro>

<Resource index={{0}} />

<Recap>

- **Likelihood.** For a model with parameter `θ`, `L(θ)` is the probability (or density) of the data you observed, with the data fixed and `θ` varying. Six heads in eight flips: `L(p) = p**6 * (1 - p)**2` (times a constant that doesn't depend on `p`). On a grid of 99 values of `p` it peaks at 0.75, where it is only {LMAX}: the data was unlikely under every `p`, and 0.75 is the least unlikely.
- **Maximum likelihood** picks the `θ` with the largest `L`. Three ways to find it: a **grid** (`np.linspace` and `argmax`), **calculus** (set the derivative of the log-likelihood to zero: `6/p - 2/(1 - p) = 0` gives `p = 6/8`), or **descent** on the negative log-likelihood with Module 4's loop (200 steps from 0.5 reach 0.75).
- **Why the log.** `log L(θ)` has the same maximizer, because the log is increasing; it turns a product of many small probabilities into a sum of logs, which doesn't underflow to zero and differentiates term by term. The **negative log-likelihood** (NLL) is a loss: smaller is better, and it is what every training loop minimizes whether it says so or not.
- **A coin:** the MLE of the bias is `heads / flips`. **A normal:** the MLE of the mean is the sample mean (`x.mean()`, {MU_HAT} for the worked example's thousand heights), and the MLE of the spread divides the squared deviations by `n`, which is NumPy's default `x.std()` ({SIGMA_HAT}); the textbook's `n - 1` version is a different, slightly larger estimate, not the maximum-likelihood one.
- **Least squares is maximum likelihood** when each target is the prediction plus normal noise with the same spread: the log-density of one observation is a constant minus `(y - ŷ)² / (2σ²)`, so the log-likelihood of all of them is a constant minus the sum of squared errors over `2σ²`. Maximizing it is minimizing the sum of squared errors. The normal assumption is the fine print.
- **Cross-entropy is maximum likelihood** when each label is a Bernoulli with the model's `p`: the probability of the labels is the product of `p` for the ones and `1 - p` for the zeros (0.3024 for the worked example's four labels), and its negative log, {NLL}, is exactly the cross-entropy sum `-Σ [y log p + (1 - y) log(1 - p)]`. Minimizing cross-entropy maximizes the likelihood of the labels.
- **What each loss assumes:** squared error, normal noise of one spread everywhere; cross-entropy, independent coin-flip labels. When the data breaks the assumption (a few wild outliers, say), the loss is the wrong one, and a different likelihood gives a different loss.
- **In machine learning:** "minimize the loss" and "maximize the likelihood" are the same sentence; `model.fit` in any library is this topic with the gradient supplied by backpropagation; and Bayes' rule from the last topic is the same likelihood multiplied by a prior, which the next modules use when the prior matters.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-log-likelihood-of-a-coin.yaml",
    '''id: parsons-log-likelihood-of-a-coin
type: parsons
rev: 1
prompt: |
  Put the lines in order to find, on a grid, the bias that makes 3 heads in 10 flips most probable, printing `0.3`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'ps = np.linspace(0.01, 0.99, 99)'
  - 'log_likelihood = 3 * np.log(ps) + 7 * np.log(1 - ps)'
  - 'print(round(float(ps[log_likelihood.argmax()]), 2))'
distractors:
  - 'log_likelihood = 3 * np.log(ps) + 7 * np.log(ps)'
explanation: |
  Three heads contribute `3 log p` and seven tails `7 log(1 - p)`; the sum peaks at `p = 0.3`, the fraction of heads. The decoy charges the tails as if they were heads too, which makes the log-likelihood `10 log p`, largest at the biggest `p` on the grid: a coin that always lands heads, for data that was mostly tails.
skills: [likelihood, maximize]
''',
)

write(
    "recall/mcq-what-a-likelihood-is.yaml",
    '''id: mcq-what-a-likelihood-is
type: mcq
rev: 1
prompt: |
  You flip a coin 8 times and see 6 heads. `L(p) = p**6 * (1 - p)**2` is the coin's likelihood. What is `L(0.75) = 0.0111`?
choices:
  - 'The probability that the coin''s bias is 0.75'
  - 'The probability of seeing exactly that sequence of flips if the bias were 0.75: the data''s probability, read as a function of the parameter'
  - 'The fraction of the time the coin lands heads'
  - 'The probability that the bias is at least 0.75'
answer: 1
explanation: |
  A likelihood keeps the data fixed and lets the parameter move: it is how probable your observations were under each candidate `p`. It is not a probability of `p` itself (that needs a prior and Bayes' rule), and the likelihoods of different `p` don''t sum to 1. Maximum likelihood picks the `p` that made the data most probable, 0.75.
skills: [likelihood]
''',
)

write(
    "recall/predict-two-heads.yaml",
    f'''id: predict-two-heads
type: predict_output
rev: 1
prompt: |
  The likelihood of two heads in two flips, and of two heads then a tail, at three biases. What does the program print?
code: |
{block(PREDICT_LIKELIHOOD)}expected_output: |
{block(PREDICT_LIKELIHOOD_OUT)}explanation: |
  Two heads have probability `p²`: largest at `p = 1`, a coin that always lands heads, which is the maximum-likelihood estimate for that data however few the flips. Two heads then a tail have probability `p² (1 - p)`, which is 0 at `p = 1` (a coin that always lands heads can't produce a tail) and peaks at `p = 2/3`, the fraction of heads.
skills: [likelihood]
''',
)

write(
    "recall/mcq-why-the-log.yaml",
    '''id: mcq-why-the-log
type: mcq
rev: 1
prompt: |
  Why maximize the log-likelihood instead of the likelihood itself?
choices:
  - 'Because the log is increasing, so the same parameter maximizes both, and it turns a product of many small probabilities into a sum that neither underflows nor needs the product rule to differentiate'
  - 'Because the log-likelihood is always positive, which makes it easier to compare'
  - 'Because the log makes the maximum larger'
  - 'Because the likelihood of a continuous variable can''t be computed without a log'
answer: 0
explanation: |
  A thousand probabilities each below 1 multiply to something like `1e-300`, which a float can''t hold; their logs add to a manageable negative number, and each term differentiates on its own. Nothing about the answer changes, because the log keeps order: whatever made the likelihood largest makes its log largest. (Log-likelihoods are usually negative, not positive.)
skills: [maximize]
''',
)

write(
    "recall/mcq-what-cross-entropy-assumes.yaml",
    '''id: mcq-what-cross-entropy-assumes
type: mcq
rev: 1
prompt: |
  A classifier is trained by minimizing cross-entropy. Seen as maximum likelihood, what is that loss assuming about the labels?
choices:
  - 'That the labels are normally distributed around the model''s output'
  - 'That there are equally many 1s and 0s'
  - 'That each label is an independent Bernoulli draw with the model''s probability `p` for a 1, so the probability of all the labels is the product of `p` for the ones and `1 - p` for the zeros, and the cross-entropy is minus its log'
  - 'Nothing: cross-entropy is a convention with no model behind it'
answer: 2
explanation: |
  Minus the log of `Π p^y (1 - p)^(1 - y)` is `-Σ [y log p + (1 - y) log(1 - p)]`, the cross-entropy sum. So minimizing it maximizes the likelihood of the labels under the assumption that each is an independent coin flip with the model''s probability. The normal assumption belongs to squared error; nothing about the class balance is assumed.
skills: [losses]
''',
)

write(
    "recall/review-mcq-what-squared-error-assumes.yaml",
    '''id: review-mcq-what-squared-error-assumes
type: mcq
rev: 1
prompt: |
  Minimizing the sum of squared errors is maximum likelihood under which assumption about the data?
choices:
  - 'That the targets are 0s and 1s'
  - 'That each target is the model''s prediction plus normal noise with the same spread everywhere, so the log-likelihood is a constant minus the sum of squared errors over `2σ²`'
  - 'That the errors are all positive'
  - 'That the model is a straight line'
answer: 1
explanation: |
  A normal density is `exp(-(y - ŷ)² / (2σ²))` up to a constant, so the log-likelihood of independent normal errors is a constant minus the sum of squared errors over `2σ²`; making it largest means making the squared errors smallest. The model can be anything, a line or a network; the assumption is about the noise. When the noise has wild outliers, squared error is the wrong loss, because the normal said outliers are nearly impossible.
skills: [losses]
''',
)

write(
    "recall/review-predict-a-sequence.yaml",
    f'''id: review-predict-a-sequence
type: predict_output
rev: 1
prompt: |
  The likelihood and log-likelihood of the flips `1, 1, 0, 1` at two biases. What does the program print?
code: |
{block(REVIEW_SEQUENCE)}expected_output: |
{block(REVIEW_SEQUENCE_OUT)}explanation: |
  At `p = 0.5` every flip has probability 0.5, so the sequence has `0.5**4 = 0.0625`. At `p = 0.75` the three heads have 0.75 each and the tail 0.25: `0.75**3 * 0.25 = 0.1055`, larger, as it should be for the bias that matches the fraction of heads. The logs are negative numbers that keep the same order.
skills: [likelihood]
''',
)

write(
    "recall/review-mcq-likelihood-is-not-probability-of-p.yaml",
    '''id: review-mcq-likelihood-is-not-probability-of-p
type: mcq
rev: 1
prompt: |
  After 3 heads in 10 flips, the maximum-likelihood estimate of the bias is 0.3. Which statement is right?
choices:
  - '0.3 is the probability that the coin is fair'
  - 'The likelihoods of all the candidate biases add up to 1, like probabilities'
  - 'The coin''s bias is 0.3 with probability equal to the likelihood at 0.3'
  - '0.3 is the bias under which 3 heads in 10 was most probable; how probable each bias is would need a prior and Bayes'' rule'
answer: 3
explanation: |
  Maximum likelihood answers "which parameter made my data most probable?", not "how probable is each parameter?". The second question is the posterior of the last topic, prior times likelihood, normalized. The likelihoods themselves don''t sum to 1 across biases, and none of them is the probability that the coin is fair.
skills: [likelihood, maximize]
''',
)

write(
    "recall/review-mcq-divide-by-n.yaml",
    '''id: review-mcq-divide-by-n
type: mcq
rev: 1
prompt: |
  The maximum-likelihood estimate of a normal's spread from a sample divides the sum of squared deviations by `n`; the textbook's sample standard deviation divides by `n - 1`. Which does `np.std(x)` compute by default, and which is the maximum-likelihood one?
choices:
  - '`np.std` divides by `n - 1`, which is the maximum-likelihood estimate'
  - '`np.std` divides by `n`, which is the maximum-likelihood estimate; dividing by `n - 1` is a different estimate that comes out slightly larger'
  - 'They are the same number for any sample larger than 30'
  - '`np.std` divides by `n`, but the maximum-likelihood estimate divides by `n - 1`'
answer: 1
explanation: |
  NumPy''s default (`ddof=0`) divides by `n`, and that is what maximizing the normal''s likelihood gives. The `n - 1` version (`ddof=1`) corrects a small downward bias and is what Module 1''s textbook used; the two differ by the factor `sqrt(n / (n - 1))`, noticeable for small samples and not for large ones, but never identical.
skills: [fit]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-a-coin-and-a-normal-by-likelihood/exercise.yaml",
    f'''id: example-a-coin-and-a-normal-by-likelihood
stage: worked_example
rev: 1
title: "A coin and a normal, by likelihood"
prompt: |
  This program finds a coin's bias by maximum likelihood three ways, fits a normal's mean and spread the same way, and then shows that cross-entropy is a negative log-likelihood. Press **Run**, then read how each part works.
steps:
  - label: "The likelihood of six heads in eight"
    lines: "3-6"
    note: "`ps` is a grid of 99 candidate biases. For each, the probability of the observed flips is `p**6 * (1 - p)**2`. It peaks at 0.75, and the peak is tiny ({LMAX}): the data was improbable under every bias, and maximum likelihood picks the least improbable one."
  - label: "The log-likelihood, same peak"
    lines: "7-8"
    note: "`6 log p + 2 log(1 - p)` peaks at the same 0.75, because the log keeps order. It also equals `heads / flips`, which is what setting the derivative `6/p - 2/(1 - p)` to zero gives."
  - label: "Found by descent"
    lines: "10-14"
    note: "Module 4's loop, climbing the log-likelihood instead of descending a loss: the slope is `heads / p - tails / (1 - p)`, and 200 small steps from 0.5 arrive at 0.75. Minimizing the negative log-likelihood is the same loop with the signs flipped, which is what a training loop does."
  - label: "A normal's mean and spread"
    lines: "16-21"
    note: "A thousand heights from a normal. Over a grid of candidate means, the log-likelihood (a constant minus the sum of squared distances over `2σ²`) peaks at {MU_HAT}, which is the sample mean. The best spread is the root of the squared deviations divided by `n`, {SIGMA_HAT}, which is `x.std()` with NumPy's default: maximum likelihood is where that default comes from."
  - label: "Cross-entropy is a negative log-likelihood"
    lines: "23-26"
    note: "Four labels and a model's four probabilities. The probability of seeing those labels is the product of `p` for each 1 and `1 - p` for each 0: 0.3024. Its negative log, {NLL}, is exactly the cross-entropy sum from Module 4. Minimizing cross-entropy maximizes the likelihood of the labels; the loss was a likelihood all along."
''',
)
write("exercises/example-a-coin-and-a-normal-by-likelihood/solution.py", EXAMPLE)
write(
    "exercises/example-a-coin-and-a-normal-by-likelihood/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the coin's bias three ways, the normal's mean and spread, and the labels' likelihood against cross-entropy."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-fit-a-coin-by-descent/exercise.yaml",
    f'''id: fill-fit-a-coin-by-descent
stage: fill_in
rev: 1
title: "Fit a coin by descent"
prompt: |
  `negative_log_likelihood(p, heads, flips)` is the loss, and `fit_coin` descends it from `p = 0.5` using the slope of the negative log-likelihood, `-heads / p + tails / (1 - p)`. Replace each `...` so the program prints the loss at 0.75 and at 0.5 for six heads in eight, then the fitted biases for three coins:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The tails' term is `(flips - heads) * np.log(1 - p)`."
  - "Descent steps against the slope: `p - rate * slope`."
skills: [maximize, likelihood]
''',
)
write("exercises/fill-fit-a-coin-by-descent/starter.py", FILL_STARTER)
write("exercises/fill-fit-a-coin-by-descent/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-fit-a-coin-by-descent/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two losses and the three fitted biases."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_the_loss_is_lowest_at_the_fraction():
    """For 2 heads in 5 the loss is lower at 0.4 than at 0.3 or 0.5, and fit_coin lands within 0.001 of 0.4."""
    nll = function("negative_log_likelihood")
    fit_coin = function("fit_coin")
    assert nll(0.4, 2, 5) < nll(0.3, 2, 5) and nll(0.4, 2, 5) < nll(0.5, 2, 5)
    assert abs(fit_coin(2, 5) - 0.4) < 0.001
''',
)
write("exercises/fill-fit-a-coin-by-descent/wrong/ascent.py", FILL_ASCENT)
write(
    "exercises/fill-fit-a-coin-by-descent/wrong/typed-in.py",
    "import numpy as np\n\n\ndef negative_log_likelihood(p, heads, flips):\n    return 4.4987\n\n\ndef fit_coin(heads, flips, rate=0.01, steps=500):\n    return heads / flips\n\n\n"
    + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-mle-normal/exercise.yaml",
    f'''id: write-mle-normal
stage: write
rev: 1
title: "A normal's maximum-likelihood fit"
prompt: |
  Write `mle_normal(x)`, which returns the maximum-likelihood mean and spread of a sample as a pair of floats: the sample mean, and the square root of the mean squared deviation from it (dividing by `n`, not `n - 1`). Then print them for the starter's thousand heights rounded to 2 places, whether they equal `x.mean()` and `x.std()` rounded the same way, and the fit for `[2, 4, 4, 4, 5, 5, 7, 9]`:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`((x - mu) ** 2).mean()` divides by `n`."
  - "Return plain floats: `float(mu), float(sigma)`."
skills: [fit]
''',
)
write("exercises/write-mle-normal/starter.py", WRITE_STARTER)
write("exercises/write-mle-normal/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-mle-normal/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the fit, the two checks and the small sample's fit."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_divides_by_n():
    """For [1, 3] the spread is 1 (dividing by n), not root 2."""
    mle_normal = function("mle_normal")
    mu, sigma = mle_normal(np.array([1.0, 3.0]))
    assert mu == 2.0 and abs(sigma - 1.0) < 1e-12
''',
)
write(
    "exercises/write-mle-normal/wrong/divides-by-n-minus-one.py",
    WRITE_SOLUTION.replace("    sigma = np.sqrt(((x - mu) ** 2).mean())", "    sigma = np.sqrt(((x - mu) ** 2).sum() / (len(x) - 1))"),
)
write(
    "exercises/write-mle-normal/wrong/typed-in.py",
    WRITE_STARTER + "\n\ndef mle_normal(x):\n    return 5.0, 2.0\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof ----------------------------------------------------------------------------------

write(
    "exercises/build-likelihoods-and-losses/exercise.yaml",
    f'''id: build-likelihoods-and-losses
stage: build
rev: 1
title: "Likelihoods, and the losses they become"
prompt: |
  Starting from a blank editor, write:

  - `log_likelihood_coin(p, heads, flips)`: `heads * log(p) + tails * log(1 - p)`, for a number or an array of `p`.
  - `mle_coin(heads, flips)`: the `p` on the grid `np.linspace(0.001, 0.999, 999)` with the largest log-likelihood, as a float.
  - `nll_bernoulli(p_hat, y)`: the negative log-likelihood of labels `y` (1s and 0s) under predicted probabilities `p_hat`, as a float: `-Σ [y log p_hat + (1 - y) log(1 - p_hat)]`.
  - `nll_normal(x, mu, sigma)`: the negative log-likelihood of a sample under a normal with mean `mu` and spread `sigma`, dropping the constant: `n * log(sigma) + Σ (x - mu)² / (2 sigma²)`, as a float.

  Then print the coin fits for 6 heads in 8 and 3 in 10; the labels' negative log-likelihood for `y = [1, 0, 1, 1]` and `p_hat = [0.9, 0.2, 0.7, 0.6]` beside minus the log of the product of the matching probabilities (both rounded to 4); and `nll_normal` of the five heights `[168, 171, 174, 167, 170]` with `sigma = 3` at means 168, 170 and 172, rounded to 3:

  ```
{block(BUILD_OUT)}  ```

  The checks fit other coins, compare `nll_bernoulli` with Module 4's cross-entropy, and check `nll_normal` is lowest at the sample mean.
skills: [likelihood, maximize, fit, losses]
''',
)
write("exercises/build-likelihoods-and-losses/starter.py", "")
write("exercises/build-likelihoods-and-losses/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-likelihoods-and-losses/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the coin fits, the labels' likelihood two ways and three normal losses."""
    assert run() == {BUILD_OUT!r}


def test_coins():
    """The fitted bias is the fraction of heads, to the grid's resolution, for 1 in 4 and 99 in 100."""
    mle_coin = function("mle_coin")
    assert abs(mle_coin(1, 4) - 0.25) < 0.001
    assert abs(mle_coin(99, 100) - 0.99) < 0.001


def test_nll_bernoulli_is_the_cross_entropy_sum():
    """nll_bernoulli equals the summed cross-entropy, and is 4 log 2 for four labels at 0.5."""
    nll_bernoulli = function("nll_bernoulli")
    y = np.array([1.0, 1.0, 0.0, 1.0, 0.0])
    p = np.array([0.8, 0.6, 0.3, 0.9, 0.5])
    expected = -np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))
    assert abs(nll_bernoulli(p, y) - expected) < 1e-12
    assert abs(nll_bernoulli(np.full(4, 0.5), np.array([1.0, 0.0, 1.0, 0.0])) - 4 * np.log(2)) < 1e-12


def test_nll_normal_is_lowest_at_the_mean():
    """For [1, 2, 3, 6] the normal loss at the mean 3 is below the loss at 2 and at 4, and a larger sigma costs n log sigma."""
    nll_normal = function("nll_normal")
    x = np.array([1.0, 2.0, 3.0, 6.0])
    assert nll_normal(x, 3.0, 2.0) < nll_normal(x, 2.0, 2.0) and nll_normal(x, 3.0, 2.0) < nll_normal(x, 4.0, 2.0)
    assert abs(nll_normal(x, 3.0, 1.0) - (0 + 14 / 2)) < 1e-12
''',
)
write("exercises/build-likelihoods-and-losses/wrong/no-tails.py", BUILD_NO_TAILS)
write("exercises/build-likelihoods-and-losses/wrong/sign.py", BUILD_SIGN)
write("exercises/build-likelihoods-and-losses/wrong/no-sigma-term.py", BUILD_NO_SIGMA_TERM)
write(
    "exercises/build-likelihoods-and-losses/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def log_likelihood_coin(p, heads, flips):\n    return 0.0\n\n\n"
    + "def mle_coin(heads, flips):\n    return heads / flips\n\n\n"
    + "def nll_bernoulli(p_hat, y):\n    return 1.1961\n\n\n"
    + "def nll_normal(x, mu, sigma):\n    return 0.0\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-likelihood-report/exercise.yaml",
    f'''id: debug-likelihood-report
stage: debug
rev: 1
title: "A likelihood that always picks the edge"
prompt: |
  This program fits a coin's bias and a normal's mean by maximum likelihood over a grid, and should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the coin comes out at 0.99, the largest bias on the grid, because `coin_likelihood` charges every flip as a head (`ps**flips`) and forgets the two tails. Fix that, and the normal's mean comes out at an edge of its grid too: `normal_log_likelihood` is missing the minus sign, so the grid search finds the **least** likely mean instead of the most.
skills: [likelihood, maximize]
''',
)
write("exercises/debug-likelihood-report/starter.py", DEBUG_STARTER)
write("exercises/debug-likelihood-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-likelihood-report/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the coin's bias and the normal's mean."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_the_two_functions():
    """The coin's likelihood of 2 heads in 3 peaks at 2/3, and the normal's log-likelihood is highest at the sample mean."""
    coin_likelihood = function("coin_likelihood")
    normal_log_likelihood = function("normal_log_likelihood")
    ps = np.linspace(0.01, 0.99, 99)
    assert abs(ps[coin_likelihood(ps, 2, 3).argmax()] - 0.67) < 0.011
    x = np.array([1.0, 2.0, 3.0, 6.0])
    mus = np.array([2.0, 3.0, 4.0])
    assert normal_log_likelihood(mus, x, 1.0).argmax() == 1
''',
)
write("exercises/debug-likelihood-report/wrong/coin-only.py", DEBUG_COIN_ONLY)
write(
    "exercises/debug-likelihood-report/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def coin_likelihood(ps, heads, flips):\n    return ps\n\n\n"
    + "def normal_log_likelihood(mus, x, sigma):\n    return mus\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise ------------------------------------------------------------------

write(
    "exercises/review-mle-coin/exercise.yaml",
    f'''id: review-mle-coin
stage: review_code
rev: 1
title: "A coin's bias by maximum likelihood, from memory"
prompt: |
  Write `mle_coin(heads, flips)`, which returns the bias on the grid `np.linspace(0.001, 0.999, 999)` whose log-likelihood of the flips is largest, as a float, and print it for 6 heads in 8, 3 in 10 and 1 in 1000:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [maximize, likelihood]
''',
)
write("exercises/review-mle-coin/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-mle-coin/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-mle-coin/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 0.75 0.3 0.001."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_coins():
    """Half the flips heads gives 0.5; 9 in 10 gives 0.9."""
    mle_coin = function("mle_coin")
    assert abs(mle_coin(7, 14) - 0.5) < 0.001
    assert abs(mle_coin(9, 10) - 0.9) < 0.001
''',
)
write(
    "exercises/review-mle-coin/wrong/heads-only.py",
    REVIEW_CODE_STARTER + '''

def mle_coin(heads, flips):
    ps = np.linspace(0.001, 0.999, 999)
    return float(ps[(heads * np.log(ps)).argmax()])


print(mle_coin(6, 8), mle_coin(3, 10), mle_coin(1, 1000))
''',
)
write(
    "exercises/review-mle-coin/wrong/typed-in.py",
    REVIEW_CODE_STARTER + "\n\ndef mle_coin(heads, flips):\n    return 0.75\n\n\nprint(\"0.75 0.3 0.001\")\n",
)

print("ml.prob.maximum-likelihood written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
