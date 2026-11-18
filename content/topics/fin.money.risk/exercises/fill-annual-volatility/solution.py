import math


def volatility(returns):
    mean = sum(returns) / len(returns)
    total = 0.0
    for r in returns:
        total = total + (r - mean) ** 2
    return math.sqrt(total / (len(returns) - 1))


returns = [0.02, -0.03, 0.04, 0.01, -0.01, 0.03]
monthly = volatility(returns)
annual = monthly * math.sqrt(12)
print(f"Monthly volatility: {monthly:.2%}")
print(f"Annual volatility: {annual:.2%}")
