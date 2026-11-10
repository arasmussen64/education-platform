import numpy as np


def summary(values, probs):
    mean = (values * probs).sum()
    variance = ((values - mean) ** 2 * probs).sum()
    sd = np.sqrt(variance)
    return float(mean), float(variance), float(sd)


die = np.arange(1, 7)
mean, variance, sd = summary(die, np.full(6, 1 / 6))
print("die", mean, round(variance, 4), round(sd, 3))
prize = np.array([0.0, 10.0, 100.0])
mean, variance, sd = summary(prize, np.array([0.89, 0.1, 0.01]))
print("prize", mean, round(variance, 2), round(sd, 3))
