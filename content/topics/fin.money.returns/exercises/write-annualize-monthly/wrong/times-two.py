# A fund's first six monthly returns (made up).
monthly = [0.02, -0.01, 0.03, 0.01, -0.02, 0.015]


def chained(returns):
    growth = 1.0
    for r in returns:
        growth = growth * (1 + r)
    return growth - 1


def annualize_monthly(monthly):
    return chained(monthly) * 2


print(f"Six months: {chained(monthly):.2%}")
print(f"Annualized: {annualize_monthly(monthly):.2%}")
