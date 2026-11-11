# Throwaway checks for the stacks topic's recall items and the 5,000-level recursion claim.
import sys
print("recursion limit:", sys.getrecursionlimit(), sys.version)
stack = []
for ch in "abc":
    stack.append(ch)
print("stack-trace:", stack.pop(), stack.pop())
stack.append("d")
print("stack-trace:", stack)

def countdown(n):
    print("start", n)
    if n > 0:
        countdown(n - 1)
    print("end", n)
countdown(2)

stack = []
for token in "3 4 + 2 *".split():
    if token in {"+", "*"}:
        b = stack.pop(); a = stack.pop()
        stack.append(a + b if token == "+" else a * b)
    else:
        stack.append(int(token))
    print("postfix:", stack)

from collections import deque
tasks = deque(["a", "b", "c"]); tasks.append("d"); first = tasks.popleft(); print("parsons given order:", first, list(tasks))
tasks = deque(["a", "b", "c"]); first = tasks.popleft(); tasks.append("d"); print("parsons swapped order:", first, list(tasks))
tasks = deque(["a", "b", "c"]); tasks.append("d"); first = tasks.pop(); print("parsons decoy:", first, list(tasks))

def total(items): return items[0] + total(items[1:])
try:
    total([1, 2, 3])
except Exception as e:
    print("no-base-case:", type(e).__name__, e)

def flatten(nested):
    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat
deep = [0]
for i in range(1, 5000):
    deep = [i, deep]
try:
    flatten(deep); print("5000 recursive: worked")
except RecursionError:
    print("5000 recursive: RecursionError")
# wrong/recursive-flatten against the build test's nest
nested = [4999]
for i in range(4998, -1, -1):
    nested = [i, nested]
try:
    flatten(nested); print("build-test nest recursive: worked")
except RecursionError:
    print("build-test nest recursive: RecursionError")
print("1999*2000/2 =", 1999*2000//2)
