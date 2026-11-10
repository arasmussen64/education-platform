from collections import deque


def schedule(steps):
    """An order that runs every step after its dependencies; ValueError on a cycle."""
    remaining = {step: len(deps) for step, deps in steps.items()}
    dependents = {step: [] for step in steps}
    for step, deps in steps.items():
        for dep in deps:
            dependents[dep].append(step)
    ready = deque(step for step in steps if remaining[step] == 0)
    order = []
    while ready:
        step = ready.popleft()
        order.append(step)
        for dependent in dependents[step]:
            remaining[dependent] -= ...
            if remaining[dependent] == ...:
                ready.append(dependent)
    if len(order) < len(steps):
        raise ValueError("the steps depend on each other in a cycle")
    return order


print(schedule({"load": [], "clean": ["load"], "features": ["clean", "join"], "join": ["load"], "train": ["features"]}))
try:
    schedule({"a": ["b"], "b": ["a"]})
except ValueError as error:
    print(error)
