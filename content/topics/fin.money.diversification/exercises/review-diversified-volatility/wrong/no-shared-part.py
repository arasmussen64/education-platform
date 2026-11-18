import math

vol = 0.25
corr = 0.16


def diversified_volatility(vol, corr, n):
    return vol / math.sqrt(n)


for n in [1, 2, 5, 10, 100, 1000]:
    print(f"n = {n}: {diversified_volatility(vol, corr, n):.2%}")
