"""Writes the topic ml.dsa.stacks-queues-recursion (Module 6's third topic).
Run from the repository root under uv (python -m uv run python <this file>),
so every program's expected output is captured from CPython rather than typed
in. Both runtimes cap recursion at 1,000 frames, so the RecursionError in the
worked example is deterministic. Files are written as bytes with LF endings."""

import pathlib
import subprocess
import sys

ROOT = pathlib.Path("content/topics/ml.dsa.stacks-queues-recursion")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def out(program: str) -> str:
    result = subprocess.run([sys.executable, "-c", program], capture_output=True, text=True, check=True)
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

EXAMPLE = '''from collections import deque


def balanced(text):
    """Are the brackets matched and properly nested? A stack of the openers still waiting."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


for text in ("([]{})", "([)]", "((", "f(x[0]) + g({})"):
    print(repr(text), balanced(text))


class ArrayQueue:
    """A queue on a plain list, with the shifting that pop(0) hides written out."""

    def __init__(self):
        self.items = []
        self.moves = 0

    def push(self, item):
        self.items.append(item)

    def pop_front(self):
        first = self.items[0]
        for i in range(1, len(self.items)):
            self.items[i - 1] = self.items[i]
            self.moves += 1
        self.items.pop()
        return first


slow = ArrayQueue()
fast = deque()
for i in range(2000):
    slow.push(i)
    fast.append(i)
steps = 0
while fast:
    slow.pop_front()
    fast.popleft()
    steps += 1
print("2000 pops: the list moved", slow.moves, "elements; the deque took", steps, "steps")


def countdown(n, depth=0):
    print("  " * depth + "start", n)
    if n > 0:
        countdown(n - 1, depth + 1)
    print("  " * depth + "end", n)


countdown(2)


def flatten(nested):
    """Every number in a nest of lists, in order, by recursion."""
    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat


def flatten_with_a_stack(nested):
    """The same, with a stack you manage instead of the call stack."""
    flat = []
    stack = list(reversed(nested))
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        else:
            flat.append(item)
    return flat


data = [1, [2, [3, 4]], [], [[5]], 6]
print(flatten(data), flatten_with_a_stack(data))

deep = [0]
for i in range(1, 5000):
    deep = [i, deep]
print("5000 levels with a stack:", len(flatten_with_a_stack(deep)), "numbers")
try:
    flatten(deep)
    print("5000 levels by recursion: it worked")
except RecursionError:
    print("5000 levels by recursion: RecursionError")
'''
EXAMPLE_OUT = out(EXAMPLE)
print("example:\n" + EXAMPLE_OUT)
EX = EXAMPLE_OUT.splitlines()
assert EX[:4] == ["'([]{})' True", "'([)]' False", "'((' False", "'f(x[0]) + g({})' True"], EX[:4]
assert EX[4] == "2000 pops: the list moved 1999000 elements; the deque took 2000 steps", EX[4]
assert EX[5:11] == ["start 2", "  start 1", "    start 0", "    end 0", "  end 1", "end 2"], EX[5:11]
assert EX[11] == "[1, 2, 3, 4, 5, 6] [1, 2, 3, 4, 5, 6]", EX[11]
assert EX[12] == "5000 levels with a stack: 5000 numbers" and EX[13] == "5000 levels by recursion: RecursionError", EX[12:]
EXAMPLE_LINES = EXAMPLE.splitlines()


def ln(text: str, after: int = 0) -> int:
    return next(i + 1 for i, line in enumerate(EXAMPLE_LINES) if i + 1 > after and text in line)


# --- recall programs ----------------------------------------------------------------------------

PREDICT_STACK = '''stack = []
for ch in "abc":
    stack.append(ch)
print(stack.pop(), stack.pop())
stack.append("d")
print(stack)
'''
PREDICT_STACK_OUT = out(PREDICT_STACK)
assert PREDICT_STACK_OUT == "c b\n['a', 'd']\n", PREDICT_STACK_OUT

PREDICT_RECURSION = '''def countdown(n):
    print("start", n)
    if n > 0:
        countdown(n - 1)
    print("end", n)


countdown(2)
'''
PREDICT_RECURSION_OUT = out(PREDICT_RECURSION)
assert PREDICT_RECURSION_OUT == "start 2\nstart 1\nstart 0\nend 0\nend 1\nend 2\n", PREDICT_RECURSION_OUT

REVIEW_POSTFIX = '''stack = []
for token in "3 4 + 2 *".split():
    if token in {"+", "*"}:
        b = stack.pop()
        a = stack.pop()
        stack.append(a + b if token == "+" else a * b)
    else:
        stack.append(int(token))
    print(stack)
'''
REVIEW_POSTFIX_OUT = out(REVIEW_POSTFIX)
assert REVIEW_POSTFIX_OUT == "[3]\n[3, 4]\n[7]\n[7, 2]\n[14]\n", REVIEW_POSTFIX_OUT

PARSONS_LINES = [
    "from collections import deque",
    'tasks = deque(["a", "b", "c"])',
    'tasks.append("d")',
    "first = tasks.popleft()",
    "print(first, list(tasks))",
]
assert out("\n".join(PARSONS_LINES) + "\n") == "a ['b', 'c', 'd']\n"

# --- the fill-in --------------------------------------------------------------------------------

FILL_SOLUTION = '''def balanced(text):
    """Are the brackets matched and properly nested?"""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


for text in ("([]{})", "([)]", "((", "f(x[0]) + g({})"):
    print(repr(text), balanced(text))
'''
FILL_STARTER = FILL_SOLUTION.replace("stack.append(ch)", "stack.append(...)").replace("stack.pop() != pairs[ch]", "stack.pop() != pairs[...]")
FILL_WRONG = FILL_SOLUTION.replace("    return not stack", "    return True")
FILL_OUT = out(FILL_SOLUTION)
assert FILL_OUT == "'([]{})' True\n'([)]' False\n'((' False\n'f(x[0]) + g({})' True\n", FILL_OUT
assert out(FILL_WRONG) != FILL_OUT

# --- the write ----------------------------------------------------------------------------------

WRITE_SOLUTION = '''def flatten(nested):
    """Every non-list value in a nest of lists, in order."""
    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat


print(flatten([1, [2, [3, 4]], [], [[5]], 6]))
print(flatten([]))
print(flatten([[[]], "a"]))
'''
WRITE_OUT = out(WRITE_SOLUTION)
assert WRITE_OUT == "[1, 2, 3, 4, 5, 6]\n[]\n['a']\n", WRITE_OUT
WRITE_WRONG = WRITE_SOLUTION.replace("flat.extend(flatten(item))", "flat.append(flatten(item))")
assert out(WRITE_WRONG) != WRITE_OUT

# --- the build ----------------------------------------------------------------------------------

BUILD_SOLUTION = '''def evaluate_postfix(expression):
    """Evaluate tokens in postfix order: operands push, an operator pops two and pushes the result."""
    stack = []
    for token in expression.split():
        if token in {"+", "-", "*"}:
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b if token == "+" else a - b if token == "-" else a * b)
        else:
            stack.append(int(token))
    return stack.pop()


def balanced(text):
    """Are the brackets matched and properly nested?"""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


def max_depth(nested):
    """How deeply lists nest: a non-list is 0, an empty list 1, a list is 1 more than its deepest item."""
    if not isinstance(nested, list):
        return 0
    return 1 + max((max_depth(item) for item in nested), default=0)


def flatten_iterative(nested):
    """Every non-list value, in order, with an explicit stack so that any depth works."""
    flat = []
    stack = list(reversed(nested))
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        else:
            flat.append(item)
    return flat


print(evaluate_postfix("3 4 + 2 *"), evaluate_postfix("5 1 2 + 4 * + 3 -"))
print(balanced("([]{})"), balanced("([)]"), balanced(""))
print(max_depth(7), max_depth([]), max_depth([1, [2, [3]]]))
print(flatten_iterative([1, [2, [3, 4]], [], [[5]], 6]))
'''
BUILD_OUT = out(BUILD_SOLUTION)
print("build:\n" + BUILD_OUT)
assert BUILD_OUT == "14 14\nTrue False True\n0 1 3\n[1, 2, 3, 4, 5, 6]\n", BUILD_OUT
BUILD_RECURSIVE_FLATTEN = BUILD_SOLUTION.replace(
    '''    flat = []
    stack = list(reversed(nested))
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        else:
            flat.append(item)
    return flat''',
    '''    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(flatten_iterative(item))
        else:
            flat.append(item)
    return flat''',
)
BUILD_POSTFIX_BACKWARDS = BUILD_SOLUTION.replace("a + b if token == \"+\" else a - b if token == \"-\" else a * b", "a + b if token == \"+\" else b - a if token == \"-\" else a * b")
BUILD_IGNORES_KIND = BUILD_SOLUTION.replace("if not stack or stack.pop() != pairs[ch]:", "if not stack or not stack.pop():")
BUILD_DEPTH_OFF = BUILD_SOLUTION.replace("return 1 + max((max_depth(item) for item in nested), default=0)", "return max((1 + max_depth(item) for item in nested), default=0)")
assert out(BUILD_RECURSIVE_FLATTEN) == BUILD_OUT
for wrong in (BUILD_POSTFIX_BACKWARDS, BUILD_IGNORES_KIND, BUILD_DEPTH_OFF):
    assert wrong != BUILD_SOLUTION and out(wrong) != BUILD_OUT

# --- the debug ----------------------------------------------------------------------------------

DEBUG_SOLUTION = '''from collections import deque


def count_jobs(job):
    """How many single jobs a job holds: a name is one, a list is the sum of its parts."""
    if isinstance(job, list):
        return sum(count_jobs(part) for part in job)
    return 1


def run_all(jobs):
    """Run jobs in arrival order; a job that is a list of parts puts its parts at the back of the queue."""
    queue = deque(jobs)
    done = []
    while queue:
        job = queue.popleft()
        if isinstance(job, list):
            queue.extend(job)
        else:
            done.append(job)
    return done


jobs = ["a", ["b", "c"], "d", [["e"], "f"]]
print(count_jobs(jobs))
print(" ".join(run_all(jobs)))
'''
BUG_POP = ("        job = queue.popleft()", "        job = queue.pop()")
BUG_COUNT = ("        return sum(count_jobs(part) for part in job)", "        return 1 + sum(count_jobs(part) for part in job)")
DEBUG_STARTER = DEBUG_SOLUTION.replace(*BUG_POP).replace(*BUG_COUNT)
DEBUG_STILL_POP = DEBUG_SOLUTION.replace(*BUG_POP)
DEBUG_STILL_COUNT = DEBUG_SOLUTION.replace(*BUG_COUNT)
DEBUG_OUT = out(DEBUG_SOLUTION)
DEBUG_STARTER_OUT = out(DEBUG_STARTER)
print("debug:\n" + DEBUG_OUT + "buggy:\n" + DEBUG_STARTER_OUT)
assert DEBUG_OUT == "6\na d b c f e\n", DEBUG_OUT
assert DEBUG_STARTER_OUT == "10\nf e d c b a\n", DEBUG_STARTER_OUT
assert out(DEBUG_STILL_POP) != DEBUG_OUT and out(DEBUG_STILL_COUNT) != DEBUG_OUT

REVIEW_CODE_SOLUTION = '''def max_depth(nested):
    """How deeply lists nest: a non-list is 0, an empty list 1, a list is 1 more than its deepest item."""
    if not isinstance(nested, list):
        return 0
    return 1 + max((max_depth(item) for item in nested), default=0)


print(max_depth(3), max_depth([]), max_depth([1, [2, [3]], []]))
'''
REVIEW_CODE_OUT = out(REVIEW_CODE_SOLUTION)
assert REVIEW_CODE_OUT == "0 1 3\n", REVIEW_CODE_OUT

# =====================================================================================
# topic.yaml
# =====================================================================================

write(
    "topic.yaml",
    '''id: ml.dsa.stacks-queues-recursion
kind: topic
status: ready
title: "Stacks, queues and recursion"
summary: "Last-in-first-out and first-in-first-out as structures: a stack on a list, a queue on a deque, why popping from the front of a list is slow, and recursion as a stack the interpreter keeps for you."
prerequisites: [ml.dsa.arrays-and-hashing]
estimated_minutes: 50
rev: 1
objectives:
  - "Use a list as a stack and a deque as a queue, and say why list.pop(0) is the wrong queue."
  - "Match brackets, evaluate postfix arithmetic and undo actions with a stack."
  - "Write a recursive function, trace its call stack, and turn it into a loop with an explicit stack."
  - "Say what a linked list is, why Python rarely needs one, and where the idea still appears."
# Linked, never copied or embedded: the Runestone book is CC BY-NC-SA 4.0;
# the Python documentation is under the PSF licence.
resources:
  - title: "Problem Solving with Algorithms and Data Structures using Python (Brad Miller and David Ranum), chapter 4: Basic Data Structures, the sections on stacks (4.3 to 4.5, with balanced parentheses), queues (4.10 to 4.12) and linked lists (4.20 and 4.21)"
    url: https://runestone.academy/ns/books/published/pythonds3/BasicDS/toctree.html
    type: reading
    use: link
    license: CC BY-NC-SA 4.0
  - title: "Problem Solving with Algorithms and Data Structures using Python, chapter 5: Recursion, sections 5.2 to 5.6 (the sum of a list, the three laws of recursion, stack frames)"
    url: https://runestone.academy/ns/books/published/pythonds3/Recursion/toctree.html
    type: reading
    use: link
    license: CC BY-NC-SA 4.0
  - title: "The Python documentation: collections.deque, a list-like container with fast appends and pops on either end"
    url: https://docs.python.org/3/library/collections.html#collections.deque
    type: reading
    use: link
    license: "PSF licence (linked, not copied)"
practice:
  - example-brackets-a-queue-and-a-nest
  - parsons-a-queue-of-tasks
  - predict-a-stack-trace
  - mcq-which-queue
  - mcq-undo
  - predict-recursion-order
  - mcq-no-base-case
  - mcq-when-a-linked-list
  - fill-balanced-brackets
  - write-flatten
prove:
  build: build-stacks-and-nests
  debug: debug-a-job-queue
  explain:
    prompt: |
      A teammate has written a crawler that keeps its to-do list of pages in a Python list and takes the next one with `pop(0)`, and a function that walks a nested configuration by calling itself, which crashes with `RecursionError` on one customer's file. In your own words: what a stack and a queue are, which Python structure to use for each and why `pop(0)` on a list is the wrong queue; what happens in memory when a function calls itself, what the base case is for, and why there is a depth limit; and how you would rewrite the recursive walk as a loop with a stack of your own, and what that changes.
    rubric:
      - id: stack-queue
        required: true
        description: "A stack is last in, first out (a list with append and pop()); a queue is first in, first out (collections.deque with append and popleft()). A list's pop(0) shifts every remaining element, so a queue on a list costs a step per element per pop."
      - id: recursion
        required: true
        description: "Each call gets its own frame (its locals and where to return to) pushed on the call stack and popped when it returns; the base case is the call that doesn't recurse, so the stack stops growing; Python caps the depth at about 1,000 frames and raises RecursionError beyond it."
      - id: explicit-stack
        required: true
        description: "Push the starting work on a list; loop: pop an item, handle it, push its sub-work (reversed, to keep order); the stack you manage replaces the interpreter's and has no depth limit beyond memory, at the cost of writing the bookkeeping yourself."
      - id: stack-uses
        required: false
        description: "Stacks fit anything nested or reversible: matching brackets, undo, evaluating postfix, walking a nest; queues fit anything in arrival order: tasks, breadth-first search."
    model_answer: |
      A stack is a pile where the last thing put on is the first thing taken off, and a queue is a line where the first thing in is the first thing out. In Python a stack is just a list used with append and pop(), both of which work at the end of the list and take one step. A queue wants collections.deque, with append at the back and popleft at the front, again one step each. A list with pop(0) looks like a queue but isn't a good one: a list is an array, so removing the first element leaves a gap and every remaining element shifts down one place, which is a step per element per pop; the crawler's to-do list of a hundred thousand pages would move a hundred thousand elements for each page it takes. When a function calls itself, nothing magical happens: each call gets its own frame, a record of its local variables and of where to return to, and the frames are pushed on the call stack as calls begin and popped as they return, so the innermost call finishes first. The base case is the call that doesn't call again; without it the stack grows until Python's limit, about a thousand frames, and raises RecursionError, which is what the deep configuration file hit. To rewrite the walk as a loop, I would keep my own stack, a list: push the root, then loop while the stack isn't empty, popping an item, handling it, and pushing its children (in reverse, so they come off in the original order). That replaces the interpreter's stack with one in ordinary memory, so depth is limited only by memory, and it makes the bookkeeping explicit, which is a little more code and a little less elegance for a walk that can't crash on a deep file.
review_pool:
  - review-predict-postfix
  - review-mcq-call-stack
  - review-mcq-stack-or-queue
  - review-mcq-walk-the-chain
  - review-max-depth
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: stack-queue
    description: "Use a list as a stack and a deque as a queue, and say why list.pop(0) is the wrong queue"
  - id: stack-uses
    description: "Match brackets, evaluate postfix and undo with a stack"
  - id: recursion
    description: "Write a recursive function, trace its call stack, and turn it into a loop with an explicit stack"
  - id: linked
    description: "Say what a linked list is, why Python rarely needs one, and where the idea appears"
''',
)

# =====================================================================================
# lesson.mdx
# =====================================================================================

write(
    "lesson.mdx",
    f'''<Intro>

Two shapes of "what's next": a **stack**, where the last thing in is the first thing out, and a **queue**, where the first thing in is the first thing out. Python gives you the first for free (a list) and the second almost for free (`collections.deque`), and the difference between them is the difference between matching brackets and running tasks in order. The third idea is **recursion**, a function that calls itself, which is a stack the interpreter keeps for you; the worked example shows that stack growing and shrinking, and then replaces it with one you manage.

The main resource is **_Problem Solving with Algorithms and Data Structures using Python_, chapter 4** (stacks, balanced parentheses, queues, and the two sections on linked lists) and **chapter 5** (recursion, up to stack frames); about 40 minutes, with runnable code. The `deque` documentation is the reference. Watch for:

- **Push and pop** are both at the end of a list; a queue needs the front too.
- **The three laws of recursion**: a base case, a step towards it, and a call to itself.
- **A stack frame** is what each call owns.

</Intro>

<Resource index={{0}} />

<Recap>

- **A stack** is last in, first out: a list with `append` to push and `pop()` to pop, both one step. Anything nested or reversible is a stack problem: matching brackets (push each opener, pop on each closer and check it pairs), **undo** (push each action, pop to undo), evaluating **postfix** arithmetic (`3 4 + 2 *`: push numbers, an operator pops two and pushes the result), and walking a nest.
- **A queue** is first in, first out: `collections.deque` with `append` at the back and `popleft()` at the front, both one step. A list with `pop(0)` looks like a queue but shifts every remaining element each time: the worked example's 2,000 pops moved 1,999,000 elements on a list and took 2,000 steps on a deque. Anything in arrival order is a queue problem: tasks, messages, and breadth-first search in the graphs topic.
- **Recursion** is a function that calls itself on a smaller input, with a **base case** that doesn't. Each call gets its own **frame** (its local variables and where to return to) on the **call stack**, pushed when the call starts and popped when it returns, so the innermost call finishes first: the example's `countdown(2)` prints start 2, start 1, start 0, then end 0, end 1, end 2. Python caps the stack at about 1,000 frames and raises `RecursionError` beyond it (both the browser and CI do), so recursion suits nested data a few hundred levels deep, not a list of a million items.
- **Recursion to a loop with an explicit stack:** push the starting work; while the stack isn't empty, pop an item, handle it, and push its sub-work (reversed, so it comes off in order). The stack you manage replaces the one the interpreter managed and has no depth limit beyond memory: the example flattens 5,000 nested levels that way, where the recursive version raises `RecursionError`.
- **A linked list** is a chain of **nodes**, each holding a value and a reference to the next. Inserting or removing at a node you already hold is one step, with no shifting; but reaching the k-th node takes k steps, and every node is a separate object. Python rarely needs one: a list wins for almost everything, and `deque` is built from linked blocks so it gets fast ends without the per-node cost. The idea comes back in trees and graphs, where every node holds references to its neighbours.
- **In machine learning:** backpropagation through a deep computation graph is done with an explicit stack or a reverse topological order rather than recursion, for exactly the depth reason (Module 4's backprop walked the layers in a loop); a pipeline's work queue is a deque; and tokenizers and parsers keep a stack for nesting.

</Recap>
''',
)

# =====================================================================================
# recall
# =====================================================================================

write(
    "recall/parsons-a-queue-of-tasks.yaml",
    "id: parsons-a-queue-of-tasks\ntype: parsons\nrev: 1\nprompt: |\n"
    + block("Put the lines in order to queue a fourth task behind three, take the first one, and print `a ['b', 'c', 'd']`. One line is a decoy that doesn't belong.")
    + "lines:\n"
    + "".join(f"  - {quoted(line)}\n" for line in PARSONS_LINES)
    + "distractors:\n  - "
    + quoted("first = tasks.pop()")
    + "\nexplanation: |\n"
    + block("A queue takes from the front: `popleft()` returns `\"a\"`, the first in. The decoy's `pop()` takes from the back, `\"d\"`, which is a stack's behaviour. `append` puts the new task at the back either way, and `deque` makes both ends one step.")
    + "skills: [stack-queue]\n",
)

write(
    "recall/predict-a-stack-trace.yaml",
    f'''id: predict-a-stack-trace
type: predict_output
rev: 1
prompt: |
  Three pushes, two pops, one more push. What does the program print?
code: |
{block(PREDICT_STACK)}expected_output: |
{block(PREDICT_STACK_OUT)}explanation: |
  `pop()` takes the last item pushed: `c`, then `b`. What remains is `['a']`, and the new push goes on the end, giving `['a', 'd']`. Last in, first out, and the list's end is the top of the stack.
skills: [stack-queue]
''',
)

mcq(
    "mcq-which-queue",
    "A crawler keeps the pages still to visit in a Python list and takes the next one with `pages.pop(0)`. There are a hundred thousand pages. What is the right change?",
    [
        "Use `pages.pop()` instead, which is one step; the order pages are visited in doesn't matter",
        "Keep the list but reverse it once, then `pop()` from the end, which is one step and keeps the order",
        "Use `collections.deque` with `popleft()`: one step per pop, and first in, first out",
        "Use a dict from page to its position, and delete the lowest position each time",
    ],
    2,
    "A queue needs a cheap front, and a deque gives it: `popleft()` is one step. `pop(0)` on a list shifts every remaining page, a hundred thousand moves per pop. Reversing once and popping from the end works until the first new page is added, which belongs at the back and would then come out first. `pop()` without reversing changes the order to last in, first out.",
    ["stack-queue"],
)

mcq(
    "mcq-undo",
    "An editor needs undo: each action is recorded, and undo reverses the most recent one not yet undone. Which structure fits, and why?",
    [
        "A queue, because actions should be undone in the order they were made",
        "A stack, because the most recent action is the first one to be undone",
        "A set, because each action should be undone at most once",
        "A dict from each action to the one before it, so undo can follow the chain back",
    ],
    1,
    "Undo takes back the latest action first, then the one before it: last in, first out, which is a stack with the end of a list as its top. A queue would undo the oldest action first. A set has no order, and the dict rebuilds a stack with extra work.",
    ["stack-uses"],
)

write(
    "recall/predict-recursion-order.yaml",
    f'''id: predict-recursion-order
type: predict_output
rev: 1
prompt: |
  A function that prints on the way in and on the way out of each call. What does the program print?
code: |
{block(PREDICT_RECURSION)}expected_output: |
{block(PREDICT_RECURSION_OUT)}explanation: |
  Each call prints `start`, then calls the next before it can print `end`, so the three `start` lines come first. The innermost call, `countdown(0)`, is the base case: it prints `end 0` and returns, and then the calls finish from the inside out. The frames are pushed 2, 1, 0 and popped 0, 1, 2.
skills: [recursion]
''',
)

mcq(
    "mcq-no-base-case",
    "`def total(items): return items[0] + total(items[1:])` works on `[1, 2, 3]`? What actually happens, and what is missing?",
    [
        "It returns 6; Python stops recursing on its own when the slice becomes empty, as a loop would",
        "It raises `IndexError`: there is no base case that returns without calling again",
        "It returns 6 but slowly, because each call copies the rest of the list",
        "It raises `RecursionError` immediately, because a function may not call itself without a decorator",
    ],
    1,
    "The calls go `[1, 2, 3]`, `[2, 3]`, `[3]`, `[]`, and on the empty list `items[0]` fails. A base case, `if not items: return 0`, is what stops the chain; without one a function that keeps calling itself runs until the stack's limit, about a thousand frames, and Python raises `RecursionError`. (The copying is real and makes this version quadratic, but it isn't what breaks it.)",
    ["recursion"],
)

mcq(
    "mcq-when-a-linked-list",
    "When would a linked list beat a Python list, and why does Python code rarely use one?",
    [
        "Never; a linked list is a teaching example with no practical use",
        "For random access by position, because each node is reached directly through its reference instead of by counting",
        "For inserting or removing at a node you already hold, with no shifting; rarely, because reaching a node takes a walk",
        "For sorting, because the links can be rewired faster than elements can be moved, which is why `sorted` uses one internally for large inputs",
    ],
    2,
    "A linked list's strength is local: given a node, splice in or out without touching the others. Its weaknesses are everything else: reaching the k-th node is k steps, each node costs an object, and the cache-friendly array wins for scans. `deque` gets fast ends from linked blocks; trees and graphs use the same node-and-reference idea.",
    ["linked"],
)

write(
    "recall/review-predict-postfix.yaml",
    f'''id: review-predict-postfix
type: predict_output
rev: 1
prompt: |
  Postfix arithmetic evaluated with a stack, printing the stack after each token of `3 4 + 2 *`. What does the program print?
code: |
{block(REVIEW_POSTFIX)}expected_output: |
{block(REVIEW_POSTFIX_OUT)}explanation: |
  Numbers push; an operator pops two numbers, the later-pushed one second, and pushes the result. `3 4 +` leaves 7, `2` pushes, and `*` turns `[7, 2]` into `[14]`. Postfix needs no parentheses because the stack remembers what is waiting.
skills: [stack-uses]
''',
)

mcq(
    "review-mcq-call-stack",
    "While `countdown(2)` is running `countdown(0)`, what is on the call stack, and what happens when `countdown(0)` returns?",
    [
        "Only `countdown(0)`; the earlier calls were replaced when they called the next one, to save memory",
        "Three frames, for 2, 1 and 0, each with its own `n`; the top is popped and `countdown(1)` resumes",
        "One frame shared by all three calls, with `n` overwritten each time",
        "Three frames, and all three return at once when the innermost one does",
    ],
    1,
    "Every active call has its own frame holding its own locals and its return point, pushed as the call starts. The innermost call returns first, its frame is popped, and the call below resumes from where it paused. Nothing is shared and nothing is replaced, which is why `end 1` prints after `end 0`.",
    ["recursion"],
)

mcq(
    "review-mcq-stack-or-queue",
    "Exploring a maze: one program always continues from the most recently discovered junction, another from the earliest discovered one not yet explored. Which structure does each use?",
    [
        "Both use a list; the difference is only in how the junctions are compared",
        "The first uses a queue (most recent first), the second a stack (earliest first)",
        "The first uses a stack (most recent first), the second a queue (earliest first)",
        "The first uses a set, the second a dict, because junctions must not be revisited",
    ],
    2,
    "Most recent first is last in, first out, a stack: that is depth-first search, which dives down one passage. Earliest first is first in, first out, a queue: breadth-first search, which spreads out evenly. The graphs topic uses both; a set of visited junctions is kept alongside either.",
    ["stack-queue"],
)

mcq(
    "review-mcq-walk-the-chain",
    "A linked list holds a million nodes. What does it cost to reach the 500,000th node, and why does a Python list do better?",
    [
        "About 500,000 steps, following each reference to the next; a list is an array, so an index is one step",
        "One step, because each node stores its position and the list keeps a table of them",
        "About 20 steps, because the chain can be halved like a binary search",
        "A million steps, because the chain must be walked to the end and back to check its length before any node is reached",
    ],
    0,
    "A linked list only knows where the next node is, so reaching the middle means following half a million references. An array holds its items in one block, so an index is an address calculation, one step. That walk, and the cost of a separate object per node, is why Python code rarely builds a linked list, and why `deque` links blocks rather than single items.",
    ["linked"],
)

# =====================================================================================
# exercises
# =====================================================================================

write(
    "exercises/example-brackets-a-queue-and-a-nest/exercise.yaml",
    f'''id: example-brackets-a-queue-and-a-nest
stage: worked_example
rev: 1
title: "Brackets, a queue and a nest"
prompt: |
  A stack that checks brackets, a queue on a list against a deque, a recursive countdown that shows its frames, and a nest flattened by recursion and by a stack you manage. Press **Run**, then read how each part works.
steps:
  - label: "Matching brackets with a stack"
    lines: "{ln('def balanced')}-{ln('    print(repr(text)')}"
    note: "Each opener is pushed; each closer pops the latest opener and checks it is the matching kind. A closer with nothing to pop, a mismatched pair, or openers left over at the end all mean unbalanced. Last in, first out is exactly what nesting needs: the most recent opener is the one a closer must match."
  - label: "A queue on a list, with the shifting written out"
    lines: "{ln('class ArrayQueue')}-{ln('        return first')}"
    note: "`pop(0)` on a list has to do this: take the first element, then move every other element one place towards the front. The class counts the moves. A real list does the moving in fast compiled code, but it still does all of it."
  - label: "Two thousand pops"
    lines: "{ln('slow = ArrayQueue')}-{ln('2000 pops:')}"
    note: "Two thousand tasks queued, then taken in order. The list moved 1,999,000 elements, about `n² / 2`; the deque's `popleft()` took one step each, 2,000 in all. A deque keeps its items in linked blocks so that both ends are cheap."
  - label: "A recursive countdown, with its frames"
    lines: "{ln('def countdown')}-{ln('countdown(2)')}"
    note: "Each call prints on the way in, calls the next, and prints on the way out; the indentation is the depth of the call stack. The three `start` lines are three frames pushed; `end 0` is the base case returning; the `end` lines are the frames popped, innermost first."
  - label: "Flattening a nest by recursion"
    lines: "{ln('def flatten(nested)')}-{ln('    return flat')}"
    note: "A list inside the list is flattened by the same function, a call for each level of nesting. The three laws: a base case (an item that isn't a list is appended), a step towards it (each call handles one level), and a call to itself."
  - label: "The same, with a stack you manage"
    lines: "{ln('def flatten_with_a_stack')}-{ln('print(flatten(data)')}"
    note: "The work still to do lives in an explicit stack: push the items in reverse (so the first comes off first), pop one, and either keep it or push its contents. Same answer as the recursive version, with the interpreter's call stack replaced by a list."
  - label: "Five thousand levels deep"
    lines: "{ln('deep = [0]')}-{ln('by recursion: RecursionError')}"
    note: "A nest 5,000 levels deep. The explicit stack flattens it; the recursive version needs 5,000 frames at once and Python stops it at about a thousand with `RecursionError`, in the browser and in CI alike. Recursion is the clearer code; the loop is the one that can't be crashed by depth."
''',
)
write("exercises/example-brackets-a-queue-and-a-nest/solution.py", EXAMPLE)
write(
    "exercises/example-brackets-a-queue-and-a-nest/test_exercise.py",
    f'''from checks import run


def test_the_walkthrough():
    """Prints the bracket checks, the queue counts, the countdown's frames, the flattened nest and the deep nest's two outcomes."""
    assert run() == {EXAMPLE_OUT!r}
''',
)

write(
    "exercises/fill-balanced-brackets/exercise.yaml",
    f'''id: fill-balanced-brackets
stage: fill_in
rev: 1
title: "Balanced brackets"
prompt: |
  `balanced(text)` should say whether the brackets in a text are matched and properly nested, using a stack of the openers still waiting. Replace each `...` so that each opener is pushed and each closer is checked against the opener it should match, and the program prints:

  ```
{block(FILL_OUT)}  ```

  The program fails until every `...` is replaced.
hints:
  - "The thing to push is the opener itself, `ch`, so that it can be compared later."
  - "`pairs[ch]` is the opener that the closer `ch` requires; the popped opener must equal it."
skills: [stack-uses]
''',
)
write("exercises/fill-balanced-brackets/starter.py", FILL_STARTER)
write("exercises/fill-balanced-brackets/solution.py", FILL_SOLUTION)
write(
    "exercises/fill-balanced-brackets/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the four verdicts."""
    printed = run()
    assert printed == {FILL_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_more_texts():
    """An empty text is balanced; a lone closer, a lone opener and a crossed pair are not; letters are ignored."""
    balanced = function("balanced")
    assert balanced("") and balanced("a(b)c") and balanced("{{[()]}}")
    assert not balanced(")") and not balanced("(") and not balanced("{{(}})")
''',
)
write("exercises/fill-balanced-brackets/wrong/ignores-leftovers.py", FILL_WRONG)
write(
    "exercises/fill-balanced-brackets/wrong/typed-in.py",
    "def balanced(text):\n    return True\n\n\n" + "".join(f"print({line!r})\n" for line in FILL_OUT.splitlines()),
)

write(
    "exercises/write-flatten/exercise.yaml",
    f'''id: write-flatten
stage: write
rev: 1
title: "Flatten a nest"
prompt: |
  Write `flatten(nested)`, which returns every value that isn't a list from a nest of lists, in order, by recursion: for each item, if it is a list, add everything `flatten` gives for it; otherwise add the item. Then print it for these three calls:

  ```python
  print(flatten([1, [2, [3, 4]], [], [[5]], 6]))
  print(flatten([]))
  print(flatten([[[]], "a"]))
  ```

  ```
{block(WRITE_OUT)}  ```
hints:
  - "`isinstance(item, list)` tells a list from a value."
  - "`flat.extend(flatten(item))` adds the flattened contents; `append` would nest them again."
skills: [recursion]
''',
)
write("exercises/write-flatten/starter.py", "")
write("exercises/write-flatten/solution.py", WRITE_SOLUTION)
write(
    "exercises/write-flatten/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints the three flattened lists."""
    printed = run()
    assert printed == {WRITE_OUT!r}, f"Your program printed:\\n{{printed}}"


def test_a_hundred_levels():
    """A nest 100 levels deep flattens to the 100 numbers in order."""
    flatten = function("flatten")
    nested = [99]
    for i in range(98, -1, -1):
        nested = [i, nested]
    assert flatten(nested) == list(range(100))
''',
)
write("exercises/write-flatten/wrong/appends-the-list.py", WRITE_WRONG)
write(
    "exercises/write-flatten/wrong/typed-in.py",
    "def flatten(nested):\n    return [1, 2, 3, 4, 5, 6]\n\n\n" + "".join(f"print({line!r})\n" for line in WRITE_OUT.splitlines()),
)

# --- the proof -----------------------------------------------------------------------------------

write(
    "exercises/build-stacks-and-nests/exercise.yaml",
    f'''id: build-stacks-and-nests
stage: build
rev: 1
title: "Stacks and nests"
prompt: |
  Starting from a blank editor, write four functions:

  - `evaluate_postfix(expression)`: the value of a postfix expression whose tokens (split on spaces) are integers and `+`, `-`, `*`, evaluated with a stack: a number is pushed; an operator pops two numbers (the second popped is the left operand) and pushes the result. Return an int.
  - `balanced(text)`: whether the brackets `()[]{{}}` in the text are matched and properly nested; other characters are ignored.
  - `max_depth(nested)`: how deeply lists nest: a value that isn't a list is 0, an empty list 1, and a list is 1 more than its deepest item. Recursion is the natural way.
  - `flatten_iterative(nested)`: every non-list value in order, using a stack you manage and **no recursion**, so that a nest 5,000 levels deep works.

  Then print:

  ```python
  print(evaluate_postfix("3 4 + 2 *"), evaluate_postfix("5 1 2 + 4 * + 3 -"))
  print(balanced("([]{{}})"), balanced("([)]"), balanced(""))
  print(max_depth(7), max_depth([]), max_depth([1, [2, [3]]]))
  print(flatten_iterative([1, [2, [3, 4]], [], [[5]], 6]))
  ```

  ```
{block(BUILD_OUT)}  ```

  The checks include a nest 5,000 levels deep, which a recursive `flatten_iterative` cannot survive.
skills: [stack-uses, recursion]
''',
)
write("exercises/build-stacks-and-nests/starter.py", "")
write("exercises/build-stacks-and-nests/solution.py", BUILD_SOLUTION)
write(
    "exercises/build-stacks-and-nests/test_exercise.py",
    f'''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the four lines."""
    assert run() == {BUILD_OUT!r}


def test_postfix():
    """2 3 4 * + is 14, 10 2 - is 8, and a lone number is itself."""
    evaluate_postfix = function("evaluate_postfix")
    assert (evaluate_postfix("2 3 4 * +"), evaluate_postfix("10 2 -"), evaluate_postfix("7")) == (14, 8, 7)


def test_balanced():
    """Nested pairs of every kind pass; a crossed pair, a lone opener and a lone closer fail."""
    balanced = function("balanced")
    assert balanced("{{[()]}}") and balanced("a(b[c]{{d}})e")
    assert not balanced("{{[(])}}") and not balanced("(") and not balanced(")")


def test_max_depth():
    """Four empty lists nested are depth 4; [1, [2], [[3]]] is depth 3."""
    max_depth = function("max_depth")
    assert (max_depth([[[[]]]]), max_depth([1, [2], [[3]]])) == (4, 3)


def test_flatten_five_thousand_levels():
    """A nest 5,000 levels deep flattens to the 5,000 numbers in order, and a small nest keeps its order."""
    flatten_iterative = function("flatten_iterative")
    nested = [4999]
    for i in range(4998, -1, -1):
        nested = [i, nested]
    assert flatten_iterative(nested) == list(range(5000))
    assert flatten_iterative([[1, 2], [3, [4]], 5]) == [1, 2, 3, 4, 5]
''',
)
write("exercises/build-stacks-and-nests/wrong/recursive-flatten.py", BUILD_RECURSIVE_FLATTEN)
write("exercises/build-stacks-and-nests/wrong/postfix-backwards.py", BUILD_POSTFIX_BACKWARDS)
write("exercises/build-stacks-and-nests/wrong/ignores-kind.py", BUILD_IGNORES_KIND)
write("exercises/build-stacks-and-nests/wrong/depth-off.py", BUILD_DEPTH_OFF)
write(
    "exercises/build-stacks-and-nests/wrong/typed-in.py",
    "def evaluate_postfix(expression):\n    return 14\n\n\ndef balanced(text):\n    return True\n\n\ndef max_depth(nested):\n    return 0\n\n\ndef flatten_iterative(nested):\n    return [1, 2, 3, 4, 5, 6]\n\n\n"
    + "".join(f"print({line!r})\n" for line in BUILD_OUT.splitlines()),
)

write(
    "exercises/debug-a-job-queue/exercise.yaml",
    f'''id: debug-a-job-queue
stage: debug
rev: 1
title: "A job queue"
prompt: |
  Jobs arrive in a queue; a job may be a list of parts, which go to the back of the queue when it is reached. `count_jobs` should count the single jobs, and `run_all` should run them in arrival order. The program should print:

  ```
{block(DEBUG_OUT)}  ```

  It has two bugs. Run it: the count is 10 for 6 jobs, because `count_jobs` adds one for every **list** as well as for every name; a list is not a job, only the sum of its parts. Fix that, and the order comes out backwards: `run_all` takes jobs from the **back** of the deque with `pop()`, which makes it a stack. A queue takes from the front.
skills: [stack-queue, recursion]
''',
)
write("exercises/debug-a-job-queue/starter.py", DEBUG_STARTER)
write("exercises/debug-a-job-queue/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-a-job-queue/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_OUT!r}


def test_the_output():
    """Prints 6 and the jobs in arrival order."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_other_jobs():
    """Nested parts are counted once each and run in queue order; an empty list holds no jobs."""
    count_jobs = function("count_jobs")
    run_all = function("run_all")
    assert count_jobs([[], ["q"]]) == 1 and count_jobs("x") == 1
    assert run_all(["x", ["y", ["z"]], "w"]) == ["x", "w", "y", "z"]
''',
)
write("exercises/debug-a-job-queue/wrong/still-pops-the-back.py", DEBUG_STILL_POP)
write("exercises/debug-a-job-queue/wrong/still-counts-lists.py", DEBUG_STILL_COUNT)
write(
    "exercises/debug-a-job-queue/wrong/typed-in.py",
    "def count_jobs(job):\n    return 6\n\n\ndef run_all(jobs):\n    return list('adbcfe')\n\n\n" + "".join(f"print({line!r})\n" for line in DEBUG_OUT.splitlines()),
)

write(
    "exercises/review-max-depth/exercise.yaml",
    f'''id: review-max-depth
stage: review_code
rev: 1
title: "Nesting depth, from memory"
prompt: |
  Write `max_depth(nested)` by recursion: a value that isn't a list is 0, an empty list is 1, and a list is 1 more than its deepest item. Print it for `3`, `[]` and `[1, [2, [3]], []]`:

  ```
{block(REVIEW_CODE_OUT)}  ```
skills: [recursion]
''',
)
write("exercises/review-max-depth/starter.py", "")
write("exercises/review-max-depth/solution.py", REVIEW_CODE_SOLUTION)
write(
    "exercises/review-max-depth/test_exercise.py",
    f'''from checks import function, run


def test_the_output():
    """Prints 0 1 3."""
    assert run() == {REVIEW_CODE_OUT!r}


def test_other_nests():
    """Four empty lists nested are depth 4; a flat list is depth 1."""
    max_depth = function("max_depth")
    assert (max_depth([[[[]]]]), max_depth([1, 2, 3])) == (4, 1)
''',
)
write(
    "exercises/review-max-depth/wrong/empty-is-zero.py",
    REVIEW_CODE_SOLUTION.replace("return 1 + max((max_depth(item) for item in nested), default=0)", "return max((1 + max_depth(item) for item in nested), default=0)"),
)
write(
    "exercises/review-max-depth/wrong/typed-in.py",
    "def max_depth(nested):\n    return 0\n\n\n" + "".join(f"print({line!r})\n" for line in REVIEW_CODE_OUT.splitlines()),
)

print("ml.dsa.stacks-queues-recursion written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
