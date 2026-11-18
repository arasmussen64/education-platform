# A cap-weighted index of three made-up companies, set to 100 on day 0.
# Shares are in millions.
shares = {"North": 40, "South": 5, "West": 125}
prices = [
    {"North": 25.0, "South": 200.0, "West": 10.0},
    {"North": 26.0, "South": 190.0, "West": 10.6},
    {"North": 28.0, "South": 182.0, "West": 11.3},
]


def market_value(day_prices):
    total = 0
    for name in day_prices:
        total = total + day_prices[name] * shares[name]
    return total


start_value = market_value(prices[0])
for day in range(len(prices)):
    level = 100 * market_value(prices[day]) / start_value
    print(f"day {day}: {level:.2f}")
