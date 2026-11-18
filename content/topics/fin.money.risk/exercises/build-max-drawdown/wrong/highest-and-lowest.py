def max_drawdown(prices):
    high = max(prices)
    low = min(prices)
    return 1 - low / high, prices.index(high), prices.index(low)


prices = [50, 58, 64, 55, 48, 60, 70, 63, 52, 66]
fall, start, end = max_drawdown(prices)
print(f"Maximum drawdown: {fall:.2%}, from position {start} to position {end}")
