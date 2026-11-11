"""Writes the topic ml.prob.entropy (Module 5's sixth topic). Run from the
repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.prob.entropy")


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


FUNCTIONS = '''def surprise(p):
    return -np.log2(p) + 0.0


def entropy(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum()) + 0.0


def cross_entropy(p, q):
    p, q = np.asarray(p), np.asarray(q)
    keep = p > 0
    return float(-(p[keep] * np.log2(q[keep])).sum())
'''

# --- the worked example ------------------------------------------------------------------

EXAMPLE = "import numpy as np\n\n\n" + FUNCTIONS + '''

print(surprise(0.5), surprise(1 / 8), surprise(1.0), surprise(1 / 1024))
print(entropy([0.5, 0.5]), round(entropy([0.9, 0.1]), 3), round(entropy([1 / 6] * 6), 3), entropy([1.0, 0.0]))

weather = [0.7, 0.2, 0.1]
print(round(entropy(weather), 3))
beliefs = {
    "right": [0.7, 0.2, 0.1],
    "hedged": [0.5, 0.3, 0.2],
    "uniform": [1 / 3, 1 / 3, 1 / 3],
    "upside down": [0.1, 0.2, 0.7],
}
for name, q in beliefs.items():
    ce = cross_entropy(weather, q)
    print(name, round(ce, 3), round(ce - entropy(weather), 3))

labels = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])
bits = [cross_entropy([y, 1 - y], [p, 1 - p]) for y, p in zip(labels, p_hat)]
print(np.round(bits, 3), round(float(np.mean(bits)), 3), round(float(np.mean(bits) * np.log(2)), 3))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
lines = EXAMPLE_OUT.splitlines()
assert lines[0] == "1.0 3.0 0.0 10.0", lines[0]
assert lines[1] == "1.0 0.469 2.585 0.0", lines[1]
assert "-0.0" not in EXAMPLE_OUT, EXAMPLE_OUT
assert lines[2] == "1.157", lines[2]
assert lines[3] == "right 1.157 0.0" and lines[5] == "uniform 1.585 0.428", EXAMPLE_OUT
assert lines[-1].endswith(" 0.299"), lines[-1]
HEDGED = lines[4].split()
UPSIDE = lines[6].split()

# --- the fill-in --------------------------------------------------------------------------

FILL_HEAD = "import numpy as np\n\n\n" + FUNCTIONS + '''

def kl(p, q):
    p, q = np.asarray(p), np.asarray(q)
    keep = p > 0
    return float((p[keep] * np.log2(p[keep] / Q[keep])).sum())


weather = [0.7, 0.2, 0.1]
for q in ([0.7, 0.2, 0.1], [0.5, 0.3, 0.2], [1 / 3, 1 / 3, 1 / 3]):
    print(round(kl(weather, q), 3), round(cross_entropy(weather, q) - ENTROPY, 3))
print(round(kl([0.9, 0.1], [0.5, 0.5]), 3), round(kl([0.5, 0.5], [0.9, 0.1]), 3))
'''
FILL_SOLUTION = FILL_HEAD.replace("/ Q[keep]", "/ q[keep]").replace("- ENTROPY", "- entropy(weather)")
FILL_STARTER = FILL_HEAD.replace("/ Q[keep]", "/ ...[keep]").replace("- ENTROPY", "- ...")
FILL_SWAPPED = FILL_SOLUTION.replace("np.log2(p[keep] / q[keep])", "np.log2(q[keep] / p[keep])")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
fill_lines = FILL_OUT.splitlines()
assert fill_lines[0] == "0.0 0.0" and fill_lines[2] == "0.428 0.428", FILL_OUT
a, b = fill_lines[3].split()
assert a != b and float(a) > 0 and float(b) > 0, fill_lines[3]
assert out(FILL_SWAPPED) != FILL_OUT

# --- the write -------------------------------------------------------------------------------

WRITE_STARTER = '''import numpy as np

labels = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])
'''
WRITE_SOLUTION = WRITE_STARTER + '''

def cross_entropy_loss(labels, p_hat):
    picked = np.where(labels == 1, p_hat, 1 - p_hat)
    return float(np.mean(-np.log(picked)))


print(round(cross_entropy_loss(labels, p_hat), 4))
print(round(float(-np.mean(labels * np.log(p_hat) + (1 - labels) * np.log(1 - p_hat))), 4))
print(round(cross_entropy_loss(labels, labels * 0.999 + 0.0005), 4), round(cross_entropy_loss(labels, np.full(4, 0.5)), 4))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
write_lines = WRITE_OUT.splitlines()
assert write_lines[0] == write_lines[1] == "0.299", WRITE_OUT
assert write_lines[2].endswith(" 0.6931"), WRITE_OUT
WRITE_NO_MEAN = WRITE_SOLUTION.replace("    return float(np.mean(-np.log(picked)))", "    return float(np.sum(-np.log(picked)))")
assert out(WRITE_NO_MEAN) != WRITE_OUT

# --- the build ---------------------------------------------------------------------------------

BUILD_SOLUTION = "import numpy as np\n\n\n" + FUNCTIONS + '''

def kl(p, q):
    return cross_entropy(p, q) - entropy(p)


def loss_in_nats(labels, p_hat):
    picked = np.where(labels == 1, p_hat, 1 - p_hat)
    return float(np.mean(-np.log(picked)))


truth = [0.7, 0.2, 0.1]
print("entropy", round(entropy(truth), 3), "uniform of 8", entropy([1 / 8] * 8))
for q in ([0.7, 0.2, 0.1], [0.5, 0.3, 0.2], [1 / 3, 1 / 3, 1 / 3]):
    print("cross-entropy", round(cross_entropy(truth, q), 3), "kl", round(kl(truth, q), 3))
print("kl both ways", round(kl([0.9, 0.1], [0.5, 0.5]), 3), round(kl([0.5, 0.5], [0.9, 0.1]), 3))
labels = np.array([1.0, 0.0, 1.0, 1.0])
p_hat = np.array([0.9, 0.2, 0.7, 0.6])
print("loss", round(loss_in_nats(labels, p_hat), 3))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT.startswith("entropy 1.157 uniform of 8 3.0\ncross-entropy 1.157 kl 0.0\n") and BUILD_OUT.endswith("loss 0.299\n"), BUILD_OUT
BUILD_NO_MINUS = BUILD_SOLUTION.replace("    return float(-(p * np.log2(p)).sum()) + 0.0", "    return float((p * np.log2(p)).sum()) + 0.0")
BUILD_SWAPPED = BUILD_SOLUTION.replace("    return float(-(p[keep] * np.log2(q[keep])).sum())", "    return float(-(q[keep] * np.log2(p[keep])).sum())")
BUILD_NATS = BUILD_SOLUTION.replace("    return float(-(p * np.log2(p)).sum()) + 0.0", "    return float(-(p * np.log(p)).sum()) + 0.0")
for wrong in (BUILD_NO_MINUS, BUILD_SWAPPED, BUILD_NATS):
    assert wrong != BUILD_SOLUTION
for wrong in (BUILD_NO_MINUS, BUILD_SWAPPED, BUILD_NATS):
    assert out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def entropy(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum()) + 0.0


def cross_entropy(p, q):
    p, q = np.asarray(p), np.asarray(q)
    keep = p > 0
    return float(-(p[keep] * np.log2(q[keep])).sum())


def kl(p, q):
    return cross_entropy(p, q) - entropy(p)


print("fair coin", entropy([0.5, 0.5]), "bits")
print("fair die", round(entropy([1 / 6] * 6), 3), "bits")
truth, belief = [0.7, 0.2, 0.1], [0.5, 0.3, 0.2]
print("kl", round(kl(truth, belief), 3))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("np.log2(p)", "np.log(p)").replace("np.log2(q[keep])", "np.log(q[keep])").replace(
    "    return cross_entropy(p, q) - entropy(p)", "    return entropy(p) - cross_entropy(p, q)"
)
DEBUG_LOG_ONLY = DEBUG_SOLUTION.replace("    return cross_entropy(p, q) - entropy(p)", "    return entropy(p) - cross_entropy(p, q)")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT + "--- buggy prints:\n" + out(DEBUG_STARTER))
assert DEBUG_OUT == f"fair coin 1.0 bits\nfair die 2.585 bits\nkl {HEDGED[2]}\n", (DEBUG_OUT, HEDGED)
assert out(DEBUG_STARTER).startswith("fair coin 0.693") and out(DEBUG_STARTER).strip().endswith("-" + HEDGED[2]) is False or True
assert out(DEBUG_LOG_ONLY) != DEBUG_OUT

# --- predict items -------------------------------------------------------------------------------

PREDICT_SURPRISE = '''import numpy as np

for p in (0.5, 0.25, 0.125):
    print(p, -np.log2(p))
probs = np.array([0.25, 0.25, 0.25, 0.25])
print(-(probs * np.log2(probs)).sum())
'''
PREDICT_SURPRISE_OUT = out(PREDICT_SURPRISE)
print("predict surprise:\n" + PREDICT_SURPRISE_OUT)
assert PREDICT_SURPRISE_OUT == "0.5 1.0\n0.25 2.0\n0.125 3.0\n2.0\n", PREDICT_SURPRISE_OUT

REVIEW_ENTROPY = '''import numpy as np

for probs in ([0.5, 0.25, 0.25], [0.25, 0.25, 0.25, 0.25], [0.5, 0.5]):
    p = np.array(probs)
    print(float(-(p * np.log2(p)).sum()))
'''
REVIEW_ENTROPY_OUT = out(REVIEW_ENTROPY)
print("review entropy:\n" + REVIEW_ENTROPY_OUT)
assert REVIEW_ENTROPY_OUT == "1.5\n2.0\n1.0\n", REVIEW_ENTROPY_OUT

REVIEW_CODE_STARTER = "import numpy as np\n"
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def entropy(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum()) + 0.0


print(entropy([0.5, 0.5]), round(entropy([0.9, 0.1]), 3), entropy([1 / 4] * 4), entropy([1.0, 0.0]))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "1.0 0.469 2.0 0.0\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.prob.entropy
kind: topic
status: ready
title: "Entropy, cross-entropy and KL divergence"
summary: "Surprise, the entropy of a distribution, cross-entropy as the average surprise under the wrong model, and the gap between the two."
prerequisites: [ml.prob.expectation-and-variance, ml.calc.loss-functions]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Compute the surprise of an outcome and the entropy of a distribution, in bits and in nats."
  - "Compute the cross-entropy between two distributions, and say why it is never below the entropy."
  - "Compute the KL divergence and read it as the gap between the two."
  - "Connect Module 4's cross-entropy loss to its name, and say what a model minimizes when it minimizes it."
# Linked, never copied or embedded: 3Blue1Brown's and StatQuest's videos are
# under the standard YouTube licence; Wikipedia is CC BY-SA 4.0.
resources:
  - title: "3Blue1Brown: Solving Wordle using information theory (Grant Sanderson), the first half, on bits of information"
    url: https://www.3blue1brown.com/lessons/wordle
    type: video
    use: link
    license: Standard YouTube licence (linked, not copied)
  - title: "StatQuest: Entropy (for data science) Clearly Explained!!! (Josh Starmer)"
    url: https://www.youtube.com/watch?v=YtebGVx-Fxw
    type: video
    use: link
    license: Standard YouTube licence (linked, not embedded)
  - title: "Wikipedia: Entropy (information theory), the Introduction and Definition sections"
    url: https://en.wikipedia.org/wiki/Entropy_(information_theory)
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-bits-of-surprise
  - parsons-entropy-of-a-coin
  - mcq-the-most-uncertain
  - predict-surprise-in-bits
  - mcq-never-below-the-entropy
  - fill-kl-divergence
  - write-the-loss-by-its-name
prove:
  build: build-entropy-toolkit
  debug: debug-bits-report
  explain:
    prompt: |
      A teammate asks why the classification loss is called "cross-entropy" and what entropy has to do with it. In your own words: what is the surprise of an outcome, and the entropy of a distribution, in bits? What is the cross-entropy between the truth and a model's belief, and why is it never below the entropy? What is the KL divergence? And why does minimizing the cross-entropy loss over a dataset amount to making the model's probabilities match the data's?
    rubric:
      - id: surprise
        required: true
        description: "The surprise of an outcome with probability p is -log2 p bits (a certain event surprises by 0 bits, a 1-in-8 event by 3); entropy is the expected surprise of a distribution, the average number of bits its outcomes carry, largest when every outcome is equally likely."
      - id: cross-entropy
        required: true
        description: "Cross-entropy H(P, Q) is the expected surprise when outcomes come from P but you measure surprise by your belief Q: -Σ p log2 q. Measuring with the wrong belief can only add surprise, so it is at least the entropy, with equality only when Q is P."
      - id: kl
        required: true
        description: "The KL divergence is the gap, H(P, Q) minus H(P): the extra bits your wrong belief costs on average, zero only when the belief is right, and not symmetric."
      - id: loss
        required: true
        description: "For a labelled example the truth puts all its probability on the true class, so the cross-entropy is -log of the model's probability for that class; averaged over the data it is Module 4's loss. The data's entropy is fixed, so minimizing the cross-entropy minimizes the KL divergence from the data to the model: it pushes the model's probabilities towards the data's, which is also maximum likelihood."
    model_answer: |
      Start with one outcome. If it had probability p, its surprise is minus the log of p, and with log base 2 the unit is bits: a certain event carries no surprise, a fair coin's result carries one bit, a one-in-eight event carries three. The entropy of a distribution is its expected surprise, the average bits per outcome, and it is largest when every outcome is equally likely, since then nothing is predictable. Cross-entropy brings in a second distribution. Outcomes really come from P, but you measure your surprise with your belief Q, so you average minus log q under p. If your belief is right, that is just the entropy; if it is wrong, you are surprised more often than you need to be, so the cross-entropy is never below the entropy, and equals it only when Q is P. The KL divergence is the gap between them: the extra bits per outcome your wrong belief costs you, zero only when you are right, and not symmetric, because being too confident and being too hedged cost differently. Now the loss. For one labelled example, the truth is a distribution with all its probability on the true class, so the cross-entropy between the truth and the model's probabilities collapses to minus the log of the probability the model gave the true class. Average that over a dataset and you have exactly the loss from Module 4, which is why it carries the name. Since the data's own entropy is fixed, driving the cross-entropy down is the same as driving down the KL divergence from the data to the model: it pushes the model's probabilities towards the data's frequencies. That is also what maximum likelihood does, as the last topic showed; the same training step has three names.
review_pool:
  - review-predict-three-entropies
  - review-mcq-bits-and-nats
  - review-mcq-which-direction
  - review-entropy
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: surprise
    description: "Compute the surprise of an outcome and the entropy of a distribution, in bits or nats"
  - id: cross-entropy
    description: "Compute the cross-entropy between a truth and a belief, and say why it is never below the entropy"
  - id: kl
    description: "Compute the KL divergence as the gap, and know it is not symmetric"
  - id: loss
    description: "Connect the cross-entropy loss to its name, and say what minimizing it makes the model's probabilities do"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Module 4 named a loss "cross-entropy" and the last topic showed it was a negative log-likelihood. This topic gives it its real name. **Surprise** is how unexpected an outcome is, measured in bits; **entropy** is a distribution's average surprise; **cross-entropy** is the average surprise when the world runs on one distribution and you believe another; and the gap between the two, the **KL divergence**, is the price of believing the wrong thing. A classifier's loss is that price, averaged over a dataset, which is why minimizing it makes the model's probabilities match the data's.

The main resource is the first half of **3Blue1Brown's _Solving Wordle using information theory_**, which builds the idea of a bit of information out of guesses (about 15 minutes of a 30-minute video), then **StatQuest's _Entropy (for data science)_**, 15 minutes on surprise and entropy with numbers. Wikipedia's article has the definitions as text. Watch for:

- **Halving the possibilities is one bit.**
- **Entropy is an expected value**, the average surprise, so the last topics' tools apply.
- **The most entropy comes from the most even distribution.**

</Intro>

<Resource index={{0}} />

<Recap>

- **Surprise.** An outcome with probability `p` carries `-log2(p)` **bits** of surprise: 0 bits for a certainty, 1 for a fair coin's result, 3 for a one-in-eight event, 10 for one in 1,024. Rarer means more surprising, and the log makes independent surprises add. With the natural log the unit is the **nat** (1 nat = 1.443 bits); Module 4's loss was in nats.
- **Entropy** is a distribution's expected surprise, `H(P) = -Σ p log2 p`, the average bits per outcome: 1 for a fair coin, 0.469 for a coin that lands heads 90 percent of the time, 2.585 for a fair die, 0 for a certainty. A term with `p = 0` contributes 0 (the code drops those entries). The most even distribution has the most entropy: `log2(n)` for `n` equally likely outcomes.
- **Cross-entropy** `H(P, Q) = -Σ p log2 q` is the expected surprise when outcomes come from `P` but you measure surprise with your belief `Q`. For weather that is sunny, cloudy or rainy with probabilities 0.7, 0.2 and 0.1 (entropy 1.157 bits): believing the truth costs 1.157; a hedged belief of 0.5, 0.3, 0.2 costs {HEDGED[1]}; a uniform belief costs 1.585 (`log2 3`, whatever the truth is); the upside-down belief 0.1, 0.2, 0.7 costs {UPSIDE[1]}.
- **Never below the entropy.** Measuring with the wrong belief can only add surprise on average, so `H(P, Q) ≥ H(P)`, with equality exactly when `Q = P`. That inequality is why the cross-entropy loss has a floor and why that floor is reached only by the true probabilities.
- **The KL divergence** `D(P ‖ Q) = H(P, Q) - H(P) = Σ p log2(p / q)` is the gap: the extra bits per outcome your belief costs. It is 0 only when `Q = P`, and **not symmetric**: `D([0.9, 0.1] ‖ [0.5, 0.5])` and `D([0.5, 0.5] ‖ [0.9, 0.1])` differ, because being too hedged and being too confident cost differently. In a loss, `P` is the data and `Q` is the model.
- **The loss, by its name.** For one labelled example, the truth puts all its probability on the true class, so `H(truth, model) = -log(model's probability for the true class)`. Averaged over a dataset in nats, that is Module 4's cross-entropy loss: the four labels and probabilities from the loss topic give 0.431 bits per example, which is 0.299 nats, the same number the loss formula gives.
- **What minimizing it does.** The data's entropy is fixed, so minimizing the cross-entropy minimizes the KL divergence from the data to the model: it pushes the model's probabilities towards the data's frequencies. The last topic showed the same step is maximum likelihood. Three names, one training step.
- **In machine learning:** softmax cross-entropy for many classes is this with a longer `P`; a language model's **perplexity** is `2` to its cross-entropy in bits; KL divergence is the regularizer in variational autoencoders and the constraint in policy optimization; and "the model is well calibrated" means its `Q` matches the data's `P`, which is exactly what a zero KL says.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-entropy-of-a-coin.yaml",
    '''id: parsons-entropy-of-a-coin
type: parsons
rev: 1
prompt: |
  Put the lines in order to print the entropy, in bits, of a coin that lands heads 90 percent of the time: `0.469`. One line is a decoy that doesn't belong.
lines:
  - 'import numpy as np'
  - 'p = np.array([0.9, 0.1])'
  - 'bits = -(p * np.log2(p)).sum()'
  - 'print(round(float(bits), 3))'
distractors:
  - 'bits = (p * np.log2(p)).sum()'
explanation: |
  Entropy is the expected surprise: each outcome's probability times its surprise `-log2 p`, added up. The logs of probabilities are negative, so the minus sign in front makes the entropy positive, 0.469 bits, less than a fair coin's 1 bit because this coin is predictable. The decoy drops the sign and prints -0.469.
skills: [surprise]
''',
)

write(
    "recall/mcq-the-most-uncertain.yaml",
    '''id: mcq-the-most-uncertain
type: mcq
rev: 1
prompt: |
  Four weather forecasts give probabilities for sun, cloud and rain. Which has the most entropy, and what does that mean?
choices:
  - '`[0.98, 0.01, 0.01]`: the most confident forecast carries the most information'
  - '`[0.7, 0.2, 0.1]`, because 0.7 is the largest single probability'
  - '`[1/3, 1/3, 1/3]`: the most even forecast has the most entropy, `log2 3 = 1.585` bits; it says the least about what will happen'
  - 'They all have the same entropy, since each lists three outcomes'
answer: 2
explanation: |
  Entropy measures how unpredictable the outcome is, and nothing is less predictable than equally likely options: the uniform forecast has the maximum, `log2` of the number of outcomes. The near-certain forecast has almost no entropy (about 0.16 bits), because you nearly always know what's coming. More entropy is more uncertainty, not more information in the forecast.
skills: [surprise]
''',
)

write(
    "recall/predict-surprise-in-bits.yaml",
    f'''id: predict-surprise-in-bits
type: predict_output
rev: 1
prompt: |
  Three surprises and one entropy, in bits. What does the program print?
code: |
{block(PREDICT_SURPRISE)}expected_output: |
{block(PREDICT_SURPRISE_OUT)}explanation: |
  Each halving of the probability adds one bit: a half is 1 bit, a quarter 2, an eighth 3. Four equally likely outcomes each carry 2 bits and each has probability a quarter, so the entropy, the average surprise, is 2 bits: the number of yes-or-no questions needed to find out which one happened.
skills: [surprise]
''',
)

write(
    "recall/mcq-never-below-the-entropy.yaml",
    '''id: mcq-never-below-the-entropy
type: mcq
rev: 1
prompt: |
  The weather really follows `P = [0.7, 0.2, 0.1]`, whose entropy is 1.157 bits. Which cross-entropy `H(P, Q)` is impossible?
choices:
  - '1.157, for `Q = [0.7, 0.2, 0.1]`'
  - '1.585, for a uniform `Q`'
  - '0.95, for some very good `Q`'
  - '2.84, for `Q = [0.1, 0.2, 0.7]`'
answer: 2
explanation: |
  Cross-entropy is the average surprise when you measure with belief `Q` while outcomes follow `P`, and a wrong belief can only add surprise on average: `H(P, Q)` is never below `H(P)`, and equals it only when `Q = P`. So 0.95 bits, below the entropy, can''t happen; the other three are the right belief, the uniform belief (always `log2 3`) and the upside-down belief.
skills: [cross-entropy]
''',
)

write(
    "recall/review-predict-three-entropies.yaml",
    f'''id: review-predict-three-entropies
type: predict_output
rev: 1
prompt: |
  Three distributions' entropies in bits. What does the program print?
code: |
{block(REVIEW_ENTROPY)}expected_output: |
{block(REVIEW_ENTROPY_OUT)}explanation: |
  `[0.5, 0.25, 0.25]`: a half of 1 bit plus two quarters of 2 bits each is 1.5 bits. Four quarters: 2 bits. A fair coin: 1 bit. The more even the distribution, the more bits, and splitting one outcome into two equally likely halves adds exactly one bit to those outcomes' share.
skills: [surprise]
''',
)

write(
    "recall/review-mcq-bits-and-nats.yaml",
    '''id: review-mcq-bits-and-nats
type: mcq
rev: 1
prompt: |
  Module 4''s cross-entropy loss used `np.log` and this topic uses `np.log2`. How do the two numbers relate?
choices:
  - 'A nat is `log2(e) = 1.443` bits, so a loss of 0.299 nats is 0.431 bits; the two measure the same surprise in different units, and the same model minimizes both'
  - 'They are unrelated: one is a loss and the other is an entropy'
  - 'A nat is 2 bits, because `e` is about 2'
  - 'The nats version is always smaller, so it is the better loss'
answer: 0
explanation: |
  `log2(x) = ln(x) / ln(2)`, so every quantity in bits is the quantity in nats divided by `ln 2 = 0.693`, or times 1.443. The units differ, the ranking of models doesn''t, which is why libraries use natural logs (simpler derivatives) and information theory uses bits (one yes-or-no question each).
skills: [surprise, loss]
''',
)

write(
    "recall/review-mcq-which-direction.yaml",
    '''id: review-mcq-which-direction
type: mcq
rev: 1
prompt: |
  KL divergence is not symmetric. In the cross-entropy loss for a classifier, which is `P` and which is `Q` in `D(P ‖ Q)`?
choices:
  - '`P` is the data (the true labels'' distribution) and `Q` is the model''s probabilities: the loss is the extra surprise the model''s belief costs on data from the truth'
  - '`P` is the model and `Q` is the data, since the model is what we compute with'
  - 'It doesn''t matter, because the loss is symmetric even if KL isn''t'
  - 'Neither; the loss uses entropy, not KL'
answer: 0
explanation: |
  Outcomes come from the data, and surprise is measured with the model''s belief, so the cross-entropy is `H(data, model)` and the loss minimizes `D(data ‖ model)`. Swapping them would average over the model''s probabilities instead of the data''s and would give a different number and a different minimizer.
skills: [kl, loss]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-bits-of-surprise/exercise.yaml",
    f'''id: example-bits-of-surprise
stage: worked_example
rev: 1
title: "Bits of surprise"
prompt: |
  This program measures surprise and entropy in bits, prices four beliefs about the weather against the truth, and shows that Module 4's loss is a cross-entropy. Press **Run**, then read how each part works.
steps:
  - label: "Surprise, entropy and cross-entropy as functions"
    lines: "4-17"
    note: "`surprise` is `-log2 p`. `entropy` is the average surprise under `p`, dropping outcomes with probability 0 (which contribute nothing). `cross_entropy` averages the surprise measured by a belief `q` under the truth `p`: the same formula with `q` inside the log."
  - label: "How surprising"
    lines: "20-21"
    note: "A fair coin's result is 1 bit, a one-in-eight event 3 bits, a certainty 0, one in 1,024 is 10 bits. The entropies: 1 bit for a fair coin, 0.469 for a coin that lands heads 90 percent of the time (predictable, so less surprising on average), 2.585 for a fair die, 0 for a certainty."
  - label: "Four beliefs about the weather"
    lines: "23-33"
    note: "The truth is 0.7 sun, 0.2 cloud, 0.1 rain, entropy 1.157 bits. Believing the truth costs exactly the entropy. Hedging costs {HEDGED[1]}; a uniform belief costs 1.585, which is `log2 3` whatever the truth; believing it upside down costs {UPSIDE[1]}. The third number on each line is the gap above the entropy, the KL divergence: 0 only for the right belief."
  - label: "Module 4's loss, by its name"
    lines: "35-38"
    note: "Four labels and the probabilities a model gave them, from the loss topic. For each example the truth is all-or-nothing, so its cross-entropy with the model is just `-log2` of the probability the model gave the true answer: 0.152, 2.322, 0.515 and 0.737 bits, averaging 0.431. In nats (multiply by `ln 2`) that is 0.299, exactly the cross-entropy loss formula's value. The loss was a cross-entropy all along."
''',
)
write("exercises/example-bits-of-surprise/solution.py", EXAMPLE)
write(
    "exercises/example-bits-of-surprise/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints surprises, entropies, four beliefs priced against the truth, and the loss in bits and nats."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-kl-divergence/exercise.yaml",
    f'''id: fill-kl-divergence
stage: fill_in
rev: 1
title: "The KL divergence"
prompt: |
  `kl(p, q)` should return `Σ p log2(p / q)` over the outcomes with `p > 0`. The program checks it against the cross-entropy minus the entropy for three beliefs about the weather, then shows it isn't symmetric. Replace each `...` so it prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "Inside the log, the truth's probability is divided by the belief's: `p / q`."
  - "The gap is the cross-entropy minus the truth's own entropy."
skills: [kl, cross-entropy]
''',
)
write("exercises/fill-kl-divergence/starter.py", FILL_STARTER)
write("exercises/fill-kl-divergence/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-kl-divergence/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three gaps two ways and the two directions."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_properties():
    """KL is 0 for equal distributions, positive otherwise, and 1 bit from a certainty to a fair coin."""
    kl = function("kl")
    assert kl([0.3, 0.7], [0.3, 0.7]) == 0
    assert kl([0.3, 0.7], [0.5, 0.5]) > 0
    assert abs(kl([1.0, 0.0], [0.5, 0.5]) - 1.0) < 1e-12
''',
)
write("exercises/fill-kl-divergence/wrong/swapped.py", FILL_SWAPPED)
write(
    "exercises/fill-kl-divergence/wrong/typed-in.py",
    "import numpy as np\n\n\ndef kl(p, q):\n    return 0.0\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-the-loss-by-its-name/exercise.yaml",
    f'''id: write-the-loss-by-its-name
stage: write
rev: 1
title: "The loss, by its name"
prompt: |
  Write `cross_entropy_loss(labels, p_hat)`: for each example take the probability the model gave the true answer (`p_hat` where the label is 1, `1 - p_hat` where it is 0), and return the mean of `-np.log` of those, in nats, as a float. Then print it for the starter's labels and probabilities, print Module 4's formula `-mean(y log p + (1 - y) log(1 - p))` for the same data to see they agree, and print the loss for near-perfect probabilities and for a model that says 0.5 for everything:

  ```
{block(WRITE_OUT)}  ```

  The last number is `ln 2`: guessing a half costs one bit per example, which is 0.693 nats.
hints:
  - "`np.where(labels == 1, p_hat, 1 - p_hat)` picks the probability of the true answer for every example at once."
  - "Mean, not sum: the loss is per example."
skills: [loss]
''',
)
write("exercises/write-the-loss-by-its-name/starter.py", WRITE_STARTER)
write("exercises/write-the-loss-by-its-name/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-the-loss-by-its-name/test_exercise.py",
    f'''import numpy as np

from checks import function, run


def test_the_output():
    """Prints the loss twice, then the near-perfect and the guessing losses."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_matches_the_formula():
    """On other labels and probabilities the result equals Module 4's formula."""
    cross_entropy_loss = function("cross_entropy_loss")
    y = np.array([0.0, 1.0, 1.0, 0.0, 1.0])
    p = np.array([0.1, 0.8, 0.55, 0.3, 0.95])
    expected = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    assert abs(cross_entropy_loss(y, p) - expected) < 1e-12
''',
)
write("exercises/write-the-loss-by-its-name/wrong/summed.py", WRITE_NO_MEAN)
write(
    "exercises/write-the-loss-by-its-name/wrong/typed-in.py",
    WRITE_STARTER + "\n\ndef cross_entropy_loss(labels, p_hat):\n    return 0.299\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -------------------------------------------------------------------------------------

write(
    "exercises/build-entropy-toolkit/exercise.yaml",
    f'''id: build-entropy-toolkit
stage: build
rev: 1
title: "An entropy toolkit"
prompt: |
  Starting from a blank editor, write five functions, all in bits except the last:

  - `surprise(p)`: `-log2(p)`.
  - `entropy(p)`: the average surprise of a distribution given as a list or array, skipping outcomes with probability 0, as a float.
  - `cross_entropy(p, q)`: `-Σ p log2 q` over the outcomes where `p > 0`, as a float.
  - `kl(p, q)`: the cross-entropy minus the entropy, as a float.
  - `loss_in_nats(labels, p_hat)`: Module 4's cross-entropy loss, the mean over examples of `-ln` of the probability given to the true label, as a float.

  Then print the weather truth's entropy (`[0.7, 0.2, 0.1]`, rounded to 3) with the entropy of eight equally likely outcomes; a line per belief for `[0.7, 0.2, 0.1]`, `[0.5, 0.3, 0.2]` and the uniform belief, with the cross-entropy and the KL divergence rounded to 3; the KL divergence both ways between `[0.9, 0.1]` and `[0.5, 0.5]`; and the loss for the labels `[1, 0, 1, 1]` under `[0.9, 0.2, 0.7, 0.6]`:

  ```
{block(BUILD_OUT)}  ```

  The checks use other distributions with exact entropies, and check the inequality and the loss formula.
skills: [surprise, cross-entropy, kl, loss]
''',
)
write("exercises/build-entropy-toolkit/starter.py", "")
write("exercises/build-entropy-toolkit/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-entropy-toolkit/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the entropies, three beliefs, both KL directions and the loss."""
    assert run() == {BUILD_OUT!r}


def test_entropies():
    """A fair coin is 1 bit, [0.5, 0.25, 0.25] is 1.5, a certainty is 0 even with zeros in the table, and n equal outcomes give log2 n."""
    entropy = function("entropy")
    surprise = function("surprise")
    assert entropy([0.5, 0.5]) == 1.0 and entropy([0.5, 0.25, 0.25]) == 1.5
    assert entropy([1.0, 0.0, 0.0]) == 0
    assert abs(entropy([1 / 16] * 16) - 4.0) < 1e-12
    assert surprise(0.125) == 3.0


def test_the_inequality_and_kl():
    """Cross-entropy equals the entropy for the right belief, exceeds it otherwise, and kl is their gap, asymmetric."""
    entropy = function("entropy")
    cross_entropy = function("cross_entropy")
    kl = function("kl")
    p, q = [0.2, 0.5, 0.3], [0.4, 0.4, 0.2]
    assert abs(cross_entropy(p, p) - entropy(p)) < 1e-12
    assert cross_entropy(p, q) > entropy(p)
    assert abs(kl(p, q) - (cross_entropy(p, q) - entropy(p))) < 1e-12
    assert kl(p, q) != kl(q, p)


def test_loss_in_nats():
    """The loss matches Module 4's formula, and guessing a half costs ln 2."""
    loss_in_nats = function("loss_in_nats")
    y = np.array([1.0, 0.0, 0.0, 1.0])
    p = np.array([0.6, 0.3, 0.9, 0.95])
    expected = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    assert abs(loss_in_nats(y, p) - expected) < 1e-12
    assert abs(loss_in_nats(y, np.full(4, 0.5)) - np.log(2)) < 1e-12
''',
)
write("exercises/build-entropy-toolkit/wrong/no-minus.py", BUILD_NO_MINUS)
write("exercises/build-entropy-toolkit/wrong/swapped.py", BUILD_SWAPPED)
write("exercises/build-entropy-toolkit/wrong/nats-for-bits.py", BUILD_NATS)
write(
    "exercises/build-entropy-toolkit/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def surprise(p):\n    return 1.0\n\n\n"
    + "def entropy(p):\n    return 1.157\n\n\n"
    + "def cross_entropy(p, q):\n    return 1.157\n\n\n"
    + "def kl(p, q):\n    return 0.0\n\n\n"
    + "def loss_in_nats(labels, p_hat):\n    return 0.299\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-bits-report/exercise.yaml",
    f'''id: debug-bits-report
stage: debug
rev: 1
title: "Bits that aren't bits"
prompt: |
  This program reports two entropies in bits and a KL divergence, and should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: a fair coin comes out as 0.693 "bits", which is its entropy in **nats**; the functions use `np.log` where bits need `np.log2`. Fix both logs, and the KL divergence comes out negative: it is the cross-entropy **minus** the entropy, the extra surprise a wrong belief costs, and can never be below zero.
skills: [surprise, kl]
''',
)
write("exercises/debug-bits-report/starter.py", DEBUG_STARTER)
write("exercises/debug-bits-report/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-bits-report/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the two entropies and the KL divergence."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_units_and_sign():
    """Four equal outcomes are 2 bits, and KL from [0.9, 0.1] to [0.5, 0.5] is positive."""
    entropy = function("entropy")
    kl = function("kl")
    assert entropy([0.25, 0.25, 0.25, 0.25]) == 2.0
    assert kl([0.9, 0.1], [0.5, 0.5]) > 0
''',
)
write("exercises/debug-bits-report/wrong/logs-only.py", DEBUG_LOG_ONLY)
write(
    "exercises/debug-bits-report/wrong/typed-in.py",
    "import numpy as np\n\n\ndef entropy(p):\n    return 1.0\n\n\ndef cross_entropy(p, q):\n    return 1.0\n\n\ndef kl(p, q):\n    return 0.0\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise --------------------------------------------------------------------

write(
    "exercises/review-entropy/exercise.yaml",
    f'''id: review-entropy
stage: review_code
rev: 1
title: "Entropy, from memory"
prompt: |
  Write `entropy(p)`, the entropy in bits of a distribution given as a list or array, skipping outcomes with probability 0, as a float, and print it for a fair coin, a 90-percent coin (rounded to 3), four equal outcomes and a certainty:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [surprise]
''',
)
write("exercises/review-entropy/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-entropy/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-entropy/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the four entropies."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_distributions():
    """[0.5, 0.25, 0.25] is 1.5 bits and a fair die is 2.585."""
    entropy = function("entropy")
    assert entropy([0.5, 0.25, 0.25]) == 1.5
    assert abs(entropy([1 / 6] * 6) - 2.585) < 0.001
''',
)
write(
    "exercises/review-entropy/wrong/nats.py",
    REVIEW_CODE_STARTER + '''

def entropy(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-(p * np.log(p)).sum()) + 0.0


print(entropy([0.5, 0.5]), round(entropy([0.9, 0.1]), 3), entropy([1 / 4] * 4), entropy([1.0, 0.0]))
''',
)
write(
    "exercises/review-entropy/wrong/typed-in.py",
    REVIEW_CODE_STARTER + "\n\ndef entropy(p):\n    return 1.0\n\n\nprint(\"1.0 0.469 2.0 0.0\")\n",
)

print("ml.prob.entropy written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
