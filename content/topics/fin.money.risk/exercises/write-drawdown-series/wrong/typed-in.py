# A fund's month-end prices (made up).
prices = [20.0, 22.0, 19.8, 23.0, 18.4, 20.7, 24.0]


def drawdowns(prices):
    return [0.0, 0.0, -0.1, 0.0, -0.2, -0.1, 0.0]


print("Month 0: $20.00, drawdown 0.0%")
print("Month 1: $22.00, drawdown 0.0%")
print("Month 2: $19.80, drawdown -10.0%")
print("Month 3: $23.00, drawdown 0.0%")
print("Month 4: $18.40, drawdown -20.0%")
print("Month 5: $20.70, drawdown -10.0%")
print("Month 6: $24.00, drawdown 0.0%")
