def max_drawdown(prices):
    peak_index = 0
    worst = 0.0
    worst_peak = 0
    worst_trough = 0
    for i in range(len(prices)):
        if prices[i] > prices[peak_index]:
            peak_index = i
        fall = 1 - prices[i] / prices[peak_index]
        if fall > worst:
            worst = fall
            worst_peak = peak_index
            worst_trough = i
    return worst, worst_peak, worst_trough


prices = [50, 58, 64, 55, 48, 60, 70, 63, 52, 66]
fall, start, end = max_drawdown(prices)
print(f"Maximum drawdown: {fall:.2%}, from position {start} to position {end}")
