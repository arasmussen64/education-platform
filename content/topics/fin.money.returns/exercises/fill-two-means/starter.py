returns = [0.30, -0.20, 0.10]
growth = 1.0
for r in returns:
    growth = growth ... (1 + r)
arithmetic = sum(returns) ... len(returns)
geometric = growth ** (1 ... len(returns)) - 1
print(f"Arithmetic mean: {arithmetic:.2%}")
print(f"Geometric mean: {geometric:.2%}")
