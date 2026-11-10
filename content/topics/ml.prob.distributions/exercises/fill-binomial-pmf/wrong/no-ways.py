import math


def binomial_pmf(k, n, p):
    """The chance of exactly k yeses in n tries, each a yes with chance p."""
    return p**k * (1 - p) ** (n - k)


for k in range(11):
    print(k, round(binomial_pmf(k, 10, 0.3), 3), "#" * round(binomial_pmf(k, 10, 0.3) * 50))
print(round(sum(binomial_pmf(k, 10, 0.3) for k in range(11)), 6))
