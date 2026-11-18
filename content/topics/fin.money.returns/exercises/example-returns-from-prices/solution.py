prices = [40.0, 44.0, 39.6, 43.56]
returns = []
for i in range(1, len(prices)):
    returns.append(prices[i] / prices[i - 1] - 1)
growth = 1.0
for r in returns:
    growth = growth * (1 + r)
for r in returns:
    print(f"{r:.2%}")
print(f"Chained: {growth - 1:.2%}")
print(f"Last over first: {prices[-1] / prices[0] - 1:.2%}")
print(f"Added up: {sum(returns):.2%}")
