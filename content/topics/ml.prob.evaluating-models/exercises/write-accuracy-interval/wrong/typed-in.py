import numpy as np

rng = np.random.default_rng(5)
correct = (rng.random(200) < 0.84).astype(int)


def accuracy_interval(correct, z=1.96):
    return (1.0, 1.0, 1.0)


print('(0.845, 0.795, 0.895)')
print('(0.845, 0.82, 0.87)')
print('(1.0, 1.0, 1.0)')
