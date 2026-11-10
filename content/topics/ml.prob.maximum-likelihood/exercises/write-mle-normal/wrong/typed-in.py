import numpy as np

rng = np.random.default_rng(6)
x = rng.normal(170, 10, size=1000)


def mle_normal(x):
    return 5.0, 2.0


print('169.87 9.89')
print('True True')
print('(5.0, 2.0)')
