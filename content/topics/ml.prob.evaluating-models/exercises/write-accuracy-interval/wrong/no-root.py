import numpy as np

rng = np.random.default_rng(5)
correct = (rng.random(200) < 0.84).astype(int)


def accuracy_interval(correct, z=1.96):
    p = correct.mean()
    se = p * (1 - p) / len(correct)
    return round(float(p), 3), round(float(p - z * se), 3), round(float(p + z * se), 3)


print(accuracy_interval(correct))
print(accuracy_interval(np.tile(correct, 4)))
print(accuracy_interval(np.ones(50, dtype=int)))
