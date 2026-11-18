# A fund's month-end prices (made up).
prices = [20.0, 22.0, 19.8, 23.0, 18.4, 20.7, 24.0]


def drawdowns(prices):
    result = []
    peak = prices[0]
    for price in prices:
        result.append(price / peak - 1)
    return result


falls = drawdowns(prices)
for i in range(len(prices)):
    print(f"Month {i}: ${prices[i]:.2f}, drawdown {falls[i]:.1%}")
