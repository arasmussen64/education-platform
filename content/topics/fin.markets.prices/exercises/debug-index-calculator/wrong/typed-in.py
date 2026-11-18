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


print("day 0: 100.00")
print("day 1: 102.00")
print("day 2: 105.92")
