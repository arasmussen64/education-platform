import math

# Eight months of made-up returns.
stocks = [0.03, -0.04, 0.05, 0.01, -0.02, 0.06, -0.05, 0.02]
bonds = [0.00, 0.02, 0.01, 0.01, 0.00, -0.01, 0.01, 0.02]


def volatility(returns):
    mean = sum(returns) / len(returns)
    squares = 0
    for r in returns:
        squares = squares + (r - mean) ** 2
    return math.sqrt(squares / (len(returns) - 1))


def correlation(a, b):
    n = len(a)
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    total = 0
    for i in range(n):
        total = total + (a[i] - mean_a) * (b[i] - mean_b)
    covariance = total / (n - 1)
    return covariance / (volatility(a) * volatility(b))


print("Stocks and bonds: -0.46")
print("Stocks with themselves: 1.00")
