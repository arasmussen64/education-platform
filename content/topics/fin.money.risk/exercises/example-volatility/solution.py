import math
import statistics

returns = [0.03, -0.02, 0.05, -0.04, 0.01, 0.02]
mean = sum(returns) / len(returns)
total = 0.0
for r in returns:
    total = total + (r - mean) ** 2
monthly = math.sqrt(total / (len(returns) - 1))
print(f"Mean monthly return: {mean:.2%}")
print(f"Monthly volatility: {monthly:.2%}")
print(f"statistics.stdev agrees: {statistics.stdev(returns):.2%}")
print(f"Dividing by n instead: {statistics.pstdev(returns):.2%}")
print(f"Annual volatility: {monthly * math.sqrt(12):.2%}")
