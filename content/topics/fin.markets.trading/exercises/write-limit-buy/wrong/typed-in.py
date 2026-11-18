asks = [
    {"price": 50.05, "shares": 100},
    {"price": 50.10, "shares": 200},
    {"price": 50.20, "shares": 400},
]


def limit_buy(asks, shares, limit):
    return 300


filled = limit_buy(asks, 500, 50.10)
print(f"filled {filled} now")
print(f"{500 - filled} wait on the book as a bid at 50.10")
