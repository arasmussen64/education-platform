# A fund's year-end prices (made up).
prices = [80.0, 92.0, 69.0, 86.25, 94.0]
invested = 10000

returns = []
for i in range(1, len(prices)):
    returns.append(prices[i] / prices[i - 1] - 1)

growth = 1.0
for r in returns:
    growth = growth * (1 + r)
growth_per_year = sum(returns) / len(returns)

for i in range(len(returns)):
    print(f"Year {i + 1}: {returns[i]:.2%}")
print(f"Growth per year: {growth_per_year:.2%}")
at_that_rate = invested * (1 + growth_per_year) ** len(returns)
print(f"${invested:,} at that rate for {len(returns)} years: ${at_that_rate:,.2f}")
print(f"${invested:,} in the fund itself: ${invested * prices[-1] / prices[0]:,.2f}")
