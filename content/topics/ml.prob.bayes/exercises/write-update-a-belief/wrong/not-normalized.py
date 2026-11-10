import numpy as np

biases = np.linspace(0, 1, 11)


def update(belief, likelihood):
    weighted = belief * likelihood
    return weighted


belief = np.full(11, 1 / 11)
for flip in [1, 0, 0, 0, 1, 0, 0, 0, 0, 0]:
    belief = update(belief, np.where(flip == 1, biases, 1 - biases))
print(np.round(belief, 3))
print(round(float(biases[belief.argmax()]), 1), round(float(belief.max()), 3))
