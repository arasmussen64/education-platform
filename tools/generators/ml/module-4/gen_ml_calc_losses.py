"""Writes the topic ml.calc.loss-functions (Module 4's fifth topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.calc.loss-functions")


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


SIGMOID = '''def sigmoid(z):
    return 1 / (1 + np.exp(-z))
'''

# --- the worked example ------------------------------------------------------------------

EXAMPLE = "import numpy as np\n\n\n" + SIGMOID + '''

pred = np.array([2.5, 0.0, 2.1, 7.8])
target = np.array([3.0, -0.5, 2.0, 8.0])
miss = pred - target
print(miss, round(float(np.mean(miss**2)), 4))
print(np.round(2 * miss / len(miss), 3))

p = np.array([0.9, 0.6, 0.3, 0.05])
y = np.array([1.0, 1.0, 0.0, 1.0])
each = -(y * np.log(p) + (1 - y) * np.log(1 - p))
print(np.round(each, 3), round(float(each.mean()), 3))
print(round(float(-np.log(0.01)), 3), round(float((1 - 0.01) ** 2), 3))

z = np.array([2.0, 0.0, -1.0])
y = np.array([1.0, 0.0, 1.0])
p = sigmoid(z)
print(np.round(p, 3))
print(np.round(p - y, 3))

scores = np.array([2.0, 1.0, 0.1])
e = np.exp(scores - scores.max())
probs = e / e.sum()
print(np.round(probs, 3), round(float(probs.sum()), 6))
print(round(float(-np.log(probs[0])), 3))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
assert EXAMPLE_OUT.startswith("[-0.5  0.5  0.1 -0.2] 0.1375\n[-0.25  0.25  0.05 -0.1 ]\n"), EXAMPLE_OUT
assert "e-" not in EXAMPLE_OUT and "e+" not in EXAMPLE_OUT

# --- the fill-in ----------------------------------------------------------------------------

FILL_HEAD = '''import numpy as np


def cross_entropy(p, y, eps=1e-12):
    p = np.clip(p, eps, ONE - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(ONE - p)))


print(round(cross_entropy(np.array([0.9, 0.6, 0.3, 0.05]), np.array([1.0, 1.0, 0.0, 1.0])), 3))
print(round(cross_entropy(np.array([1.0, 0.0]), np.array([1.0, 0.0])), 6))
print(round(cross_entropy(np.array([0.0]), np.array([1.0])), 3))
'''
FILL_SOLUTION = FILL_HEAD.replace("ONE", "1")
FILL_STARTER = FILL_HEAD.replace("ONE", "...")
FILL_NO_CLIP = FILL_SOLUTION.replace("    p = np.clip(p, eps, 1 - eps)\n", "")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT == "0.992\n0.0\n27.631\n", FILL_OUT
assert out(FILL_NO_CLIP) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_STARTER = "import numpy as np\n"
WRITE_SOLUTION = WRITE_STARTER + '''

def softmax(scores):
    e = np.exp(scores - scores.max())
    return e / e.sum()


print(np.round(softmax(np.array([2.0, 1.0, 0.1])), 3))
print(softmax(np.array([1000.0, 1000.0])))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT == "[0.659 0.242 0.099]\n[0.5 0.5]\n", WRITE_OUT
WRITE_UNSTABLE = WRITE_SOLUTION.replace("    e = np.exp(scores - scores.max())", "    e = np.exp(scores)")
assert out(WRITE_UNSTABLE) != WRITE_OUT

# --- the build ---------------------------------------------------------------------------------------

BUILD_FUNCTIONS = '''def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def mse(pred, target):
    return float(np.mean((pred - target) ** 2))


def d_mse(pred, target):
    return 2 * (pred - target) / len(target)


def cross_entropy(p, y, eps=1e-12):
    p = np.clip(p, eps, 1 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def d_cross_entropy_dz(z, y):
    return (sigmoid(z) - y) / len(y)
'''
BUILD_SOLUTION = "import numpy as np\n\n\n" + BUILD_FUNCTIONS + '''

pred = np.array([2.5, 0.0, 2.1, 7.8])
target = np.array([3.0, -0.5, 2.0, 8.0])
print("mse", round(mse(pred, target), 4))
print("d_mse", np.round(d_mse(pred, target), 3))
p = np.array([0.9, 0.6, 0.3, 0.05])
y = np.array([1.0, 1.0, 0.0, 1.0])
print("cross-entropy", round(cross_entropy(p, y), 3))
z = np.array([2.0, 0.0, -1.0])
y = np.array([1.0, 0.0, 1.0])
print("d/dz", np.round(d_cross_entropy_dz(z, y), 3))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "mse 0.1375\nd_mse [-0.25  0.25  0.05 -0.1 ]\ncross-entropy 0.992\nd/dz [-0.04   0.167 -0.244]\n", BUILD_OUT
BUILD_NO_TWO = BUILD_SOLUTION.replace("    return 2 * (pred - target) / len(target)", "    return (pred - target) / len(target)")
BUILD_NO_N = BUILD_SOLUTION.replace("    return (sigmoid(z) - y) / len(y)", "    return sigmoid(z) - y")
BUILD_SUM = BUILD_SOLUTION.replace("    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))", "    return float(-np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)))")
for wrong in (BUILD_NO_TWO, BUILD_NO_N, BUILD_SUM):
    assert out(wrong) != BUILD_OUT

# --- the debug -----------------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def mse(pred, target):
    return float(np.mean((pred - target) ** 2))


def cross_entropy(p, y):
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


pred = np.array([2.5, 0.0, 2.1, 7.8])
target = np.array([3.0, -0.5, 2.0, 8.0])
print("mse", round(mse(pred, target), 4))
p = np.array([0.9, 0.6, 0.3, 0.05])
y = np.array([1.0, 1.0, 0.0, 1.0])
print("cross-entropy", round(cross_entropy(p, y), 3))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("np.mean((pred - target) ** 2)", "np.mean(np.abs(pred - target))").replace(
    "np.log(p) + (1 - y) * np.log(1 - p)", "np.log10(p) + (1 - y) * np.log10(1 - p)"
)
DEBUG_LOG_ONLY = DEBUG_SOLUTION.replace("np.mean((pred - target) ** 2)", "np.mean(np.abs(pred - target))")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == "mse 0.1375\ncross-entropy 0.992\n", DEBUG_OUT

# --- predict items ----------------------------------------------------------------------------------------

PREDICT_MSE = '''import numpy as np

pred = np.array([1.0, 4.0, 2.0])
target = np.array([2.0, 2.0, 2.0])
miss = pred - target
print(round(float(np.mean(miss**2)), 3))
print(np.round(2 * miss / 3, 3))
'''
PREDICT_MSE_OUT = out(PREDICT_MSE)
print("predict mse:\n" + PREDICT_MSE_OUT)
assert PREDICT_MSE_OUT == "1.667\n[-0.667  1.333  0.   ]\n", PREDICT_MSE_OUT

REVIEW_CERTAINTY = '''import numpy as np

p = np.array([0.5, 0.9, 0.99, 0.999])
print(np.round(-np.log(p), 3))
print(np.round(-np.log(1 - p), 3))
'''
REVIEW_CERTAINTY_OUT = out(REVIEW_CERTAINTY)
print("review certainty:\n" + REVIEW_CERTAINTY_OUT)
assert REVIEW_CERTAINTY_OUT == "[0.693 0.105 0.01  0.001]\n[0.693 2.303 4.605 6.908]\n", REVIEW_CERTAINTY_OUT

REVIEW_CODE_STARTER = '''import numpy as np

pred = np.array([2.5, 0.0, 2.1, 7.8])
target = np.array([3.0, -0.5, 2.0, 8.0])
'''
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def mse(pred, target):
    return float(np.mean((pred - target) ** 2))


print(round(mse(pred, target), 4))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "0.1375\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.calc.loss-functions
kind: topic
status: ready
title: "Loss functions and their gradients"
summary: "Squared error, cross-entropy with the sigmoid and the softmax, why logs appear, and the gradient of each loss."
prerequisites: [ml.calc.derivatives, ml.math.probability-and-statistics]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Compute mean squared error and cross-entropy for predictions and targets."
  - "Say why a probability model uses log loss rather than squared error."
  - "Differentiate each loss with respect to the prediction."
  - "Read a loss curve and say whether training is working."
# Linked, never copied or embedded: Michael Nielsen's book is CC BY-NC 3.0;
# 3Blue1Brown's videos are under the standard YouTube licence; NumPy's
# documentation is under the NumPy licence (BSD-3-Clause).
resources:
  - title: "Neural Networks and Deep Learning, chapter 3, the section The cross-entropy cost function (Michael Nielsen)"
    url: https://neuralnetworksanddeeplearning.com/chap3.html#the_cross-entropy_cost_function
    type: reading
    use: link
    license: CC BY-NC 3.0 (linked, not copied)
  - title: "3Blue1Brown: Neural networks (Grant Sanderson), chapter 2: Gradient descent, how neural networks learn (the cost function)"
    url: https://www.3blue1brown.com/topics/neural-networks
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "numpy.clip (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.clip.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-two-losses-and-their-gradients
  - parsons-cross-entropy
  - mcq-why-log-loss
  - predict-mse-and-its-gradient
  - mcq-reading-two-curves
  - fill-cross-entropy
  - write-softmax
prove:
  build: build-loss-functions
  debug: debug-loss-report
  explain:
    prompt: |
      A teammate is training a spam filter, whose output is the probability that a message is spam, with mean squared error, "because it worked for the house-price model". The loss falls slowly, and the model's confident mistakes never seem to get corrected. In your own words: what does squared error measure, and when is it the right loss? What does cross-entropy measure, and why do logs appear in it? What is the gradient of cross-entropy with respect to the sigmoid's input score, and why does that explain the stuck confident mistakes? And how would you read the training and held-out loss curves to tell whether the fixed model is learning?
    rubric:
      - id: mse
        required: true
        description: "Mean squared error is the average squared miss between prediction and target; it's the loss for predicting numbers (regression), where a miss of 2 should cost four times a miss of 1."
      - id: cross-entropy
        required: true
        description: "Cross-entropy is minus the log of the probability the model gave the right answer, averaged; the log turns the product of independent probabilities into a sum, and it punishes confident wrong answers hard (minus log 0.01 is 4.6, where squared error would say about 1)."
      - id: gradient
        required: true
        description: "With a sigmoid output and cross-entropy, the gradient of the loss with respect to the score is p - y (per example): the log's derivative 1/p and the sigmoid's p(1 - p) cancel, so a confident wrong answer gets a large gradient; with squared error the sigmoid's derivative p(1 - p) stays in and is nearly zero exactly when p is near 0 or 1, so confident mistakes barely move."
      - id: curves
        required: false
        description: "Both curves falling means learning; training falling while held-out rises means overfitting (stop early or regularize); a two-class cross-entropy stuck near 0.693, which is log 2, means the model is doing no better than guessing a half."
    model_answer: |
      Mean squared error is the average of the squared gaps between what the model predicted and the true value. It's the right loss when the target is a number, like a price, because a miss of 2 should cost four times a miss of 1 and the gradient, 2 times the miss over n, pulls harder the further off you are. A spam filter predicts a probability, and the loss for that is cross-entropy: for each message, minus the log of the probability the model gave to the right answer, averaged over the messages. The log is there because the probability of getting a whole set of independent messages right is a product, and a log turns that product into a sum you can average and differentiate; it also makes confidence expensive in the right way, since minus log of 0.01 is about 4.6 while squared error would charge about 1 for the same confident mistake. The gradient explains the stuck mistakes. With a sigmoid turning a score into p, the derivative of cross-entropy with respect to the score comes out to p minus y: the log's 1 over p and the sigmoid's p times 1 minus p cancel. A message the model calls 99 percent spam that isn't gets a gradient of 0.99, a hard shove. With squared error the sigmoid's derivative p times 1 minus p stays in the product, and it is nearly zero when p is near 0 or 1, which is precisely when the model is confidently wrong, so those examples barely move. For the curves: if the training loss and the loss on held-out messages both fall, it's learning; if training keeps falling while held-out turns up, it's memorizing the training set and should stop early or be regularized; and a two-class cross-entropy sitting at 0.69, which is log 2, means it's doing no better than guessing a half for everything.
review_pool:
  - review-predict-cost-of-confidence
  - review-mcq-p-minus-y
  - review-mcq-stuck-at-log-two
  - review-mse
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: mse
    description: "Compute mean squared error and its gradient"
  - id: cross-entropy
    description: "Compute cross-entropy for sigmoid and softmax outputs, and say why the logs are there"
  - id: gradient
    description: "Differentiate a loss with respect to the prediction or the score, and know the sigmoid-cross-entropy gradient is p - y"
  - id: curves
    description: "Read training and held-out loss curves and say whether training is working"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    '''<Intro>

Every chain in this module ends in the same link: a **loss**, one number that says how wrong the model is. Training steps the weights to shrink it, so the loss decides what the model learns to care about, and its gradient is where every backward pass starts. This topic has the two losses that cover most of machine learning, mean squared error for numbers and cross-entropy for probabilities, each computed, differentiated and checked, and the reason the second one has logs in it.

The main resource is **Michael Nielsen's chapter 3**, the section on the cross-entropy cost function, which shows a sigmoid neuron learning slowly under squared error and briskly under cross-entropy, and works out why; about 25 minutes. 3Blue1Brown's _Neural networks_ chapter 2 introduces the cost function with pictures. Watch for:

- **The learning slowdown:** a confidently wrong sigmoid barely moves under squared error.
- **Why the cross-entropy gradient is `p - y`:** two derivatives cancel.
- **Minus log of a probability** as the cost of a prediction.

</Intro>

<Resource index={0} />

<Recap>

- **Mean squared error**, for predicting numbers: `np.mean((pred - target) ** 2)`. A miss of 2 costs four times a miss of 1. Its gradient with respect to the predictions is `2 * (pred - target) / n`: proportional to the miss, pulling harder the further off you are.
- **Cross-entropy**, for predicting probabilities: for each example, minus the log of the probability the model gave to the right answer, `-(y * np.log(p) + (1 - y) * np.log(1 - p))` with `y` 1 or 0, averaged. Guessing 0.9 for a true 1 costs 0.105; 0.05 for a true 1 costs 3.0; 0.01 costs 4.6, where squared error would charge about 1.
- **Why logs.** The probability of getting many independent answers right is a product; a log turns it into a sum that can be averaged and differentiated. And `-log` is steep near zero, so confidence in the wrong answer is expensive in the right way. Clip `p` to `[1e-12, 1 - 1e-12]` before the log, or a model that says exactly 0 gives an infinite loss.
- **The gradient through the sigmoid.** With `p = sigmoid(z)` and cross-entropy, `dL/dz = p - y` for each example (divided by `n` for the mean). The log's derivative `1/p` and the sigmoid's `p(1 - p)` cancel. A model that says 0.99 for a true 0 gets a gradient of 0.99: a hard shove, exactly when it needs one. Under squared error the sigmoid's `p(1 - p)` stays in the product and is nearly zero at `p` near 0 or 1, so confident mistakes barely move: the **learning slowdown**.
- **Softmax**, for several classes: `np.exp(scores - scores.max())` divided by its sum, probabilities that add to 1. Subtracting the maximum first changes nothing mathematically and stops `exp` overflowing. The loss is minus the log of the probability given to the true class, and its gradient with respect to the scores is again `p - onehot`.
- **Reading loss curves.** Training and held-out loss both falling: learning. Training falling while held-out rises: **overfitting**, memorizing the training set; stop early or regularize. A two-class cross-entropy flat at 0.693 (`log 2`): the model is guessing a half for everything, so check the gradient, the rate and the data. Below 0.693 and falling: it has found something.
- **In machine learning:** the loss is the last link of the chain and the first factor of the backward pass; `p - y` is the gradient that enters every network in the next topic.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-cross-entropy.yaml",
    '''id: parsons-cross-entropy
type: parsons
rev: 1
prompt: |
  Put the lines in order to compute the mean cross-entropy of two predictions, `0.9` for a true 1 and `0.2` for a true 0, printing `0.164`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'p = np.array([0.9, 0.2])'
  - 'y = np.array([1.0, 0.0])'
  - 'each = -(y * np.log(p) + (1 - y) * np.log(1 - p))'
  - 'print(round(float(each.mean()), 3))'
distractors:
  - 'each = -(y * np.log(p) + (1 - y) * np.log(p))'
explanation: |
  For a true 1 the cost is `-log(p)`, the log of the probability given to the right answer; for a true 0 the right answer had probability `1 - p`, so the cost is `-log(1 - p)`. Here `-log(0.9) = 0.105` and `-log(0.8) = 0.223`, mean 0.164. The decoy charges `-log(p)` for the true 0 as well, which would reward predicting spam for a message that isn't.
skills: [cross-entropy]
''',
)

write(
    "recall/mcq-why-log-loss.yaml",
    '''id: mcq-why-log-loss
type: mcq
rev: 1
prompt: |
  A model outputs a probability through a sigmoid. Why train it with cross-entropy rather than mean squared error?
choices:
  - 'Confident wrong answers cost a lot (`-log 0.01` is 4.6 where squared error says about 1), and the gradient with respect to the score is `p - y`, which stays large when the model is confidently wrong; under squared error the sigmoid''s derivative multiplies in and vanishes exactly then'
  - 'Cross-entropy is always a smaller number, so training finishes sooner'
  - 'Squared error can''t be computed for numbers between 0 and 1'
  - 'Cross-entropy has no gradient, so it can''t overshoot'
answer: 0
explanation: |
  Both losses can be computed; the difference is in the gradient. With cross-entropy the log's `1/p` cancels the sigmoid's `p(1 - p)`, leaving `p - y`: a model that says 0.99 for a true 0 gets a shove of 0.99. With squared error the `p(1 - p)` stays and is nearly 0 when `p` is near 0 or 1, so the most wrong examples move the least. That's Nielsen's learning slowdown.
skills: [cross-entropy, gradient]
''',
)

write(
    "recall/predict-mse-and-its-gradient.yaml",
    f'''id: predict-mse-and-its-gradient
type: predict_output
rev: 1
prompt: |
  Mean squared error and its gradient for three predictions. What does the program print?
code: |
{block(PREDICT_MSE)}expected_output: |
{block(PREDICT_MSE_OUT)}explanation: |
  The misses are `-1`, `2` and `0`; squared, `1`, `4` and `0`; their mean is `5 / 3 = 1.667`. The gradient is `2 * miss / n`: `-0.667`, `1.333` and `0`. The prediction that was right gets no push, and the one twice as far off gets twice the push: squared error's gradient is proportional to the miss.
skills: [mse, gradient]
''',
)

write(
    "recall/mcq-reading-two-curves.yaml",
    '''id: mcq-reading-two-curves
type: mcq
rev: 1
prompt: |
  Over fifty epochs (passes through the training data), the training loss falls from 0.69 to 0.05. The loss on **held-out** data (examples the model never trains on) falls to 0.20 by epoch 15, then climbs to 0.35 by epoch 50. What's happening?
choices:
  - 'After epoch 15 the model is overfitting: it keeps fitting the training set but gets worse on new data; keep the epoch-15 model, or regularize'
  - 'The learning rate is too large; the held-out loss is bouncing'
  - 'Training never worked: a loss of 0.69 means nothing was learned'
  - 'The held-out data must be mislabelled, since the training loss is fine'
answer: 0
explanation: |
  The training loss can always be pushed down by memorizing the training set; the held-out loss is the one that says whether the model learned something general. Falling then rising is the signature of overfitting, and the usual response is to stop at the best held-out epoch or add regularization. The 0.69 at the start is `log 2`, the loss of guessing a half, which is where an untrained two-class model begins.
skills: [curves]
''',
)

write(
    "recall/review-predict-cost-of-confidence.yaml",
    f'''id: review-predict-cost-of-confidence
type: predict_output
rev: 1
prompt: |
  The cost of a probability when it's right, and when it's wrong. What does the program print?
code: |
{block(REVIEW_CERTAINTY)}expected_output: |
{block(REVIEW_CERTAINTY_OUT)}explanation: |
  The first line is `-log(p)`, the cost when the answer the model gave `p` to is right: small and shrinking as confidence grows. The second is `-log(1 - p)`, the cost when it's wrong: 2.3 at 0.9, 4.6 at 0.99, 6.9 at 0.999. Each extra nine of misplaced confidence adds another 2.3. That's the log doing its job.
skills: [cross-entropy]
''',
)

write(
    "recall/review-mcq-p-minus-y.yaml",
    '''id: review-mcq-p-minus-y
type: mcq
rev: 1
prompt: |
  A sigmoid unit outputs `p = 0.9` for an example whose true label is `y = 0`. What is the gradient of the cross-entropy with respect to the unit's score `z` (for this one example)?
choices:
  - '`0.9`: `p - y`, positive, so descent lowers the score'
  - '`-0.9`: `y - p`'
  - '`0.09`: `p * (1 - p)`'
  - '`0`: the sigmoid is saturated'
answer: 0
explanation: |
  For a sigmoid output with cross-entropy, `dL/dz = p - y`, here `0.9 - 0 = 0.9`. It's positive, so the loss rises with the score and descent pushes the score down, towards a smaller `p`. The sigmoid's own derivative `p(1 - p) = 0.09` would have shrunk the step under squared error; here it cancelled.
skills: [gradient]
''',
)

write(
    "recall/review-mcq-stuck-at-log-two.yaml",
    '''id: review-mcq-stuck-at-log-two
type: mcq
rev: 1
prompt: |
  A two-class model's cross-entropy sits at 0.69 for the whole run, training and held-out alike. What does that tell you?
choices:
  - 'It''s doing no better than guessing a half for every example (`log 2` is 0.693): nothing is being learned, so check the gradient, the learning rate and the data'
  - 'Training is working; 0.69 is a good loss'
  - 'The model is overfitting'
  - 'The learning rate is too large'
answer: 0
explanation: |
  `-log(0.5) = 0.693` is what cross-entropy charges a model that says 50-50 about everything, so a curve flat there from the start is a model that hasn''t moved. Overfitting shows as a gap between the two curves; a rate too large shows as climbing or bouncing. Flat at the guessing line points at a zero gradient, a rate of zero, or labels that carry no signal.
skills: [curves]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-two-losses-and-their-gradients/exercise.yaml",
    f'''id: example-two-losses-and-their-gradients
stage: worked_example
rev: 1
title: "Two losses and their gradients"
prompt: |
  This program computes mean squared error and its gradient, cross-entropy and the cost of a confident mistake, the gradient of cross-entropy through a sigmoid, and a softmax over three scores. Press **Run**, then read how each part works.
steps:
  - label: "Mean squared error"
    lines: "8-12"
    note: "Four predictions of numbers, four targets. `miss` is the gap for each; the loss is the mean of the squared gaps, 0.1375. Its gradient with respect to the predictions is `2 * miss / n`: the push on each prediction is proportional to how far off it is, and the sign says which way."
  - label: "Cross-entropy, and the price of confidence"
    lines: "14-18"
    note: "Four probabilities for a yes-or-no answer, with the true answers `y`. Each example costs minus the log of the probability given to the **right** answer: `-log(0.9)` is 0.105, `-log(1 - 0.3)` is 0.357, and the confident miss, 0.05 for a true 1, costs 2.996 on its own. The last line compares a 0.01 for a true 1: cross-entropy charges 4.6, squared error 0.98."
  - label: "The gradient through the sigmoid"
    lines: "20-24"
    note: "Scores `z` become probabilities through the sigmoid. The gradient of the cross-entropy with respect to each score is just `p - y`: the log's `1/p` and the sigmoid's `p(1 - p)` cancel. The third example, a true 1 given 0.269, gets a push of -0.731; the loss falls as its score rises."
  - label: "Softmax, for more than two classes"
    lines: "26-30"
    note: "Three scores become three probabilities that add to 1: `exp` of each over the sum. Subtracting the largest score first changes nothing mathematically (it cancels top and bottom) and keeps `exp` from overflowing on big scores. The loss for a true first class is minus the log of its probability, 0.417."
''',
)
write("exercises/example-two-losses-and-their-gradients/solution.py", EXAMPLE)
write(
    "exercises/example-two-losses-and-their-gradients/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints mean squared error and its gradient, cross-entropy, the sigmoid gradient and a softmax."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-cross-entropy/exercise.yaml",
    f'''id: fill-cross-entropy
stage: fill_in
rev: 1
title: "Cross-entropy, safely"
prompt: |
  `cross_entropy(p, y)` should return the mean cross-entropy of probabilities `p` against labels `y` (1 or 0), after clipping `p` into `[eps, 1 - eps]` so a prediction of exactly 0 or 1 can't make the log infinite. Replace each `...` so the program prints:

  ```
{block(FILL_OUT)}  ```

  The second line is two perfect predictions (a cost of 0.0 after clipping); the third is a prediction of exactly 0 for a true 1, which clipping turns into a large but finite 27.631. The program fails until every `...` is replaced.
hints:
  - "The top of the clip range is `1 - eps`."
  - "A true 0 had probability `1 - p`, so its cost is `-log(1 - p)`."
skills: [cross-entropy]
''',
)
write("exercises/fill-cross-entropy/starter.py", FILL_STARTER)
write("exercises/fill-cross-entropy/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-cross-entropy/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three losses."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_known_values():
    """Guessing a half for everything costs log 2; a 0.9 for a true 0 costs -log(0.1)."""
    cross_entropy = function("cross_entropy")
    assert abs(cross_entropy(np.array([0.5, 0.5, 0.5]), np.array([1.0, 0.0, 1.0])) - np.log(2)) < 1e-9
    assert abs(cross_entropy(np.array([0.9]), np.array([0.0])) + np.log(0.1)) < 1e-9
''',
)
write("exercises/fill-cross-entropy/wrong/no-clip.py", FILL_NO_CLIP)
write(
    "exercises/fill-cross-entropy/wrong/typed-in.py",
    '''import numpy as np


def cross_entropy(p, y, eps=1e-12):
    return 0.992


print(0.992)
print(0.0)
print(27.631)
''',
)

write(
    "exercises/write-softmax/exercise.yaml",
    f'''id: write-softmax
stage: write
rev: 1
title: "A softmax that doesn't overflow"
prompt: |
  Write `softmax(scores)`, which turns an array of scores into probabilities that add to 1: `exp` of each score divided by the sum of all of them, **after subtracting the largest score from every score** (which changes nothing mathematically and keeps `exp` from overflowing). Print it for `[2.0, 1.0, 0.1]` rounded to 3 places, and for `[1000.0, 1000.0]` as is:

  ```
{block(WRITE_OUT)}  ```

  Without the subtraction the second call prints `nan`, because `exp(1000)` is infinite.
hints:
  - "`scores - scores.max()` makes the largest score 0 and the rest negative, so every `exp` is at most 1."
  - "Divide the array of exponentials by its own sum."
skills: [cross-entropy]
''',
)
write("exercises/write-softmax/starter.py", WRITE_STARTER)
write("exercises/write-softmax/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-softmax/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the three probabilities and [0.5 0.5]."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_properties():
    """Probabilities sum to 1, keep the scores' order, and survive scores of 5000."""
    softmax = function("softmax")
    p = softmax(np.array([3.0, -1.0, 0.5, 2.0]))
    assert abs(p.sum() - 1) < 1e-12
    assert list(np.argsort(p)) == list(np.argsort([3.0, -1.0, 0.5, 2.0]))
    big = softmax(np.array([5000.0, 4999.0]))
    assert np.isfinite(big).all()
    assert abs(big[0] - 1 / (1 + np.exp(-1))) < 1e-9
''',
)
write("exercises/write-softmax/wrong/overflows.py", WRITE_UNSTABLE)
write(
    "exercises/write-softmax/wrong/typed-in.py",
    WRITE_STARTER + '''

def softmax(scores):
    return np.array([0.659, 0.242, 0.099])


print("[0.659 0.242 0.099]")
print("[0.5 0.5]")
''',
)

# --- the proof ---------------------------------------------------------------------------------------------

write(
    "exercises/build-loss-functions/exercise.yaml",
    f'''id: build-loss-functions
stage: build
rev: 1
title: "Two losses, with gradients"
prompt: |
  Starting from a blank editor, write the two losses a network ends in, each with its gradient:

  - `mse(pred, target)`: the mean squared error, as a float; `d_mse(pred, target)`: its gradient with respect to `pred`, `2 * (pred - target) / n`.
  - `cross_entropy(p, y, eps=1e-12)`: the mean cross-entropy of probabilities `p` against labels `y`, with `p` clipped into `[eps, 1 - eps]` first; `d_cross_entropy_dz(z, y)`: the gradient of that mean loss with respect to the **scores** `z`, where `p = sigmoid(z)`. It comes out to `(sigmoid(z) - y) / n`; write `sigmoid` yourself.

  Then print four lines: `mse` and `d_mse` for predictions `[2.5, 0.0, 2.1, 7.8]` against targets `[3.0, -0.5, 2.0, 8.0]`; `cross_entropy` for `p = [0.9, 0.6, 0.3, 0.05]` against `y = [1, 1, 0, 1]`; and `d_cross_entropy_dz` for scores `[2.0, 0.0, -1.0]` against `y = [1, 0, 1]`, rounded as shown:

  ```
{block(BUILD_OUT)}  ```

  The checks compare both gradients with numeric ones, and try losses whose values are known exactly.
skills: [mse, cross-entropy, gradient]
''',
)
write("exercises/build-loss-functions/starter.py", "")
write("exercises/build-loss-functions/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-loss-functions/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def numeric_gradient(f, p, h=1e-6):
    grad = np.zeros(len(p))
    for i in range(len(p)):
        step = np.zeros(len(p))
        step[i] = h
        grad[i] = (f(p + step) - f(p - step)) / (2 * h)
    return grad


def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_mse_and_its_gradient():
    """mse is 0 for a perfect prediction and 1 for misses of 1; d_mse matches a numeric gradient."""
    mse = function("mse")
    d_mse = function("d_mse")
    target = np.array([1.0, 2.0, 3.0])
    assert mse(target, target) == 0
    assert abs(mse(target + 1, target) - 1.0) < 1e-12
    pred = np.array([0.5, 2.5, 2.0])
    assert np.abs(d_mse(pred, target) - numeric_gradient(lambda q: mse(q, target), pred)).max() < 1e-6


def test_cross_entropy_values():
    """Guessing a half costs log 2; perfect predictions cost about 0; a prediction of exactly 0 stays finite."""
    cross_entropy = function("cross_entropy")
    assert abs(cross_entropy(np.array([0.5, 0.5]), np.array([1.0, 0.0])) - np.log(2)) < 1e-9
    assert cross_entropy(np.array([1.0, 0.0]), np.array([1.0, 0.0])) < 1e-9
    assert np.isfinite(cross_entropy(np.array([0.0]), np.array([1.0])))


def test_gradient_through_the_sigmoid():
    """d_cross_entropy_dz matches a numeric gradient of cross_entropy(sigmoid(z), y)."""
    cross_entropy = function("cross_entropy")
    d = function("d_cross_entropy_dz")
    z = np.array([1.5, -0.5, 0.0, 3.0])
    y = np.array([0.0, 1.0, 1.0, 0.0])
    numeric = numeric_gradient(lambda q: cross_entropy(1 / (1 + np.exp(-q)), y), z)
    assert np.abs(d(z, y) - numeric).max() < 1e-6
''',
)
write("exercises/build-loss-functions/wrong/d-mse-without-the-two.py", BUILD_NO_TWO)
write("exercises/build-loss-functions/wrong/dz-without-the-mean.py", BUILD_NO_N)
write("exercises/build-loss-functions/wrong/cross-entropy-summed.py", BUILD_SUM)
write(
    "exercises/build-loss-functions/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def mse(pred, target):\n    return 0.1375\n\n\n"
    + "def d_mse(pred, target):\n    return np.array([-0.25, 0.25, 0.05, -0.1])\n\n\n"
    + "def cross_entropy(p, y, eps=1e-12):\n    return 0.992\n\n\n"
    + "def d_cross_entropy_dz(z, y):\n    return np.array([-0.04, 0.167, -0.244])\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-loss-report/exercise.yaml",
    f'''id: debug-loss-report
stage: debug
rev: 1
title: "Two losses, both wrong"
prompt: |
  This program reports a mean squared error and a cross-entropy, and should print:

  ```
{block(DEBUG_OUT)}  ```

  It runs, but both numbers are wrong. `mse` averages the misses without squaring them (it's measuring mean **absolute** error), and `cross_entropy` uses `np.log10`, the base-10 log, where the loss is defined with the natural log, `np.log`; base 10 makes every cost 2.3 times too small.
skills: [mse, cross-entropy]
''',
)
write("exercises/debug-loss-report/starter.py", DEBUG_STARTER)
write("exercises/debug-loss-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-loss-report/test_exercise.py",
    f'''import numpy as np

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the two losses."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_known_values():
    """Misses of 2 cost 4 under mse; a half costs log 2 under cross-entropy."""
    mse = function("mse")
    cross_entropy = function("cross_entropy")
    assert abs(mse(np.array([3.0, 3.0]), np.array([1.0, 1.0])) - 4.0) < 1e-12
    assert abs(cross_entropy(np.array([0.5]), np.array([1.0])) - np.log(2)) < 1e-9
''',
)
write("exercises/debug-loss-report/wrong/log-only.py", DEBUG_LOG_ONLY)
write(
    "exercises/debug-loss-report/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def mse(pred, target):\n    return 0.1375\n\n\ndef cross_entropy(p, y):\n    return 0.992\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise -----------------------------------------------------------------------------

write(
    "exercises/review-mse/exercise.yaml",
    f'''id: review-mse
stage: review_code
rev: 1
title: "Mean squared error, from memory"
prompt: |
  Write `mse(pred, target)`, the mean squared error, and print it for the starter's arrays rounded to 4 places:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [mse]
''',
)
write("exercises/review-mse/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-mse/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-mse/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints 0.1375."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_values():
    """Misses of 1, 2 and 3 average to 14/3; equal arrays give 0."""
    mse = function("mse")
    assert abs(mse(np.array([1.0, 2.0, 3.0]), np.array([0.0, 0.0, 0.0])) - 14 / 3) < 1e-12
    assert mse(np.array([5.0, 5.0]), np.array([5.0, 5.0])) == 0
''',
)
write(
    "exercises/review-mse/wrong/absolute.py",
    REVIEW_CODE_STARTER + '''

def mse(pred, target):
    return float(np.mean(np.abs(pred - target)))


print(round(mse(pred, target), 4))
''',
)
write(
    "exercises/review-mse/wrong/typed-in.py",
    REVIEW_CODE_STARTER + '''

def mse(pred, target):
    return 0.1375


print(0.1375)
''',
)

print("ml.calc.loss-functions written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
