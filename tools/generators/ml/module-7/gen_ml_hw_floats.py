"""Writes the topic ml.hw.floating-point (Module 7's second topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
IEEE arithmetic is identical in Pyodide, and every program runs with warnings
as errors so that no overflow warning hides in the output. Files are written
as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.hw.floating-point")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str, check: bool = True) -> str:
    result = subprocess.run([sys.executable, "-W", "error", "-c", program], capture_output=True, text=True, check=check)
    return result.stdout.replace("\r\n", "\n")


def block(text: str, indent: str = "  ") -> str:
    return "".join(indent + line + "\n" for line in text.rstrip("\n").splitlines())


def quoted(text: str) -> str:
    """A single-quoted YAML scalar: the one place where '' is an apostrophe."""
    return "'" + text.replace("'", "''") + "'"


def mcq(item_id: str, prompt: str, choices: list[str], answer: int, explanation: str, skills: list[str]) -> None:
    """An MCQ whose right answer is never the longest choice, with plain apostrophes in the block scalars."""
    lengths = [len(c) for c in choices]
    assert lengths[answer] < max(length for i, length in enumerate(lengths) if i != answer), (item_id, lengths)
    assert "''" not in prompt and "''" not in explanation, item_id
    write(
        f"recall/{item_id}.yaml",
        f"id: {item_id}\ntype: mcq\nrev: 1\nprompt: |\n{block(prompt)}choices:\n"
        + "".join(f"  - {quoted(c)}\n" for c in choices)
        + f"answer: {answer}\nexplanation: |\n{block(explanation)}skills: [{', '.join(skills)}]\n",
    )


# --- the worked example ----------------------------------------------------------------------

EXAMPLE = '''import math
import struct

import numpy as np

print(0.1 + 0.2 == 0.3, 0.1 + 0.2, f"{0.1:.20f}")

bits = struct.unpack(">I", struct.pack(">f", 0.1))[0]
pattern = f"{bits:032b}"
sign, exponent, mantissa = pattern[0], pattern[1:9], pattern[9:]
print("0.1 as float32:", sign, exponent, mantissa)
print("exponent", int(exponent, 2), "- 127 =", int(exponent, 2) - 127, "| mantissa 1 +", int(mantissa, 2), "/ 2**23")
print("which is", float(np.float32(0.1)))

print("epsilon: float32", float(np.finfo(np.float32).eps), "float64", np.finfo(np.float64).eps)
print("16777216 + 1 in float32:", float(np.float32(16777216) + np.float32(1)), "| in float64:", 16777216.0 + 1.0)
print("isclose:", math.isclose(0.1 + 0.2, 0.3), "| allclose:", np.allclose([0.1 + 0.2], [0.3]))

tenths = [0.1] * 10
total = 0.0
for tenth in tenths:
    total += tenth
print("ten tenths, one at a time:", total, "| sum():", sum(tenths), "| fsum:", math.fsum(tenths), "| 0.1 * 10:", 0.1 * 10)

total = np.float32(0)
for _ in range(100_000):
    total += np.float32(0.1)
print("100,000 tenths in float32, one at a time:", float(total))
print("the same with np.sum (pairwise):", float(np.sum(np.full(100_000, 0.1, dtype=np.float32))))

print("overflow:", 1e308 * 10, "| inf - inf:", float("inf") - float("inf"), "| nan == nan:", float("nan") == float("nan"))
logits = np.array([1000.0, 1001.0])
with np.errstate(over="ignore", invalid="ignore"):
    naive = np.exp(logits) / np.exp(logits).sum()
print("naive softmax of [1000, 1001]:", naive)
shifted = np.exp(logits - logits.max())
print("stable softmax:", shifted / shifted.sum(), "| log-sum-exp:", logits.max() + np.log(np.exp(logits - logits.max()).sum()))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert EX[0] == "False 0.30000000000000004 0.10000000000000000555", EX[0]
assert EX[1] == "0.1 as float32: 0 01111011 10011001100110011001101", EX[1]
assert EX[2] == "exponent 123 - 127 = -4 | mantissa 1 + 5033165 / 2**23", EX[2]
assert EX[3] == "which is 0.10000000149011612", EX[3]
assert EX[4] == "epsilon: float32 1.1920928955078125e-07 float64 2.220446049250313e-16", EX[4]
assert EX[5] == "16777216 + 1 in float32: 16777216.0 | in float64: 16777217.0", EX[5]
assert EX[6] == "isclose: True | allclose: True", EX[6]
assert EX[7] == "ten tenths, one at a time: 0.9999999999999999 | sum(): 1.0 | fsum: 1.0 | 0.1 * 10: 1.0", EX[7]
LOOP_TOTAL = float(EX[8].split()[-1])
PAIRWISE_TOTAL = float(EX[9].split()[-1])
assert abs(LOOP_TOTAL - 10000) > 1 and abs(PAIRWISE_TOTAL - 10000) < 0.01, (LOOP_TOTAL, PAIRWISE_TOTAL)
assert EX[10] == "overflow: inf | inf - inf: nan | nan == nan: False", EX[10]
assert EX[11] == "naive softmax of [1000, 1001]: [nan nan]", EX[11]
assert EX[12].startswith("stable softmax: [0.26894142 0.73105858] | log-sum-exp: 1001.3132616875182"), EX[12]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_TENTH = '''print(0.1 + 0.2 == 0.3, round(0.1 + 0.2, 10) == 0.3)
print(0.5 + 0.25 == 0.75, 0.1 * 3 == 0.3)
print(f"{0.5:.20f}")
'''
PREDICT_TENTH_OUT = out(PREDICT_TENTH)
assert PREDICT_TENTH_OUT == "False True\nTrue False\n0.50000000000000000000\n", PREDICT_TENTH_OUT

PREDICT_SUMS = '''import math

tenths = [0.1] * 10
total = 0.0
for tenth in tenths:
    total += tenth
print(total == 1.0, sum(tenths) == 1.0, math.fsum(tenths) == 1.0)
print(total)
'''
PREDICT_SUMS_OUT = out(PREDICT_SUMS)
assert PREDICT_SUMS_OUT == "False True True\n0.9999999999999999\n", PREDICT_SUMS_OUT

REVIEW_SPECIAL = '''big = 1e308
print(big * 10, -big * 10, big * 10 > big)
inf = float("inf")
print(inf - inf, inf * 0, 1 / inf)
nan = float("nan")
print(nan == nan, nan != nan, max(1.0, nan))
'''
REVIEW_SPECIAL_OUT = out(REVIEW_SPECIAL)
assert REVIEW_SPECIAL_OUT == "inf -inf True\nnan nan 0.0\nFalse True 1.0\n", REVIEW_SPECIAL_OUT

REVIEW_EPSILON = '''import numpy as np

eps64 = np.finfo(np.float64).eps
print(1.0 + eps64 > 1.0, 1.0 + eps64 / 2 > 1.0)
eps32 = np.float32(np.finfo(np.float32).eps)
print(bool(np.float32(1) + eps32 > 1), bool(np.float32(1) + eps32 / 2 > 1))
print(abs((0.1 + 0.2) - 0.3) < 4 * eps64)
'''
REVIEW_EPSILON_OUT = out(REVIEW_EPSILON)
assert REVIEW_EPSILON_OUT == "True False\nTrue False\nTrue\n", REVIEW_EPSILON_OUT

PARSONS_LINES = [
    "import numpy as np",
    "logits = np.array([1000.0, 1001.0])",
    "shifted = np.exp(logits - logits.max())",
    "print(shifted / shifted.sum())",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "[0.26894142 0.73105858]\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''import struct


def decode_float32(x):
    """The sign bit, the stored exponent and the mantissa bits of x as a float32."""
    bits = struct.unpack(">I", struct.pack(">f", x))[0]
    sign = bits >> 31
    exponent = (bits >> 23) & 0xFF
    mantissa = bits & 0x7FFFFF
    return sign, exponent, mantissa


for x in (1.0, -2.5, 0.1):
    sign, exponent, mantissa = decode_float32(x)
    value = (-1) ** sign * (1 + mantissa / 2**23) * 2 ** (exponent - 127)
    print(x, "->", sign, exponent - 127, mantissa, "->", value)
'''
FILL_STARTER = FILL_SOLUTION.replace("exponent = (bits >> 23) & 0xFF", "exponent = (bits >> ...) & 0xFF").replace("mantissa = bits & 0x7FFFFF", "mantissa = bits & ...")
FILL_WRONG = FILL_SOLUTION.replace("exponent = (bits >> 23) & 0xFF", "exponent = (bits >> 24) & 0xFF")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "1.0 -> 0 0 0 -> 1.0\n-2.5 -> 1 1 2097152 -> -2.5\n0.1 -> 0 -4 5033165 -> 0.10000000149011612\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''import numpy as np


def kahan_sum(values):
    """Sum values in float32 while carrying the rounding error forward, so it doesn't accumulate."""
    total = np.float32(0)
    carry = np.float32(0)
    for value in values:
        adjusted = np.float32(value) - carry
        new_total = total + adjusted
        carry = (new_total - total) - adjusted
        total = new_total
    return float(total)


def plain_sum(values):
    total = np.float32(0)
    for value in values:
        total += np.float32(value)
    return float(total)


tenths = [0.1] * 100_000
print("plain:", plain_sum(tenths))
print("kahan:", kahan_sum(tenths))
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
KAHAN = float(WRITE_OUT.splitlines()[1].split()[-1])
assert abs(KAHAN - 10000) < 0.01 and WRITE_OUT.splitlines()[0] == f"plain: {LOOP_TOTAL}", WRITE_OUT
WRITE_WRONG = WRITE_SOLUTION.replace("        carry = (new_total - total) - adjusted\n", "")
assert out(WRITE_WRONG) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''import math
import struct

import numpy as np


def decode_float32(x):
    """(sign bit, unbiased exponent, mantissa bits) of x stored as a float32."""
    bits = struct.unpack(">I", struct.pack(">f", x))[0]
    return bits >> 31, ((bits >> 23) & 0xFF) - 127, bits & 0x7FFFFF


def close(a, b, rel=1e-9, abs_=0.0):
    """Whether a and b agree within a relative tolerance of the larger, or an absolute one."""
    return abs(a - b) <= max(rel * max(abs(a), abs(b)), abs_)


def kahan_sum(values):
    """A float32 sum that carries its rounding error forward."""
    total = np.float32(0)
    carry = np.float32(0)
    for value in values:
        adjusted = np.float32(value) - carry
        new_total = total + adjusted
        carry = (new_total - total) - adjusted
        total = new_total
    return float(total)


def log_sum_exp(xs):
    """log(sum(exp(xs))) without overflowing: pull the largest term out first."""
    biggest = max(xs)
    return biggest + math.log(sum(math.exp(x - biggest) for x in xs))


def softmax(xs):
    """exp(xs) scaled to sum to 1, computed the stable way."""
    biggest = max(xs)
    weights = [math.exp(x - biggest) for x in xs]
    total = sum(weights)
    return [w / total for w in weights]


print(decode_float32(1.0), decode_float32(-2.5), decode_float32(0.1))
print(close(0.1 + 0.2, 0.3), close(1.0, 1.0 + 1e-6), close(0.0, 1e-12, abs_=1e-9))
print(round(kahan_sum([0.1] * 100_000), 3))
print(round(log_sum_exp([1000.0, 1001.0]), 6), [round(p, 6) for p in softmax([1000.0, 1001.0])])
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "(0, 0, 0) (1, 1, 2097152) (0, -4, 5033165)\nTrue False True\n10000.0\n1001.313262 [0.268941, 0.731059]\n", BUILD_OUT
BUILD_PLAIN_SUM = BUILD_SOLUTION.replace("        adjusted = np.float32(value) - carry\n        new_total = total + adjusted\n        carry = (new_total - total) - adjusted\n        total = new_total", "        total = total + np.float32(value)")
BUILD_NAIVE_SOFTMAX = BUILD_SOLUTION.replace("    biggest = max(xs)\n    weights = [math.exp(x - biggest) for x in xs]", "    weights = [math.exp(x) for x in xs]")
BUILD_BIASED_EXPONENT = BUILD_SOLUTION.replace("((bits >> 23) & 0xFF) - 127", "(bits >> 23) & 0xFF")
assert out(BUILD_PLAIN_SUM) != BUILD_OUT and out(BUILD_BIASED_EXPONENT) != BUILD_OUT
naive = subprocess.run([sys.executable, "-W", "error", "-c", BUILD_NAIVE_SOFTMAX], capture_output=True, text=True)
assert naive.returncode != 0 and "OverflowError" in naive.stderr, "the naive softmax should overflow"

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import math


def softmax(logits):
    """exp(logits) scaled to sum to 1, with the largest logit pulled out so nothing overflows."""
    biggest = max(logits)
    weights = [math.exp(x - biggest) for x in logits]
    total = sum(weights)
    return [w / total for w in weights]


def cross_entropy(logits, true_index):
    """Minus the log of the probability given to the true class."""
    return -math.log(softmax(logits)[true_index])


batch = [([2.0, 1.0, 0.1], 0), ([1000.0, 1001.0, 999.0], 1), ([0.0, 0.0, 0.0], 2)]
losses = [cross_entropy(logits, true_index) for logits, true_index in batch]
print("losses:", [round(loss, 4) for loss in losses], "mean:", round(sum(losses) / len(losses), 4))
print("probabilities sum to 1:", all(math.isclose(sum(softmax(logits)), 1.0) for logits, _ in batch))
'''
BUG_NAIVE = ("    biggest = max(logits)\n    weights = [math.exp(x - biggest) for x in logits]", "    weights = [math.exp(x) for x in logits]")
BUG_EXACT = ("math.isclose(sum(softmax(logits)), 1.0)", "sum(softmax(logits)) == 1.0")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_NAIVE).replace(*BUG_EXACT)
DEBUG_STILL_NAIVE = DEBUG_SOLUTION.replace(*BUG_NAIVE)
DEBUG_STILL_EXACT = DEBUG_SOLUTION.replace(*BUG_EXACT)
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT)
assert DEBUG_OUT == "losses: [0.417, 0.4076, 1.0986] mean: 0.6411\nprobabilities sum to 1: True\n", DEBUG_OUT
starter = subprocess.run([sys.executable, "-W", "error", "-c", DEBUG_STARTER], capture_output=True, text=True)
assert starter.returncode != 0 and "OverflowError" in starter.stderr, starter.stderr
EXACT_OUT = out(DEBUG_STILL_EXACT)
assert EXACT_OUT.splitlines()[1] == "probabilities sum to 1: False", EXACT_OUT

REVIEW_CODE_SOLUTION = '''import math


def softmax(xs):
    """exp(xs) scaled to sum to 1, computed so that large inputs don't overflow."""
    biggest = max(xs)
    weights = [math.exp(x - biggest) for x in xs]
    total = sum(weights)
    return [w / total for w in weights]


print([round(p, 4) for p in softmax([1.0, 2.0, 3.0])])
print([round(p, 4) for p in softmax([1000.0, 1001.0, 1002.0])])
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "[0.09, 0.2447, 0.6652]\n[0.09, 0.2447, 0.6652]\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.hw.floating-point
kind: topic
status: ready
title: "Floating point"
summary: "How a computer stores a fraction: sign, exponent and mantissa; why 0.1 + 0.2 isn't 0.3; float32 against float64; machine epsilon, rounding that accumulates, overflow to infinity, NaN, and the log-sum-exp trick that keeps a loss finite."
prerequisites: [ml.hw.bits-and-integers]
packages: [numpy]
estimated_minutes: 55
rev: 1
objectives:
  - "Explain how a float stores a number as sign, exponent and mantissa, and why most decimals are stored approximately."
  - "Compare two floats safely with a tolerance, and say what machine epsilon is for float32 and float64."
  - "Show rounding error accumulating in a long sum, and reduce it with pairwise or compensated summation."
  - "Say where infinity and NaN come from, and keep a softmax or a log-likelihood finite with log-sum-exp."
# Linked, never copied or embedded: the Python documentation is under the PSF
# licence; Wikipedia is CC BY-SA 4.0.
resources:
  - title: "The Python tutorial, chapter 15: Floating-Point Arithmetic: Issues and Limitations"
    url: https://docs.python.org/3/tutorial/floatingpoint.html
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
  - title: "Wikipedia: Single-precision floating-point format (the section IEEE 754 standard: binary32, and the sections on converting decimal to binary32)"
    url: https://en.wikipedia.org/wiki/Single-precision_floating-point_format
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
  - title: "Wikipedia: Kahan summation algorithm (the algorithm and the worked example)"
    url: https://en.wikipedia.org/wiki/Kahan_summation_algorithm
    type: reading
    use: link
    license: CC BY-SA 4.0 (linked, not copied)
practice:
  - example-what-a-float-holds
  - predict-a-tenth
  - mcq-why-a-tenth-is-not-exact
  - mcq-seven-digits
  - mcq-comparing-floats
  - predict-ten-tenths
  - mcq-nan-spreads
  - parsons-a-stable-softmax
  - fill-decode-a-float32
  - write-kahan-sum
prove:
  build: build-a-float-toolkit
  debug: debug-a-loss-that-overflowed
  explain:
    prompt: |
      A teammate's test asserts that a model's probabilities sum to exactly 1.0 and fails one time in five; another's training loss became NaN at the first large logit; a third keeps a running total of a million float32 losses and gets a mean that is visibly wrong. In your own words: how a float stores a number and why 0.1 can't be stored exactly; what machine epsilon is and how to compare floats; why a long sum drifts in float32 and what pairwise or compensated summation does about it; and where infinity and NaN come from and how log-sum-exp keeps a softmax finite.
    rubric:
      - id: representation
        required: true
        description: "A float is a sign, an exponent and a mantissa: a binary fraction times a power of two. Only fractions whose denominator is a power of two are exact (0.5, 0.25); 0.1 repeats in binary and is rounded to the nearest representable value, so 0.1 + 0.2 lands a last-digit away from 0.3. float32 keeps 24 bits of mantissa (about 7 decimal digits), float64 53 (about 16)."
      - id: epsilon
        required: true
        description: "Machine epsilon is the gap between 1 and the next float: about 1.2e-7 for float32 and 2.2e-16 for float64. Equality tests on computed floats fail by last-digit rounding; compare with a tolerance, math.isclose or np.isclose, relative for large values and absolute near zero."
      - id: accumulation
        required: true
        description: "Each addition rounds to the current magnitude, so adding small values to a large running total loses their low digits and the error grows with the count; summing in float64, pairwise summation (np.sum), math.fsum, or Kahan's carried-error sum keeps the result right."
      - id: special
        required: true
        description: "Overflow past the largest float gives inf, inf minus inf and 0 times inf give NaN, and NaN poisons everything it touches and is never equal to anything, itself included. exp of a large logit overflows; subtracting the maximum before exp (log-sum-exp) leaves the ratios unchanged and every term at most 1."
    model_answer: |
      A float stores a number in three parts: a sign bit, an exponent, and a mantissa that holds the significant digits in binary. The value is the mantissa times two to the exponent, so a float is a binary fraction scaled by a power of two. That is why only fractions whose denominator is a power of two come out exact: 0.5 and 0.25 do, but 0.1 is a repeating fraction in binary the way a third is in decimal, and it is rounded to the nearest pattern that fits. A float32 keeps 24 bits of mantissa, about seven decimal digits; a float64 keeps 53, about sixteen. So 0.1 + 0.2 is computed on two already-rounded numbers and lands a last digit away from the rounded 0.3, and the teammate's test for an exact sum of 1.0 fails whenever the rounding errors of the probabilities don't happen to cancel. Machine epsilon is the gap between 1 and the next representable number, about 1.2 times ten to the minus seven in float32 and 2.2 times ten to the minus sixteen in float64; it is the size of a single rounding step at magnitude one. The right test is a tolerance: math.isclose or np.isclose, with a relative tolerance for numbers of ordinary size and an absolute one near zero, where a relative tolerance shrinks to nothing. The running total drifts because every addition is rounded to the precision of the current total: once the total is large, a small loss's low digits fall off the end, and the loss repeats a million times in the same direction. Adding a hundred thousand tenths in float32 one at a time comes out well off ten thousand. The fixes are to accumulate in float64, to add pairwise so that partners are always of similar size, which is what np.sum does, to use math.fsum, which is exact, or to use Kahan's method, which keeps the rounding error of each step and feeds it back into the next. Infinity appears when a result is larger than the largest float, about 1.8 times ten to the 308 in float64 and 3.4 times ten to the 38 in float32; exp of 1000 overflows in either. NaN, not a number, appears when the arithmetic has no answer, such as infinity minus infinity or zero times infinity, and it spreads: anything computed from a NaN is NaN, and NaN is not equal to anything, not even itself. The loss went NaN because the softmax divided an overflowed infinity by an overflowed infinity. The log-sum-exp trick subtracts the largest logit from all of them before exponentiating, which leaves the ratios, and so the probabilities, unchanged while making every exponent at most zero and every term at most one, and adds the maximum back in the log.
review_pool:
  - review-predict-inf-and-nan
  - review-predict-epsilon
  - review-mcq-summing-a-million
  - review-mcq-why-subtract-the-max
  - review-stable-softmax
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: representation
    description: "Explain sign, exponent and mantissa, and why most decimals are stored approximately"
  - id: epsilon
    description: "Compare floats with a tolerance, and say what machine epsilon is for float32 and float64"
  - id: accumulation
    description: "Show rounding accumulating in a long sum, and reduce it"
  - id: special
    description: "Say where inf and NaN come from, and keep a softmax or a log-likelihood finite with log-sum-exp"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Every number in a model, the weights it learns, the activations it computes on the way and the loss that says how wrong it is, is a **float**, and floats are approximations with rules. `0.1 + 0.2` is not `0.3`; a float32 can't tell 16,777,216 from 16,777,217; a million small additions drift; `exp(1000)` is infinity and infinity divided by infinity is a value that poisons everything it touches. This topic opens a float up (sign, exponent, mantissa), measures how much precision each kind has, watches rounding accumulate and fixes it, and ends with the one trick every cross-entropy loss relies on: **log-sum-exp**.

The main resource is **the Python tutorial's chapter on floating-point arithmetic**, which walks through why 0.1 is stored approximately and what to do about it; about 20 minutes. Wikipedia's _Single-precision floating-point format_ has the bit layout, and its _Kahan summation algorithm_ page has the carried-error sum. Watch for:

- **Binary fractions**: which decimals come out exact and which repeat.
- **`repr` and rounding**: what Python shows you and what is stored.
- **`math.fsum`**: the exact sum, and what a plain running total loses.

</Intro>

<Resource index={{0}} />

<Recap>

- **A float is sign, exponent and mantissa.** A float32 spends 1 bit on the sign, 8 on an **exponent** (stored with 127 added, so `01111011`, 123, means `2**-4`) and 23 on the **mantissa**, the binary digits after a leading 1. The value is `(1 + mantissa / 2**23) * 2**(exponent - 127)`, with the sign. `0.1` is `0 01111011 10011001100110011001101`, which is `0.10000000149011612`: a binary fraction times a power of two, rounded to the nearest pattern. Only fractions with a power-of-two denominator are exact (`0.5`, `0.25`, `0.75`); `0.1` repeats in binary as a third does in decimal. So `0.1 + 0.2` is `0.30000000000000004`, and `0.1` printed to 20 places is `0.10000000000000000555`.
- **Precision.** float32 keeps 24 significant bits, about 7 decimal digits; float64 keeps 53, about 16. **Machine epsilon** is the gap between 1 and the next float: `1.19e-07` for float32 and `2.22e-16` for float64. Past `2**24` a float32 can't hold every integer: `16777216 + 1` stays `16777216`. That is why counts live in integers, why a long sum is accumulated in a wider type than its terms, and why models that compute in float16 keep a float32 copy of their weights and optimizer state (**mixed precision**, in the last bullet below).
- **Compare with a tolerance.** `0.1 + 0.2 == 0.3` is `False`; `math.isclose(0.1 + 0.2, 0.3)` and `np.isclose` are `True`. Use a relative tolerance for numbers of ordinary size and an absolute one near zero, where any relative tolerance shrinks to nothing. A test that asserts probabilities sum to exactly `1.0` fails by rounding.
- **Rounding accumulates.** Each addition rounds to the precision of the running total, so small values added to a large total lose their low digits, in the same direction, every time: a hundred thousand tenths added one at a time in float32 come to {LOOP_TOTAL:,.2f}, not 10,000; ten tenths added one at a time in float64 come to `0.9999999999999999`. Fixes: accumulate in float64; `np.sum`, which adds **pairwise** so partners stay the same size (the same hundred thousand tenths come to {PAIRWISE_TOTAL:,.3f}); `math.fsum`, which is exact, and Python's built-in `sum`, which has compensated for rounding since 3.12; or **Kahan summation**, which keeps each step's rounding error and feeds it into the next.
- **Infinity and NaN.** A result beyond the largest float (`1.8e308` in float64, `3.4e38` in float32) **overflows** to `inf`; `inf - inf`, `0 * inf` and `inf / inf` are `nan`, not a number, which spreads through every calculation it enters and is not equal to anything, itself included (`np.isnan` finds it; `==` never does). A mean with one `nan` in it is `nan`; the question is always where the first one came from.
- **Log-sum-exp.** `exp(1000)` overflows, so a naive **softmax** (the step that turns a model's raw scores, its **logits**, into probabilities that sum to 1) of `[1000, 1001]` is `inf / inf`, `nan`. Subtract the largest value first: `exp([0, 1])` is finite, the ratios are unchanged, and the probabilities are `[0.269, 0.731]`. For a log of a sum of exponentials, add the maximum back: `log(sum(exp(x))) = m + log(sum(exp(x - m)))`, `1001.313` here. Every cross-entropy (the loss that scores those probabilities) and every log-likelihood in a library does this.
- **In machine learning** (names you'll meet later): a loss that becomes `nan` is almost always an overflowed exponential, a log of zero or a division by zero, found by tracing the first `nan` back; **mixed precision** trains in float16 or bfloat16 with float32 accumulation for exactly the reasons above; `allclose` with a stated tolerance is how two implementations are checked against each other; and gradient clipping and learning-rate warm-up exist partly to keep numbers inside float range.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/predict-a-tenth.yaml",
    f'''id: predict-a-tenth
type: predict_output
rev: 1
prompt: |
  Four equality tests on decimals, and one decimal printed to twenty places. What does the program print?
code: |
{block(PREDICT_TENTH)}expected_output: |
{block(PREDICT_TENTH_OUT)}explanation: |
  `0.1` and `0.2` are both rounded before they are added, and their rounded sum isn't the rounded `0.3`; rounding the result to 10 places hides the difference. `0.5` and `0.25` have power-of-two denominators, so they are exact and their sum is too. `0.1 * 3` misses `0.3` the same way the sum does. `0.5` to twenty places is all zeros, because it is stored exactly.
skills: [representation]
''',
)

mcq(
    "mcq-why-a-tenth-is-not-exact",
    "Why can a float hold `0.5` and `0.75` exactly but not `0.1`?",
    [
        "Because `0.1` has fewer significant digits, and floats keep their precision for numbers with more digits than that",
        "Because `0.5` and `0.75` are multiples of a quarter, and floats count in quarters before they count in anything else",
        "Because a float is a binary fraction, exact only for power-of-two denominators; 1/10 repeats in binary",
        "Because Python rounds decimal literals to the nearest half or quarter when it reads them from the source file",
    ],
    2,
    "A float's mantissa is a binary fraction: a sum of halves, quarters, eighths and so on, so a value is exact only if it can be written that way, which means a denominator that is a power of two. 1/10 can't: in binary it is 0.000110011001100..., repeating, and it is rounded to the nearest 24 or 53 bits. Floats don't count in quarters; they count in whatever power of two the exponent sets.",
    ["representation"],
)

mcq(
    "mcq-seven-digits",
    "A float32 holds about 7 significant decimal digits and `np.float32(16777216) + 1` is still `16777216`. What limits it?",
    [
        "The exponent: 8 bits can't reach past 16 million, so larger numbers are clipped to the largest value it can express",
        "Rounding mode: NumPy rounds down by default, so adding 1 to a large number is lost",
        "Python converts the result to an int, which truncates anything a float32 carries",
        "The mantissa: 24 significant bits tell integers apart only up to `2**24`; above it neighbours are 2 apart",
    ],
    3,
    "The exponent sets the scale and 8 bits reach to about 3.4 times 10 to the 38; it is the 24-bit mantissa that fixes how many distinct values each scale has. Between 2 to the 24 and 2 to the 25 the representable numbers are 2 apart, so 16,777,217 doesn't exist in float32 and the sum rounds back. float64's 53 bits push the same cliff out to 9 quadrillion. NumPy rounds to nearest, not down, and the result stays a float32; nothing is converted to an int.",
    ["representation"],
)

mcq(
    "mcq-comparing-floats",
    "A test asserts `sum(probabilities) == 1.0` and fails one run in five. What is the right fix?",
    [
        "Compare with a tolerance, `math.isclose` or `np.isclose`: a sum of rounded floats lands a few last digits from 1",
        "Round the probabilities to 2 decimal places before summing, so the small rounding errors disappear before the test",
        "Use float32, whose rounding is coarser and therefore more forgiving of small errors",
        "Sort the probabilities before summing, so the result is deterministic from run to run",
    ],
    0,
    "Each probability is rounded to the nearest float, and their sum carries those roundings, so it lands within a few machine epsilons of 1 and is exactly 1 only by luck. A tolerance is the honest test. Rounding to 2 places would pass sums that are genuinely wrong; float32 makes the errors larger; sorting changes which digits are lost but not whether some are.",
    ["epsilon"],
)

write(
    "recall/predict-ten-tenths.yaml",
    f'''id: predict-ten-tenths
type: predict_output
rev: 1
prompt: |
  Ten tenths added three ways. What does the program print?
code: |
{block(PREDICT_SUMS)}expected_output: |
{block(PREDICT_SUMS_OUT)}explanation: |
  The loop adds the ten rounded tenths one after another and the roundings pile up to a last digit short of 1. Python's built-in `sum` has compensated for that rounding as it goes since version 3.12, and `math.fsum` tracks the exact sum and rounds once at the end: both give exactly 1.0. It is a plain running total that drifts.
skills: [accumulation]
''',
)

mcq(
    "mcq-nan-spreads",
    "A training run prints a loss of `nan` from step 300 onwards. What is true of `nan`, and what should you look for?",
    [
        "`nan` means the loss is too small to print; lower the learning rate and the numbers will come back into the printable range",
        "`nan` spreads to everything computed from it and equals nothing, even itself; find the first operation that made one",
        "`nan` compares equal to itself, so `loss == float('nan')` finds the bad step and the batch that caused it",
        "`nan` is NumPy's marker for a missing batch and can be skipped, as a missing value in a column would be",
    ],
    1,
    "Once a `nan` enters, every sum, product and gradient downstream is `nan`, so the loss stays `nan` for good; the useful question is where the first one came from. `nan == nan` is `False` by design, so use `np.isnan` to catch it. The usual sources are an exponential past float range, `log(0)` and `0 / 0`, which the next steps of this topic guard against. A `nan` is not a small number, so no learning rate brings it back, and NumPy puts `nan` only where your code or your data put it, never for a missing batch.",
    ["special"],
)

write(
    "recall/parsons-a-stable-softmax.yaml",
    "id: parsons-a-stable-softmax\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to compute the softmax of two large logits (a model's raw scores, turned into probabilities) without overflowing, and print `[0.26894142 0.73105858]`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("shifted = np.exp(logits)")
    + "\nexplanation: |\n"
    + block("Subtracting the largest logit leaves the differences, and so the ratios, unchanged, and makes every exponent at most 0, so every `exp` is at most 1. The decoy exponentiates the raw logits: `exp(1000)` overflows to infinity, and infinity over infinity is `nan`.")
    + "skills: [special]\n",
)

write(
    "recall/review-predict-inf-and-nan.yaml",
    f'''id: review-predict-inf-and-nan
type: predict_output
rev: 1
prompt: |
  Arithmetic at the edge of the float range. What does the program print?
code: |
{block(REVIEW_SPECIAL)}expected_output: |
{block(REVIEW_SPECIAL_OUT)}explanation: |
  `1e308 * 10` is past the largest float64, so it overflows to `inf`, and `inf` is greater than any finite number. Infinity minus infinity and zero times infinity have no answer, so they are `nan`; one over infinity is 0. `nan` is not equal to anything, even itself, so `nan == nan` is `False` and `nan != nan` is `True`; `max` keeps its first argument unless a later one compares greater, and no comparison with `nan` is ever `True`, so it keeps 1.0.
skills: [special]
''',
)

write(
    "recall/review-predict-epsilon.yaml",
    f'''id: review-predict-epsilon
type: predict_output
rev: 1
prompt: |
  Machine epsilon added to 1, whole and halved, in float64 and in float32; then the gap between `0.1 + 0.2` and `0.3` against four epsilons. What does the program print?
code: |
{block(REVIEW_EPSILON)}expected_output: |
{block(REVIEW_EPSILON_OUT)}explanation: |
  Epsilon is the gap between 1 and the next float, so adding it moves past 1; adding half of it lands exactly between two floats and rounds back to 1, in either width. The gap between `0.1 + 0.2` and `0.3` is a fraction of an epsilon, which is why a tolerance of a few epsilons, or `math.isclose`, calls them equal.
skills: [epsilon]
''',
)

mcq(
    "review-mcq-summing-a-million",
    "A million per-example losses are float32 and must be averaged. Which way of summing them is wrong, and why?",
    [
        "`np.sum` on the float32 array, which adds pairwise so that partners stay about the same size and few digits are dropped",
        "Converting to float64 first and summing, which has digits to spare for a million values",
        "A float32 running total in a Python loop: once it is large, each small loss loses its low digits, a million times",
        "`math.fsum` over the values, which keeps the exact sum and rounds once at the end",
    ],
    2,
    "The running total is the problem: with the total near a million and each loss near one, a float32 addition keeps about 7 digits, so each loss's last digits are dropped, always in the same direction. Pairwise summation, float64 accumulation and `fsum` all avoid that; the one-at-a-time float32 total is the version that drifts, as the worked example's hundred thousand tenths show.",
    ["accumulation"],
)

mcq(
    "review-mcq-why-subtract-the-max",
    "A stable softmax subtracts the largest logit from every logit before exponentiating. Why doesn't that change the answer, and what does it prevent?",
    [
        "It does change the answer slightly, but the error is far smaller than the overflow would be, so it is the lesser of two evils in practice",
        "It centres the logits so that the softmax sums to 1, which it otherwise wouldn't for large inputs of either sign",
        "It makes the largest probability exactly 1, which is what argmax needs to pick a class without ties",
        "A common factor exp(-m) cancels in the ratio, so the probabilities are the same; every exponent is at most 0, so none overflows",
    ],
    3,
    "`exp(x - m)` is `exp(x) * exp(-m)`, the same factor for every entry, and a common factor cancels when each entry is divided by the sum. So the probabilities are exactly the same in exact arithmetic, and in float arithmetic the shifted version is the one that can be computed at all: the largest exponent is 0, so the largest term is 1 and nothing overflows. The softmax always sums to 1; the subtraction is about range, not normalization.",
    ["special"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-what-a-float-holds/exercise.yaml",
    f'''id: example-what-a-float-holds
stage: worked_example
rev: 1
title: "What a float holds"
prompt: |
  A tenth opened up into its bits, the precision of float32 against float64, a tolerance, a sum that drifts and three that don't, and a softmax that overflows and one that doesn't. Press **Run**, then read how each part works.
steps:
  - label: "A tenth plus two tenths"
    lines: "{ln('print(0.1 + 0.2 == 0.3')}-{ln('print(0.1 + 0.2 == 0.3')}"
    note: "The sum isn't `0.3`; it is `0.30000000000000004`, and `0.1` itself, printed to twenty places, is `0.10000000000000000555`. Python's short `repr` shows the fewest digits that read back to the same float, which hides the rounding until you add."
  - label: "The bits of 0.1 as a float32"
    lines: "{ln('bits = struct.unpack')}-{ln('"which is"')}"
    note: "`struct` packs the float into its four bytes and unpacks them as an integer, so the 32 bits can be printed: one sign bit (0, positive), eight exponent bits (`01111011`, 123, which means `2**(123 - 127)`) and 23 mantissa bits (the digits after a leading 1). `(1 + 5033165 / 2**23) * 2**-4` is `0.10000000149011612`: the nearest float32 to a tenth."
  - label: "Epsilon and the integer cliff"
    lines: "{ln('epsilon:')}-{ln('isclose:')}"
    note: "Machine epsilon is the gap between 1 and the next float: about `1.2e-7` for float32, about `2.2e-16` for float64, roughly 7 and 16 decimal digits. With 24 significant bits, a float32 can't hold every integer past `2**24`, so 16,777,216 plus 1 stays 16,777,216; float64 reaches 16,777,217 without trouble. `math.isclose` and `np.allclose` compare with a tolerance instead of exactly."
  - label: "Ten tenths, four ways"
    lines: "{ln('tenths = [0.1] * 10')}-{ln('ten tenths, one at a time')}"
    note: "Added one at a time, the rounded tenths land at `0.9999999999999999`. Python's built-in `sum` has compensated for the rounding as it goes since version 3.12 and gets 1.0; `math.fsum` keeps the exact sum and rounds once, 1.0; and a single multiplication `0.1 * 10` also rounds to exactly 1.0. A plain running total is what drifts."
  - label: "A hundred thousand tenths in float32"
    lines: "{ln('total = np.float32(0)')}-{ln('the same with np.sum')}"
    note: "Added one at a time in float32, the total comes to {LOOP_TOTAL:,.2f} instead of 10,000: once the total is in the thousands, each tenth's low bits are dropped, always downwards or always upwards, a hundred thousand times. `np.sum` adds pairwise, so partners stay the same size, and gets {PAIRWISE_TOTAL:,.3f}: a thousandth off, where the running total was a unit and a half off."
  - label: "Infinity, NaN, and a softmax that overflows"
    lines: "{ln('overflow:')}-{ln('naive softmax of')}"
    note: "Past the largest float the result is `inf`; `inf - inf` is `nan`; and `nan` isn't equal to anything, itself included. A naive softmax of `[1000, 1001]` computes `exp(1000)`, which overflows, and divides infinity by infinity: `[nan nan]`. (The `errstate` block only silences the warnings so the result can be shown.)"
  - label: "The stable version, and log-sum-exp"
    lines: "{ln('shifted = np.exp(logits - logits.max())')}-{ln('stable softmax:')}"
    note: "Subtract the largest logit first: `exp([0, 1])` is finite, the ratios are unchanged, and the probabilities are `[0.269, 0.731]`. For the log of a sum of exponentials, add the maximum back: `1001 + log(exp(-1) + exp(0))`, which is 1001.313. Every cross-entropy in a library does exactly this."
''',
)
write("exercises/example-what-a-float-holds/solution.py", EXAMPLE)
write(
    "exercises/example-what-a-float-holds/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the tenth's bits, the precision lines, the sums and the two softmaxes."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-decode-a-float32/exercise.yaml",
    f'''id: fill-decode-a-float32
stage: fill_in
rev: 1
title: "Decode a float32"
prompt: |
  `decode_float32(x)` should split the 32 bits of a float32 into its sign bit (the top bit), its 8 exponent bits (the next eight) and its 23 mantissa bits (the rest), using shifts and masks from Bits, bytes and integers. Replace each `...` so the program decodes three values and rebuilds each from its parts:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The exponent sits just above the 23 mantissa bits, so shift right by 23 before masking with `0xFF`."
  - "The mantissa is the bottom 23 bits: a mask of 23 ones, `0x7FFFFF`."
skills: [representation]
''',
)
write("exercises/fill-decode-a-float32/starter.py", FILL_STARTER)
write("exercises/fill-decode-a-float32/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-decode-a-float32/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three decoded values."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_more_values():
    """2.0 is exponent 128 with a zero mantissa; 0.5 is exponent 126; the parts rebuild 3.75 exactly."""
    decode_float32 = function("decode_float32")
    assert decode_float32(2.0) == (0, 128, 0) and decode_float32(0.5) == (0, 126, 0)
    sign, exponent, mantissa = decode_float32(3.75)
    assert (-1) ** sign * (1 + mantissa / 2**23) * 2 ** (exponent - 127) == 3.75
''',
)
write("exercises/fill-decode-a-float32/wrong/shifts-too-far.py", FILL_WRONG)
write(
    "exercises/fill-decode-a-float32/wrong/typed-in.py",
    "def decode_float32(x):\n    return (0, 127, 0)\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-kahan-sum/exercise.yaml",
    f'''id: write-kahan-sum
stage: write
rev: 1
title: "A sum that carries its error"
prompt: |
  The starter adds a hundred thousand tenths one at a time in float32 and gets the wrong total. Write `kahan_sum(values)`, which sums in float32 but keeps a `carry` of the rounding error from each step and subtracts it from the next value: for each value, `adjusted = value - carry`, `new_total = total + adjusted`, `carry = (new_total - total) - adjusted`, `total = new_total`, all in `np.float32`. Return the total as a float, and print both sums:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`(new_total - total) - adjusted` is the part of `adjusted` that the addition rounded away; it is what the next step gives back."
  - "Keep every intermediate in `np.float32`; the point is that the method, not the precision, saves the sum."
skills: [accumulation]
''',
)
write("exercises/write-kahan-sum/starter.py", WRITE_SOLUTION.split("def kahan_sum")[0] + "def plain_sum" + WRITE_SOLUTION.split("def plain_sum")[1].split('print("kahan:"')[0])
write("exercises/write-kahan-sum/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-kahan-sum/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the plain and the Kahan totals."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_within_a_thousandth():
    """A hundred thousand tenths come to 10,000 within 0.001, and a thousand values of 0.001 to 1 within 1e-6."""
    kahan_sum = function("kahan_sum")
    assert abs(kahan_sum([0.1] * 100_000) - 10000) < 0.001
    assert abs(kahan_sum([0.001] * 1000) - 1.0) < 1e-6
''',
)
write("exercises/write-kahan-sum/wrong/no-carry.py", WRITE_WRONG)
write(
    "exercises/write-kahan-sum/wrong/typed-in.py",
    "def kahan_sum(values):\n    return 10000.0\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-a-float-toolkit/exercise.yaml",
    f'''id: build-a-float-toolkit
stage: build
rev: 1
title: "A float toolkit"
prompt: |
  Starting from a blank editor, write five functions:

  - `decode_float32(x)`: the tuple `(sign bit, exponent minus 127, mantissa bits)` of `x` stored as a float32 (`struct.pack(">f", x)` gives the four bytes; `struct.unpack(">I", ...)` reads them as one integer).
  - `close(a, b, rel=1e-9, abs_=0.0)`: whether `abs(a - b)` is at most the larger of `rel` times the larger magnitude and `abs_`.
  - `kahan_sum(values)`: the float32 sum with the carried rounding error, as a float.
  - `log_sum_exp(xs)`: `log(sum(exp(xs)))` computed without overflow, by pulling the largest value out.
  - `softmax(xs)`: the list `exp(xs) / sum(exp(xs))`, computed the stable way, using `math.exp` (which raises `OverflowError` rather than returning infinity, so the naive version fails loudly).

  Then print:

  ```python
  print(decode_float32(1.0), decode_float32(-2.5), decode_float32(0.1))
  print(close(0.1 + 0.2, 0.3), close(1.0, 1.0 + 1e-6), close(0.0, 1e-12, abs_=1e-9))
  print(round(kahan_sum([0.1] * 100_000), 3))
  print(round(log_sum_exp([1000.0, 1001.0]), 6), [round(p, 6) for p in softmax([1000.0, 1001.0])])
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks compare the decoding with `struct` for several values, test the tolerance both ways round, hold the sum to within a thousandth, and feed the softmax logits of 1,000 and of -1,000.
skills: [representation, epsilon, accumulation, special]
''',
)
write("exercises/build-a-float-toolkit/starter.py", "")
write("exercises/build-a-float-toolkit/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-a-float-toolkit/test_exercise.py",
    f'''import math
import struct

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_decode_against_struct():
    """For 2.0, 0.5, 3.75, -1.0 and 1e10, the parts rebuild the float32 value exactly."""
    decode_float32 = function("decode_float32")
    for x in (2.0, 0.5, 3.75, -1.0, 1e10):
        sign, exponent, mantissa = decode_float32(x)
        stored = struct.unpack(">f", struct.pack(">f", x))[0]
        assert (-1) ** sign * (1 + mantissa / 2**23) * 2**exponent == stored


def test_close_both_ways():
    """close is symmetric, accepts a relative gap of 1e-12, rejects one of 1e-6, and needs the absolute tolerance near zero."""
    close = function("close")
    assert close(1e6, 1e6 + 1e-6) and close(1e6 + 1e-6, 1e6)
    assert not close(1.0, 1.000001)
    assert not close(0.0, 1e-12) and close(0.0, 1e-12, abs_=1e-9)


def test_kahan_sum():
    """A hundred thousand tenths come to 10,000 within a thousandth."""
    kahan_sum = function("kahan_sum")
    assert abs(kahan_sum([0.1] * 100_000) - 10000) < 0.001


def test_log_sum_exp_and_softmax():
    """log_sum_exp of large and of very negative logits is finite and right; softmax sums to 1 and keeps the ratios."""
    log_sum_exp = function("log_sum_exp")
    softmax = function("softmax")
    assert math.isclose(log_sum_exp([1000.0, 1001.0]), 1001 + math.log(1 + math.exp(-1)))
    assert math.isclose(log_sum_exp([-1000.0, -1001.0]), -1000 + math.log(1 + math.exp(-1)))
    probabilities = softmax([1000.0, 1001.0, 1002.0])
    assert math.isclose(sum(probabilities), 1.0) and math.isclose(probabilities[2] / probabilities[1], math.e)
    assert math.isclose(sum(softmax([-1000.0, -999.0])), 1.0)
''',
)
write("exercises/build-a-float-toolkit/wrong/plain-sum.py", BUILD_PLAIN_SUM)
write("exercises/build-a-float-toolkit/wrong/naive-softmax.py", BUILD_NAIVE_SOFTMAX)
write("exercises/build-a-float-toolkit/wrong/biased-exponent.py", BUILD_BIASED_EXPONENT)
write(
    "exercises/build-a-float-toolkit/wrong/typed-in.py",
    "def decode_float32(x):\n    return (0, 0, 0)\n\n\ndef close(a, b, rel=1e-9, abs_=0.0):\n    return True\n\n\ndef kahan_sum(values):\n    return 10000.0\n\n\ndef log_sum_exp(xs):\n    return 1001.313262\n\n\ndef softmax(xs):\n    return [0.268941, 0.731059]\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-loss-that-overflowed/exercise.yaml",
    f'''id: debug-a-loss-that-overflowed
stage: debug
rev: 1
title: "A loss that went wrong"
prompt: |
  The program computes the cross-entropy (the loss that scores a softmax's probabilities) of three examples from their logits (raw scores) and checks that each softmax sums to 1. It should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: it crashes with `OverflowError: math range error`, because the softmax exponentiates the raw logits and `exp(1000)` is beyond the largest float (`math.exp` raises where NumPy's `exp` would give `inf`, and then `nan` in the division); subtract the largest logit from all of them first, which leaves the probabilities unchanged. Fix that, and the check prints `False`: it asks for the probabilities to sum to exactly `1.0`, and a sum of rounded floats lands a few last digits away. Compare with a tolerance, `math.isclose`.
skills: [special, epsilon]
''',
)
write("exercises/debug-a-loss-that-overflowed/starter.py", DEBUG_STARTER)
write("exercises/debug-a-loss-that-overflowed/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-loss-that-overflowed/test_exercise.py",
    f'''import math

from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints the three losses, their mean and a True."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_large_logits():
    """softmax survives logits of 5,000 and the loss of a confident right answer is near 0."""
    softmax = function("softmax")
    cross_entropy = function("cross_entropy")
    assert math.isclose(sum(softmax([5000.0, 4999.0, 4990.0])), 1.0)
    assert cross_entropy([50.0, 0.0, 0.0], 0) < 1e-10
''',
)
write("exercises/debug-a-loss-that-overflowed/wrong/still-overflows.py", DEBUG_STILL_NAIVE)
write("exercises/debug-a-loss-that-overflowed/wrong/still-exact.py", DEBUG_STILL_EXACT)
write(
    "exercises/debug-a-loss-that-overflowed/wrong/typed-in.py",
    "import math\n\n\ndef softmax(logits):\n    return [1 / len(logits)] * len(logits)\n\n\ndef cross_entropy(logits, true_index):\n    return 0.6411\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-stable-softmax/exercise.yaml",
    f'''id: review-stable-softmax
stage: review_code
rev: 1
title: "A stable softmax, from memory"
prompt: |
  Write `softmax(xs)`, the list `exp(xs)` scaled to sum to 1, computed so that large inputs don't overflow (`math.exp` raises `OverflowError` past about 709). Print it, rounded to 4 places, for `[1.0, 2.0, 3.0]` and for `[1000.0, 1001.0, 1002.0]`:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [special]
''',
)
write("exercises/review-stable-softmax/starter.py", "")
write("exercises/review-stable-softmax/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-stable-softmax/test_exercise.py",
    f'''import math

from checks import function, run


def test_the_output():
    """Prints the same three probabilities twice."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_sums_and_survives():
    """Sums to 1 for ordinary, huge and very negative inputs."""
    softmax = function("softmax")
    for xs in ([0.0, 0.0], [5000.0, 4000.0], [-5000.0, -5001.0]):
        assert math.isclose(sum(softmax(xs)), 1.0)
''',
)
write(
    "exercises/review-stable-softmax/wrong/naive.py",
    REVIEW_CODE_SOLUTION.replace("    biggest = max(xs)\n    weights = [math.exp(x - biggest) for x in xs]", "    weights = [math.exp(x) for x in xs]"),
)
write(
    "exercises/review-stable-softmax/wrong/typed-in.py",
    "def softmax(xs):\n    return [0.09, 0.2447, 0.6652]\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.hw.floating-point written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
