import math
import statistics

# A fund's month-end prices for a year, starting from the end of the year before (made up).
prices = [100, 104, 101, 108, 112, 105, 98, 94, 99, 87, 92, 101, 106]

returns = []
for i in range(1, len(prices)):
    returns.append(prices[i] / prices[i - 1] - 1)
monthly_vol = statistics.stdev(returns)
annual_vol = monthly_vol * 12

worst = 0.0
peak = prices[0]
for i in range(1, len(prices)):
    peak = max(prices[i - 1], prices[i])
    worst = max(worst, 1 - prices[i] / peak)

print(f"Monthly volatility: {monthly_vol:.2%}")
print(f"Annual volatility: {annual_vol:.2%}")
print(f"Maximum drawdown: {worst:.2%}")
