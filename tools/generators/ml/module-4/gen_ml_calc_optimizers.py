"""Writes the topic ml.calc.optimizers (Module 4's seventh topic). Run from
the repository root under uv (python -m uv run python <this file>), so every
program's expected output is captured from CPython rather than typed in.
Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.calc.optimizers")


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


VALLEY = '''def loss(p):
    return p[0] ** 2 + 100 * p[1] ** 2


def grad(p):
    return np.array([2 * p[0], 200 * p[1]])
'''
OPTIMIZERS = '''def plain(p, rate, steps):
    for step in range(steps):
        p = p - rate * grad(p)
    return p


def momentum(p, rate, beta, steps):
    v = np.zeros(len(p))
    for step in range(steps):
        v = beta * v + grad(p)
        p = p - rate * v
    return p


def plain_decayed(p, rate, steps):
    for step in range(steps):
        p = p - rate * 0.5 ** (step // 100) * grad(p)
    return p


def adam(p, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    m = np.zeros(len(p))
    s = np.zeros(len(p))
    for t in range(1, steps + 1):
        g = grad(p)
        m = beta1 * m + (1 - beta1) * g
        s = beta2 * s + (1 - beta2) * g**2
        m_hat = m / (1 - beta1**t)
        s_hat = s / (1 - beta2**t)
        p = p - rate * m_hat / (np.sqrt(s_hat) + eps)
    return p
'''

# --- the worked example ------------------------------------------------------------------

EXAMPLE = "import numpy as np\n\n\n" + VALLEY + "\n\n" + OPTIMIZERS + '''

start = np.array([10.0, 1.0])
checkpoints = (10, 50, 100, 200)
print("plain", [round(float(loss(plain(start, 0.005, n))), 4) for n in checkpoints])
print("momentum", [round(float(loss(momentum(start, 0.005, 0.9, n))), 4) for n in checkpoints])
print(np.round([plain(start, 0.009, n) for n in (1, 2, 3)], 3))
print("rate 0.015", round(float(loss(plain(start, 0.015, 10))), 1))
print("fixed 0.01", [round(float(loss(plain(start, 0.01, n))), 4) for n in checkpoints])
print("decayed 0.01", [round(float(loss(plain_decayed(start, 0.01, n))), 4) for n in checkpoints])
print("adam", [round(float(loss(adam(start, 0.3, n))), 4) for n in checkpoints])
print("adam's first step", np.round(adam(start, 0.3, 1), 3))
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + numbered(EXAMPLE) + EXAMPLE_OUT)
assert "e-" not in EXAMPLE_OUT and "e+" not in EXAMPLE_OUT and "nan" not in EXAMPLE_OUT, EXAMPLE_OUT
assert out(EXAMPLE.replace("start = np.array([10.0, 1.0])", "start = np.array([10.0000000001, 1.0])")) == EXAMPLE_OUT


def losses_of(label):
    line = next(line for line in EXAMPLE_OUT.splitlines() if line.startswith(label + " ["))
    return [float(v) for v in line[len(label) + 2 : -1].split(", ")]


PLAIN, MOMENTUM, FIXED, DECAYED, ADAM = (
    losses_of("plain"),
    losses_of("momentum"),
    losses_of("fixed 0.01"),
    losses_of("decayed 0.01"),
    losses_of("adam"),
)
assert MOMENTUM[2] < PLAIN[2] and DECAYED[3] < 1 < 100 <= FIXED[3] and ADAM[3] <= 0.01, (PLAIN, MOMENTUM, FIXED, DECAYED, ADAM)
# halving every 20 steps instead runs out of rate with x still far from home (loss near 20)
TOO_FAST = out(EXAMPLE.replace("0.5 ** (step // 100)", "0.5 ** (step // 20)"))
TOO_FAST_LOSS = float(next(line for line in TOO_FAST.splitlines() if line.startswith("decayed 0.01 ["))[len("decayed 0.01 [") : -1].split(", ")[3])
assert 15 < TOO_FAST_LOSS < 25, TOO_FAST_LOSS
assert EXAMPLE_OUT.endswith("adam's first step [9.7 0.7]\n"), EXAMPLE_OUT
RATE_TOO_LARGE = next(line for line in EXAMPLE_OUT.splitlines() if line.startswith("rate 0.015")).split()[-1]
assert float(RATE_TOO_LARGE) > 1e6, RATE_TOO_LARGE


def ln(text):
    """1-based number of the first line of EXAMPLE containing the text."""
    return next(i + 1 for i, line in enumerate(EXAMPLE.splitlines()) if text in line)


LINES = {
    "valley": f"{ln('def loss')}-{ln('return np.array([2 * p[0], 200')}",
    "plain_momentum": f"{ln('def plain(')}-{ln('def momentum(') + 5}",
    "decayed_def": f"{ln('def plain_decayed(')}-{ln('def plain_decayed(') + 3}",
    "adam_def": f"{ln('def plain_decayed(')}-{ln('def adam(') + 10}",
    "table": f"{ln('checkpoints = ')}-{ln('print(' + chr(34) + 'momentum')}",
    "zigzag": f"{ln('plain(start, 0.009')}",
    "too_large": f"{ln('rate 0.015')}",
    "schedule": f"{ln('fixed 0.01')}-{ln('decayed 0.01')}",
    "adam_runs": f"{ln('print(' + chr(34) + 'adam' + chr(34))}-{ln('first step')}",
}

# --- the fill-in ------------------------------------------------------------------------------

FILL_HEAD = '''import numpy as np


def grad(x):
    return 2 * x


def adam_steps(x, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    m = 0.0
    s = 0.0
    path = []
    for t in range(1, steps + 1):
        g = grad(x)
        m = beta1 * m + (1 - beta1) * g
        s = beta2 * s + (1 - beta2) * g**2
        m_hat = m / (1 - beta1**__T__)
        s_hat = s / (1 - beta2**t)
        x = x - rate * m_hat / (np.sqrt(__SHAT__) + eps)
        path.append(round(float(x), 4))
    return path


print(adam_steps(2.0, 0.1, 3))
print(adam_steps(-50.0, 0.1, 3))
'''
FILL_SOLUTION = FILL_HEAD.replace("__T__", "t").replace("__SHAT__", "s_hat")
FILL_STARTER = FILL_HEAD.replace("__T__", "...").replace("__SHAT__", "...")
FILL_NO_CORRECTION = FILL_SOLUTION.replace("        m_hat = m / (1 - beta1**t)\n        s_hat = s / (1 - beta2**t)\n", "        m_hat = m\n        s_hat = s\n")
FILL_OUT = out(FILL_SOLUTION)
print("fill:\n" + FILL_OUT)
assert FILL_OUT.startswith("[1.9, 1.8002, ") and FILL_OUT.splitlines()[1].startswith("[-49.9, "), FILL_OUT
assert out(FILL_NO_CORRECTION) != FILL_OUT

# --- the write -------------------------------------------------------------------------------------

WRITE_STARTER = "import numpy as np\n"
WRITE_SOLUTION = WRITE_STARTER + '''

def step_decay(rate0, step, every, factor):
    return rate0 * factor ** (step // every)


print([step_decay(0.1, step, 2, 0.5) for step in range(6)])
print([step_decay(0.3, step, 10, 0.5) for step in (0, 10, 20, 50)])
'''
WRITE_OUT = out(WRITE_SOLUTION)
print("write:\n" + WRITE_OUT)
assert WRITE_OUT == "[0.1, 0.1, 0.05, 0.05, 0.025, 0.025]\n[0.3, 0.15, 0.075, 0.009375]\n", WRITE_OUT

# --- the build ------------------------------------------------------------------------------------------

BUILD_SOLUTION = "import numpy as np\n\n\n" + VALLEY + '''

def momentum(grad, p, rate, beta, steps):
    v = np.zeros(len(p))
    path = []
    for step in range(steps):
        v = beta * v + grad(p)
        p = p - rate * v
        path.append(p)
    return path


def adam(grad, p, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    m = np.zeros(len(p))
    s = np.zeros(len(p))
    path = []
    for t in range(1, steps + 1):
        g = grad(p)
        m = beta1 * m + (1 - beta1) * g
        s = beta2 * s + (1 - beta2) * g**2
        m_hat = m / (1 - beta1**t)
        s_hat = s / (1 - beta2**t)
        p = p - rate * m_hat / (np.sqrt(s_hat) + eps)
        path.append(p)
    return path


start = np.array([10.0, 1.0])
print("plain", round(float(loss(momentum(grad, start, 0.005, 0.0, 100)[-1])), 4))
print("momentum", round(float(loss(momentum(grad, start, 0.005, 0.9, 100)[-1])), 4))
print("adam", round(float(loss(adam(grad, start, 0.3, 100)[-1])), 4))
print("adam's first step", np.round(adam(grad, start, 0.3, 1)[0], 3))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT.endswith("adam's first step [9.7 0.7]\n"), BUILD_OUT
assert BUILD_OUT.splitlines()[0] == f"plain {PLAIN[2]}" and BUILD_OUT.splitlines()[1] == f"momentum {MOMENTUM[2]}", BUILD_OUT
BUILD_NO_ACCUMULATION = BUILD_SOLUTION.replace("        v = beta * v + grad(p)\n", "        v = grad(p)\n")
BUILD_NO_CORRECTION = BUILD_SOLUTION.replace(
    "        m_hat = m / (1 - beta1**t)\n        s_hat = s / (1 - beta2**t)\n", "        m_hat = m\n        s_hat = s\n"
)
BUILD_NOT_SQUARED = BUILD_SOLUTION.replace("        s = beta2 * s + (1 - beta2) * g**2\n", "        s = beta2 * s + (1 - beta2) * np.abs(g)\n")
for wrong in (BUILD_NO_ACCUMULATION, BUILD_NO_CORRECTION, BUILD_NOT_SQUARED):
    assert out(wrong) != BUILD_OUT

# --- the debug ------------------------------------------------------------------------------------------------

DEBUG_SOLUTION = '''import numpy as np


def grad(x):
    return 2 * x


def adam(x, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    m = 0.0
    s = 0.0
    for t in range(1, steps + 1):
        g = grad(x)
        m = beta1 * m + (1 - beta1) * g
        s = beta2 * s + (1 - beta2) * g**2
        m_hat = m / (1 - beta1**t)
        s_hat = s / (1 - beta2**t)
        x = x - rate * m_hat / (np.sqrt(s_hat) + eps)
    return x


for steps in (1, 2, 50):
    print(steps, round(float(adam(2.0, 0.1, steps)), 4))
'''
DEBUG_STARTER = DEBUG_SOLUTION.replace("    for t in range(1, steps + 1):", "    for t in range(steps):").replace(
    "        s = beta2 * s + (1 - beta2) * g**2\n", "        s = beta2 * s + (1 - beta2) * g\n"
)
DEBUG_RANGE_ONLY = DEBUG_SOLUTION.replace("        s = beta2 * s + (1 - beta2) * g**2\n", "        s = beta2 * s + (1 - beta2) * g\n")
DEBUG_OUT = out(DEBUG_SOLUTION)
print("debug:\n" + DEBUG_OUT)
assert DEBUG_OUT.startswith("1 1.9\n2 1.8002\n50 "), DEBUG_OUT
assert out(DEBUG_RANGE_ONLY) != DEBUG_OUT
crash = subprocess.run([sys.executable, "-c", DEBUG_STARTER], capture_output=True, text=True)
assert crash.returncode != 0 and "ZeroDivisionError" in crash.stderr, crash.stderr[-300:]

# --- predict items ------------------------------------------------------------------------------------------------

PREDICT_MOMENTUM = '''x = 2.0
v = 0.0
for step in range(2):
    g = 2 * x
    v = 0.5 * v + g
    x = x - 0.1 * v
    print(x)
'''
PREDICT_MOMENTUM_OUT = out(PREDICT_MOMENTUM)
print("predict momentum:\n" + PREDICT_MOMENTUM_OUT)
assert PREDICT_MOMENTUM_OUT == "1.6\n1.08\n", PREDICT_MOMENTUM_OUT

REVIEW_DECAY = '''rate = 0.1
for step in range(6):
    if step > 0 and step % 2 == 0:
        rate = rate / 2
    print(step, rate)
'''
REVIEW_DECAY_OUT = out(REVIEW_DECAY)
print("review decay:\n" + REVIEW_DECAY_OUT)
assert REVIEW_DECAY_OUT == "0 0.1\n1 0.1\n2 0.05\n3 0.05\n4 0.025\n5 0.025\n", REVIEW_DECAY_OUT

REVIEW_CODE_STARTER = '''x = 2.0
v = 0.0
'''
REVIEW_CODE_SOLUTION = REVIEW_CODE_STARTER + '''

def momentum_step(x, v, g, rate, beta):
    v = beta * v + g
    return x - rate * v, v


for step in range(2):
    x, v = momentum_step(x, v, 2 * x, 0.1, 0.5)
    print(x)
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
print("review code:\n" + REVIEW_CODE_OUT)
assert REVIEW_CODE_OUT == "1.6\n1.08\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.calc.optimizers
kind: topic
status: ready
title: "Optimizers beyond plain gradient descent"
summary: "Momentum, learning-rate schedules and Adam, each in a few lines, compared on the same problem."
prerequisites: [ml.calc.descent-in-many-dimensions, ml.calc.backpropagation]
packages: [numpy]
estimated_minutes: 50
rev: 1
objectives:
  - "Add momentum to gradient descent and say what it does on a long narrow valley."
  - "Decay the learning rate on a schedule, and say when that helps."
  - "Write Adam in a few lines and compare it with plain descent on the same function."
  - "Choose an optimizer and learning rate from a loss curve, and say why."
# Linked, never copied or embedded: Distill is CC BY 4.0; arXiv papers are
# linked under arXiv's licence; NumPy's documentation is under the NumPy
# licence (BSD-3-Clause).
resources:
  - title: "Why Momentum Really Works (Gabriel Goh, Distill, 2017)"
    url: https://distill.pub/2017/momentum/
    type: interactive
    use: link
    license: CC BY 4.0
  - title: "Adam: A Method for Stochastic Optimization (Diederik Kingma and Jimmy Ba, 2014), the algorithm on page 2"
    url: https://arxiv.org/abs/1412.6980
    type: reading
    use: link
    license: arXiv non-exclusive licence (linked, not copied)
  - title: "numpy.sqrt (the NumPy developers)"
    url: https://numpy.org/doc/stable/reference/generated/numpy.sqrt.html
    type: reading
    use: link
    license: BSD-3-Clause (NumPy documentation)
practice:
  - example-three-optimizers-on-a-valley
  - parsons-momentum-update
  - mcq-momentum-in-a-valley
  - predict-two-momentum-steps
  - mcq-when-to-decay
  - fill-adam
  - write-step-decay
prove:
  build: build-momentum-and-adam
  debug: debug-adam
  explain:
    prompt: |
      A teammate shows you three runs of the same model. With plain gradient descent at a fixed rate the loss falls quickly, then bounces around 0.3 for the rest of the run. With momentum it reaches 0.3 in a third of the steps, then bounces too. With Adam it reaches 0.2 quickly and bounces there. In your own words: what does momentum change about the step, and why does that help in a long narrow valley? What does Adam adapt, and why is its very first step the same size whatever the gradient? Why decay the learning rate during a run, and which symptom in these curves calls for it? And what would you run next?
    rubric:
      - id: momentum
        required: true
        description: "Momentum keeps a velocity, v = beta * v + gradient, and steps along it; gradients that point the same way step after step (along the valley) add up into speed, while gradients that flip sign (across the valley) cancel, so the zigzag shrinks and the slow direction speeds up."
      - id: adam
        required: true
        description: "Adam keeps a running mean of the gradient (momentum) and a running mean of its square, and divides one by the root of the other, so each coordinate's step is about the rate times the sign of its gradient at first (the two bias corrections make the first step exactly that), and steep coordinates don't dominate flat ones."
      - id: decay
        required: true
        description: "A rate large enough to cross the landscape fast is too large to settle at the bottom, so the loss bounces at a floor; shrinking the rate on a schedule (halving every so often, or smoothly) lets the run start fast and finish precise. Bouncing at a floor after a fast fall is the symptom."
      - id: next
        required: false
        description: "Keep momentum or Adam for speed and add a decay schedule (or lower the rate once the bounce starts), then compare the held-out loss, not just the training curve."
    model_answer: |
      Plain descent steps by the gradient at the current point and forgets everything before. Momentum keeps a velocity: each step the gradient is added to it, scaled by a factor like 0.9 of the previous velocity, and the step follows the velocity. In a long narrow valley the gradient across the valley flips sign every step, so those contributions cancel out of the velocity and the zigzag shrinks, while the gradient along the valley points the same way every step, so it accumulates and the slow direction speeds up: that's why it reached the floor three times faster. Adam adapts the step to each coordinate. It keeps a running average of the gradient, like momentum, and a running average of the gradient squared, and it steps by the first divided by the square root of the second, so a coordinate with big gradients gets a proportionally smaller step and a coordinate with tiny gradients a larger one. Both averages start at zero and are corrected for that, which is why on the first step the ratio is exactly the gradient over its own size: a step of exactly the rate in each coordinate, whatever the gradient was. All three runs bounce at a floor for the same reason: a rate big enough to cross the landscape quickly is too big to settle into the bottom, so the last steps overshoot back and forth. The symptom is a fast fall and then a noisy flat line, and the fix is a schedule: shrink the rate as the run goes on, halving it every so many steps or decaying it smoothly, so the run starts fast and finishes precise. Next I'd rerun momentum or Adam with a decay schedule, watch the floor drop, and compare the held-out loss, since the training curve alone doesn't say which model is better.
review_pool:
  - review-predict-a-schedule
  - review-mcq-what-adam-divides-by
  - review-mcq-choose-from-the-curve
  - review-momentum-step
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: momentum
    description: "Add momentum to descent and say what it does in a long narrow valley"
  - id: schedule
    description: "Decay the learning rate on a schedule and say when that helps"
  - id: adam
    description: "Write Adam in a few lines and say what it adapts"
  - id: choose
    description: "Choose an optimizer and learning rate from a loss curve"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Plain gradient descent works, and on the loss surfaces real models have it is slow: long narrow valleys make it zigzag across the steep direction while it crawls along the flat one, and one learning rate has to serve every weight. The optimizers in every training script are small changes to the update line that fix those two problems. This topic writes three of them, momentum, a learning-rate schedule and Adam, in a few lines each, and compares them on one valley, so the names in a training script become things the learner has built.

The main resource is **Distill's _Why Momentum Really Works_**, an interactive article whose pictures of a valley you can drag are the best explanation of momentum there is; about 30 minutes. The Adam paper's page 2 has the algorithm in eight lines, the same eight you'll write. Watch for:

- **The condition number:** how much steeper the steep direction is than the flat one, which is what makes a valley long and narrow.
- **Velocity:** gradients that agree add up; gradients that flip cancel.
- **Why the first Adam step is always the rate.**

</Intro>

<Resource index={{0}} />

<Recap>

- **The valley.** `x² + 100y²` is a hundred times steeper in `y` than in `x`. Plain descent needs a rate below `2 / 200 = 0.01` to stay stable in `y`, and at a safe rate like 0.005 `x` shrinks by only 1 percent a step: it crawls along the valley. From `(10, 1)` the loss after 100 steps is still {PLAIN[2]}, and after 200 it is {PLAIN[3]}. At 0.015 each step leaves `y` at `-2` times what it was, and the loss after 10 steps is {RATE_TOO_LARGE}.
- **Momentum** keeps a velocity: `v = beta * v + grad(p)`, then `p = p - rate * v`, with `beta` usually 0.9. Gradients that point the same way step after step (along the valley) accumulate into speed, up to `1 / (1 - beta)` = 10 times the plain step; gradients that flip sign (across the valley) cancel. Same rate, same start: the loss after 100 steps is {MOMENTUM[2]}.
- **A schedule** shrinks the rate as the run goes on: **step decay** `rate * factor ** (step // every)` (halve it every so many steps), or a smooth decay. A rate big enough to move fast can be too big to settle: at exactly 0.01 each step leaves `y` at `-1` times what it was, so `y` bounces between `1` and `-1` forever and the loss sits at a floor of 100 ({FIXED[3]} after 200 steps); the same run with the rate halved every 100 steps settles and keeps falling ({DECAYED[3]} after 200 steps). Decay too fast, though, and the rate runs out before `x` gets home: halving every 20 steps freezes this run with a loss near 20. How quickly to decay is a knob: start fast, finish precise, and don't run out of rate.
- **Adam** keeps two running averages per coordinate, of the gradient (`m`, with `beta1 = 0.9`) and of its square (`s`, with `beta2 = 0.999`), corrects both for starting at zero (`m / (1 - beta1 ** t)`, `s / (1 - beta2 ** t)`), and steps by `rate * m_hat / (sqrt(s_hat) + eps)`. Dividing by the gradient's typical size makes each coordinate's step about `rate` times the sign of its gradient at first: steep coordinates don't dominate flat ones, and the very first step is exactly `rate` in every coordinate (`[9.7, 0.7]` from `(10, 1)` at 0.3, though the gradient was `[20, 200]`). On the valley at rate 0.3, thirty times plain descent's ceiling, the loss after 100 steps is {ADAM[2]} and after 200 it is {ADAM[3]}.
- **Reading the curves.** Falling fast then flat near zero: done. Falling fast then bouncing at a floor: the rate is too big to settle; decay it. Falling slowly and steadily: the rate is too small, or the valley is narrow; try momentum or Adam. Climbing: too large for any of them; cut it.
- **Choosing.** Adam with its default `0.9, 0.999` and a rate of `1e-3` is the usual first try for a network; momentum with decay often ends lower once tuned; plain descent is the baseline you compare them with. The learning rate matters more than the choice among them.
- **In machine learning:** `torch.optim.SGD(momentum=0.9)`, `torch.optim.Adam` and the schedulers are these lines; the checkpoint trains last topic's network with one of them.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-momentum-update.yaml",
    '''id: parsons-momentum-update
type: parsons
rev: 1
prompt: |
  Put the lines in order to take ten momentum steps on `x²` from `x = 2`, with a learning rate of 0.1 and `beta = 0.9`, printing the final `x` rounded to 4 places. One line is a decoy that doesn't belong.
lines:
  - 'x, v = 2.0, 0.0'
  - 'for step in range(10):'
  - '    g = 2 * x'
  - '    v = 0.9 * v + g'
  - '    x = x - 0.1 * v'
  - 'print(round(x, 4))'
distractors:
  - '    v = 0.9 * g + v'
explanation: |
  Each step the gradient is added to the velocity, which keeps 0.9 of its old value, and the step follows the velocity. The decoy keeps all of the old velocity and only 0.9 of the gradient: it never forgets, so it overshoots and keeps growing. With momentum the ten steps carry `x` past zero and back (it prints a small negative number), which is the overshoot a velocity brings.
skills: [momentum]
''',
)

write(
    "recall/mcq-momentum-in-a-valley.yaml",
    '''id: mcq-momentum-in-a-valley
type: mcq
rev: 1
prompt: |
  On a long narrow valley, plain descent zigzags across the steep direction while crawling along the flat one. What does momentum change?
choices:
  - 'Gradients that flip sign step after step (across the valley) cancel out of the velocity, so the zigzag shrinks; gradients that agree step after step (along the valley) add up, so the crawl becomes a run'
  - 'It makes every step longer by the same factor, which is the same as raising the learning rate'
  - 'It makes the steep direction steeper, so descent stays away from the walls'
  - 'It skips the steps whose gradient is small'
answer: 0
explanation: |
  The velocity is a running sum of past gradients, discounted by `beta`. Across the valley the gradient alternates in sign, so the sum stays small; along it the gradient keeps its sign, so the sum grows towards `1 / (1 - beta)` times a single step. That's different from a larger rate, which would make the zigzag worse too.
skills: [momentum]
''',
)

write(
    "recall/predict-two-momentum-steps.yaml",
    f'''id: predict-two-momentum-steps
type: predict_output
rev: 1
prompt: |
  Two momentum steps on `x²` from `x = 2`, rate 0.1, `beta = 0.5`. What does the program print?
code: |
{block(PREDICT_MOMENTUM)}expected_output: |
{block(PREDICT_MOMENTUM_OUT)}explanation: |
  Step 1: the gradient is 4, the velocity becomes `0.5 * 0 + 4 = 4`, and `x` moves to `2 - 0.4 = 1.6`. Step 2: the gradient is 3.2, the velocity is `0.5 * 4 + 3.2 = 5.2`, and `x` moves to `1.6 - 0.52 = 1.08`. The second step is longer than plain descent's would be (0.32), because the velocity remembers the first.
skills: [momentum]
''',
)

write(
    "recall/mcq-when-to-decay.yaml",
    '''id: mcq-when-to-decay
type: mcq
rev: 1
prompt: |
  A run's loss falls quickly for 200 steps, then bounces between 0.28 and 0.34 for the remaining 800 steps without getting lower. What is the most likely cause, and the fix?
choices:
  - 'The rate is big enough to cross the landscape but too big to settle at the bottom, so the last steps overshoot back and forth; decay the rate on a schedule, so the run starts fast and finishes precise'
  - 'The rate is too small; raise it'
  - 'The model has converged; 0.3 is the floor'
  - 'Momentum has been left on; turn it off'
answer: 0
explanation: |
  Bouncing at a floor after a fast fall is the signature of a fixed rate that's right for the start and wrong for the end. A schedule (halve the rate every so many steps, or shrink it smoothly) keeps the early speed and gives the late precision. A converged run sits still at its floor rather than bouncing across it.
skills: [schedule, choose]
''',
)

write(
    "recall/review-predict-a-schedule.yaml",
    f'''id: review-predict-a-schedule
type: predict_output
rev: 1
prompt: |
  A step-decay schedule written as a loop. What does the program print?
code: |
{block(REVIEW_DECAY)}expected_output: |
{block(REVIEW_DECAY_OUT)}explanation: |
  The rate halves at steps 2 and 4 (every second step, skipping step 0), so it holds for two steps at a time: 0.1, 0.1, 0.05, 0.05, 0.025, 0.025. The same schedule in one line is `0.1 * 0.5 ** (step // 2)`.
skills: [schedule]
''',
)

write(
    "recall/review-mcq-what-adam-divides-by.yaml",
    '''id: review-mcq-what-adam-divides-by
type: mcq
rev: 1
prompt: |
  Adam steps by `rate * m_hat / (sqrt(s_hat) + eps)`. What does dividing by `sqrt(s_hat)` do?
choices:
  - 'It divides each coordinate''s step by that coordinate''s typical gradient size, so steep coordinates get smaller steps and flat ones larger, and every step starts out about `rate` in size'
  - 'It makes the step proportional to the gradient squared, so big gradients move further'
  - 'It keeps the step from ever being larger than `eps`'
  - 'It averages the step over all the coordinates'
answer: 0
explanation: |
  `s_hat` is a running average of the squared gradient, per coordinate, so its square root is the gradient''s typical size there. The ratio of a gradient to its own typical size is about plus or minus one, which is why Adam''s steps are about the rate everywhere and its first step exactly the rate. `eps` only stops a division by zero.
skills: [adam]
''',
)

write(
    "recall/review-mcq-choose-from-the-curve.yaml",
    '''id: review-mcq-choose-from-the-curve
type: mcq
rev: 1
prompt: |
  Four runs of the same model, each described by its loss curve. Which run should you change, and how?

  - Run A (plain descent, rate 0.01): falls slowly and steadily, still falling at the end.
  - Run B (Adam, rate 0.001): falls fast, then sits still near its floor.
  - Run C (momentum, rate 0.1): climbs from the first step.
  - Run D (Adam, rate 0.01): falls fast, then bounces across a floor.
choices:
  - 'A is too slow (raise the rate or switch to momentum or Adam); C''s rate is too large (cut it); D wants a decay schedule; B looks done'
  - 'All four need a larger rate'
  - 'B is the failure: a loss that sits still means nothing is learned'
  - 'C is fine: climbing early is normal for momentum'
answer: 0
explanation: |
  Each curve names its own fix. Steady slow falling is a rate too small or a narrow valley; climbing is a rate too large for any optimizer; bouncing at a floor is a rate that should decay; sitting still at a low floor after a fast fall is what finished looks like. Only the held-out loss says whether B''s floor is good enough.
skills: [choose]
''',
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-three-optimizers-on-a-valley/exercise.yaml",
    f'''id: example-three-optimizers-on-a-valley
stage: worked_example
rev: 1
title: "Three optimizers on one valley"
prompt: |
  This program runs plain descent, momentum, a decaying rate and Adam on the valley `x² + 100y²` from the same start, and prints the loss each reaches after 10, 50, 100 and 200 steps, three points of a zigzag, a rate that diverges, a rate that bounces forever until it's decayed, and Adam's first step. Press **Run**, then read how each part works.
steps:
  - label: "The valley"
    lines: "{LINES['valley']}"
    note: "`x² + 100y²` is a hundred times steeper in `y` than in `x`: a long narrow valley running along the `x` axis, with gradient `[2x, 200y]`. The ratio of the two steepnesses, 100, is what makes plain descent struggle: the steep direction sets the largest safe rate, `2 / 200 = 0.01`, and at that rate the flat direction barely moves."
  - label: "Plain descent and momentum"
    lines: "{LINES['plain_momentum']}"
    note: "Plain descent is the loop from the descent topic. Momentum adds one line: a velocity `v` that keeps `beta` of its old value and adds the gradient, and the step follows `v` instead of the gradient. Along the valley the gradients agree and pile up in `v`; across it they alternate and cancel."
  - label: "A decaying rate, and Adam"
    lines: "{LINES['adam_def']}"
    note: "`plain_decayed` halves the rate every 100 steps: `0.5 ** (step // 100)`. Adam keeps two running averages per coordinate, `m` of the gradient and `s` of its square; both start at zero, so both are divided by `1 - beta ** t` to correct for that; the step is `m_hat` over the square root of `s_hat`, so each coordinate's step is scaled by its own typical gradient size."
  - label: "Crawling against running"
    lines: "{LINES['table']}"
    note: "Same start, same safe rate of 0.005. Plain descent kills `y` at once but shrinks `x` by one percent a step: its loss is still {PLAIN[2]} after 100 steps and {PLAIN[3]} after 200. Momentum's velocity along the valley builds up to ten times the plain step, and its loss after 100 steps is {MOMENTUM[2]}."
  - label: "The zigzag"
    lines: "{LINES['zigzag']}"
    note: "Three points of plain descent at 0.009, just under the ceiling: `y` flips sign every step (`-0.8`, `0.64`, `-0.512`) while `x` creeps from 10 to 9.5. That's the picture: bouncing between the walls, crawling along the floor."
  - label: "Too large a rate"
    lines: "{LINES['too_large']}"
    note: "At 0.015 the `y` step multiplies the old value by `1 - 0.015 * 200 = -2`: each step lands twice as far up the far wall, and after ten steps the loss is {RATE_TOO_LARGE}. The steep direction sets the ceiling, and that ceiling is what momentum and Adam work around."
  - label: "Bouncing at a floor, and a schedule"
    lines: "{LINES['schedule']}"
    note: "At exactly 0.01 each step multiplies `y` by `-1`: `y` bounces between 1 and -1 forever and the loss can never drop below 100 ({FIXED[3]} after 200 steps). Halving the rate every 100 steps lets `y` settle and the run keep falling ({DECAYED[3]} after 200 steps). Halve it every 20 steps instead and the rate runs out before `x` gets home: that run freezes with a loss near 20. A rate that's right for the start can be wrong for the end; a schedule serves both, if it decays slowly enough."
  - label: "Adam"
    lines: "{LINES['adam_runs']}"
    note: "Adam at rate 0.3, thirty times plain descent's ceiling, is safe because it divides each coordinate's step by that coordinate's gradient size: its first step is exactly 0.3 in both coordinates, `[9.7, 0.7]`, though the gradient was `[20, 200]`. Its loss is {ADAM[2]} after 100 steps and {ADAM[3]} after 200."
''',
)
write("exercises/example-three-optimizers-on-a-valley/solution.py", EXAMPLE)
write(
    "exercises/example-three-optimizers-on-a-valley/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints plain descent's and momentum's losses, three points of a zigzag, a diverging rate, a fixed rate against a decayed one, Adam's losses and Adam's first step."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-adam/exercise.yaml",
    f'''id: fill-adam
stage: fill_in
rev: 1
title: "Adam's two corrections"
prompt: |
  `adam_steps` runs Adam on `x²` and returns the path. Two pieces are missing: the correction of `m` for starting at zero, which divides by `1 - beta1` to the power of the step number, and the quantity whose square root the step is divided by. Replace each `...` so the program prints:

  ```
{block(FILL_OUT)}  ```

  Note the first step: exactly the rate, 0.1, whether the start is 2 or -50. The program fails until every `...` is replaced.
hints:
  - "`t` counts the steps from 1; `m_hat = m / (1 - beta1**t)`."
  - "The step divides `m_hat` by `np.sqrt(s_hat) + eps`."
skills: [adam]
''',
)
write("exercises/fill-adam/starter.py", FILL_STARTER)
write("exercises/fill-adam/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-adam/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two paths."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_first_step_is_the_rate():
    """From any start the first step has size exactly the rate, against the gradient."""
    adam_steps = function("adam_steps")
    assert adam_steps(7.0, 0.25, 1) == [6.75]
    assert adam_steps(-3.0, 0.01, 1) == [-2.99]
''',
)
write("exercises/fill-adam/wrong/no-correction.py", FILL_NO_CORRECTION)
write(
    "exercises/fill-adam/wrong/typed-in.py",
    '''import numpy as np


def adam_steps(x, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):
    return [round(x - rate * (i + 1), 4) for i in range(steps)]


'''
    + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-step-decay/exercise.yaml",
    f'''id: write-step-decay
stage: write
rev: 1
title: "A step-decay schedule"
prompt: |
  Write `step_decay(rate0, step, every, factor)`, which returns the learning rate to use at `step`: the starting rate `rate0`, multiplied by `factor` once for every `every` steps completed (`step // every` times). Then print the rates for steps 0 to 5 with `every = 2` and `factor = 0.5` starting from 0.1, and for steps 0, 10, 20 and 50 with `every = 10` and `factor = 0.5` starting from 0.3:

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`step // every` is the number of whole decays so far."
  - "`factor ** 0` is 1, so step 0 gets the starting rate."
skills: [schedule]
''',
)
write("exercises/write-step-decay/starter.py", WRITE_STARTER)
write("exercises/write-step-decay/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-step-decay/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the two lists of rates."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_other_schedules():
    """A factor of 0.1 every 100 steps: step 99 keeps the start, step 100 is a tenth, step 250 a hundredth."""
    step_decay = function("step_decay")
    assert step_decay(1.0, 99, 100, 0.1) == 1.0
    assert abs(step_decay(1.0, 100, 100, 0.1) - 0.1) < 1e-12
    assert abs(step_decay(1.0, 250, 100, 0.1) - 0.01) < 1e-12
''',
)
write(
    "exercises/write-step-decay/wrong/decays-every-step.py",
    WRITE_STARTER + '''

def step_decay(rate0, step, every, factor):
    return rate0 * factor ** (step / every)


print([step_decay(0.1, step, 2, 0.5) for step in range(6)])
print([step_decay(0.3, step, 10, 0.5) for step in (0, 10, 20, 50)])
''',
)
write(
    "exercises/write-step-decay/wrong/typed-in.py",
    WRITE_STARTER + '''

def step_decay(rate0, step, every, factor):
    return rate0


print([0.1, 0.1, 0.05, 0.05, 0.025, 0.025])
print([0.3, 0.15, 0.075, 0.009375])
''',
)

# --- the proof ----------------------------------------------------------------------------------------------------

write(
    "exercises/build-momentum-and-adam/exercise.yaml",
    f'''id: build-momentum-and-adam
stage: build
rev: 1
title: "Momentum and Adam"
prompt: |
  Starting from a blank editor, write two optimizers that take a gradient function and return the **path**, a list of the point after each step:

  - `momentum(grad, p, rate, beta, steps)`: `v = beta * v + grad(p)`, then `p = p - rate * v`, starting from `v` all zeros. With `beta = 0` it is plain descent.
  - `adam(grad, p, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8)`: the running averages `m` and `s` of the gradient and its square, both corrected for starting at zero, and the step `rate * m_hat / (np.sqrt(s_hat) + eps)`, with `t` counting from 1.

  Then, on the valley `x² + 100y²` (gradient `[2x, 200y]`) from `[10, 1]`, print the loss after 100 steps of plain descent (`momentum` with `beta = 0`) at rate 0.005, of momentum at rate 0.005 with `beta = 0.9`, and of Adam at rate 0.3, each rounded to 4 places, and Adam's first point rounded to 3:

  ```
{block(BUILD_OUT)}  ```

  The checks run both on other functions, and check Adam's first step from any start.
skills: [momentum, adam, choose]
''',
)
write("exercises/build-momentum-and-adam/starter.py", "")
write("exercises/build-momentum-and-adam/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-momentum-and-adam/test_exercise.py",
    f'''import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def grad_round(p):
    return 2 * p


def grad_valley(p):
    return np.array([2 * p[0], 200 * p[1]])


def test_the_output():
    """Prints the three losses and Adam's first point."""
    assert run() == {BUILD_OUT!r}


def test_momentum_with_beta_zero_is_plain_descent():
    """With beta 0, each step halves the point on x² + y² at rate 0.25; with beta 0.5 the second step is longer."""
    momentum = function("momentum")
    path = momentum(grad_round, np.array([4.0, 2.0]), 0.25, 0.0, 3)
    assert len(path) == 3
    assert np.allclose(path[-1], [0.5, 0.25])
    path_m = momentum(grad_round, np.array([2.0, 0.0]), 0.1, 0.5, 2)
    assert np.allclose(path_m[0], [1.6, 0.0]) and np.allclose(path_m[1], [1.08, 0.0])


def test_momentum_beats_plain_on_the_valley():
    """After 100 steps at rate 0.005, momentum's loss is below plain descent's."""
    momentum = function("momentum")
    start = np.array([10.0, 1.0])
    plain = momentum(grad_valley, start, 0.005, 0.0, 100)[-1]
    fast = momentum(grad_valley, start, 0.005, 0.9, 100)[-1]
    assert grad_valley(fast) @ fast < grad_valley(plain) @ plain


def test_adams_first_step_and_its_arrival():
    """Adam's first step is exactly the rate against the gradient's sign, from any start; after 300 steps at rate 0.05 on x² + y² it is within 0.01 of the origin."""
    adam = function("adam")
    first = adam(grad_valley, np.array([-7.0, 0.002]), 0.25, 1)[0]
    assert np.allclose(first, [-6.75, -0.248], atol=1e-6)
    end = adam(grad_round, np.array([3.0, -4.0]), 0.05, 300)[-1]
    assert np.linalg.norm(end) < 0.01
''',
)
write("exercises/build-momentum-and-adam/wrong/velocity-not-kept.py", BUILD_NO_ACCUMULATION)
write("exercises/build-momentum-and-adam/wrong/no-bias-correction.py", BUILD_NO_CORRECTION)
write("exercises/build-momentum-and-adam/wrong/s-not-squared.py", BUILD_NOT_SQUARED)
write(
    "exercises/build-momentum-and-adam/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def momentum(grad, p, rate, beta, steps):\n    return [p] * steps\n\n\n"
    + "def adam(grad, p, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):\n    return [np.array([9.7, 0.7])] * steps\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-adam/exercise.yaml",
    f'''id: debug-adam
stage: debug
rev: 1
title: "An Adam that divides by zero"
prompt: |
  This program runs Adam on `x²` from 2 at rate 0.1 and should print `x` after 1, 2 and 50 steps:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the first is a `ZeroDivisionError` in the bias correction, because `t` starts at 0 and `1 - beta1 ** 0` is zero; Adam counts its steps from 1. Fix that and it runs, but the first step isn't 0.1 and the numbers drift: `s` is meant to average the gradient **squared**, and this version averages the gradient itself.
skills: [adam]
''',
)
write("exercises/debug-adam/starter.py", DEBUG_STARTER)
write("exercises/debug-adam/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-adam/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints x after 1, 2 and 50 steps."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_first_step_from_elsewhere():
    """From -5 at rate 0.2 the first step lands at -4.8, and 200 steps at rate 0.05 end within 0.5 of zero."""
    adam = function("adam")
    assert abs(adam(-5.0, 0.2, 1) + 4.8) < 1e-9
    assert abs(adam(-5.0, 0.05, 200)) < 0.5
''',
)
write("exercises/debug-adam/wrong/range-only.py", DEBUG_RANGE_ONLY)
write(
    "exercises/debug-adam/wrong/typed-in.py",
    "import numpy as np\n\n\n"
    + "def adam(x, rate, steps, beta1=0.9, beta2=0.999, eps=1e-8):\n    return x - rate * steps\n\n\n"
    + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

# --- review pool: a code exercise ---------------------------------------------------------------------------------

write(
    "exercises/review-momentum-step/exercise.yaml",
    f'''id: review-momentum-step
stage: review_code
rev: 1
title: "One momentum step, from memory"
prompt: |
  Write `momentum_step(x, v, g, rate, beta)`, which returns the new position and the new velocity after one momentum step (`v = beta * v + g`, then `x = x - rate * v`). Then take two steps on `x²` (gradient `2 * x`) from the starter's `x = 2` with rate 0.1 and `beta = 0.5`, printing `x` after each:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [momentum]
''',
)
write("exercises/review-momentum-step/starter.py", REVIEW_CODE_STARTER)
write("exercises/review-momentum-step/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-momentum-step/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 1.6 then 1.08."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_the_velocity_is_returned():
    """From x = 1, v = 2, g = 3 at rate 0.1 and beta 0.9: v becomes 4.8 and x becomes 0.52."""
    momentum_step = function("momentum_step")
    x, v = momentum_step(1.0, 2.0, 3.0, 0.1, 0.9)
    assert abs(v - 4.8) < 1e-12
    assert abs(x - 0.52) < 1e-12
''',
)
write(
    "exercises/review-momentum-step/wrong/forgets-the-velocity.py",
    REVIEW_CODE_STARTER + '''

def momentum_step(x, v, g, rate, beta):
    v = g
    return x - rate * v, v


for step in range(2):
    x, v = momentum_step(x, v, 2 * x, 0.1, 0.5)
    print(x)
''',
)
write(
    "exercises/review-momentum-step/wrong/typed-in.py",
    REVIEW_CODE_STARTER + '''

def momentum_step(x, v, g, rate, beta):
    return 1.6, 4.0


print(1.6)
print(1.08)
''',
)

print("ml.calc.optimizers written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
