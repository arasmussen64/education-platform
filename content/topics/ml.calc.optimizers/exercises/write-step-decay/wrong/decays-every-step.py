import numpy as np


def step_decay(rate0, step, every, factor):
    return rate0 * factor ** (step / every)


print([step_decay(0.1, step, 2, 0.5) for step in range(6)])
print([step_decay(0.3, step, 10, 0.5) for step in (0, 10, 20, 50)])
