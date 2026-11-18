import math

# Six months of made-up returns for a stock fund and for gold.
stocks = [0.05, -0.03, 0.02, 0.04, -0.06, 0.03]
gold = [-0.01, 0.02, 0.01, -0.02, 0.04, 0.00]


def volatility(returns):
    mean = sum(returns) / len(returns)
    squares = 0
    for r in returns:
        squares = squares + (r - mean) ** 2
    return math.sqrt(squares / (len(returns) - 1))


def correlation(a, b):
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    total = 0
    for i in range(len(a)):
        total = total + (a[i] - mean_a) * (b[i] - mean_b)
    covariance = total / (len(a) - 1)
    return covariance / (volatility(a) * volatility(b))


print("Stocks and gold: -0.94")
