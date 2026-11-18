import math

# Six months of made-up returns for two funds, as decimals (0.04 is 4%).
fund_a = [0.04, -0.02, 0.03, -0.01, 0.05, -0.03]
fund_b = [0.02, 0.01, -0.01, 0.03, 0.01, -0.02]


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


corr = correlation(fund_a, fund_b)
vol_a = volatility(fund_a)
vol_b = volatility(fund_b)
print(f"Correlation: {corr:.2f}")
print(f"Fund A: {vol_a:.2%}, fund B: {vol_b:.2%}")

w = 0.5
variance = w**2 * vol_a**2 + (1 - w) ** 2 * vol_b**2 + 2 * w * (1 - w) * corr * vol_a * vol_b
print(f"Half and half, by the formula: {math.sqrt(variance):.2%}")

mix = []
for i in range(len(fund_a)):
    mix.append(w * fund_a[i] + (1 - w) * fund_b[i])
print(f"Half and half, month by month: {volatility(mix):.2%}")
