# A made-up order book for one stock, best prices first.
bids = [
    {"price": 99.95, "shares": 300},
    {"price": 99.90, "shares": 500},
    {"price": 99.80, "shares": 1000},
]
asks = [
    {"price": 100.05, "shares": 200},
    {"price": 100.10, "shares": 400},
    {"price": 100.25, "shares": 1000},
]

best_bid = bids[0]["price"]
best_ask = asks[0]["price"]
spread = best_ask - best_bid
middle = (best_bid + best_ask) / 2
print(f"bid {best_bid:.2f}, ask {best_ask:.2f}, spread {spread:.2f}, middle {middle:.2f}")

# A market order to buy 500 shares takes the cheapest asks first.
wanted = 500
cost = 0
for order in asks:
    taken = min(wanted, order["shares"])
    if taken > 0:
        print(f"bought {taken} at {order['price']:.2f}")
    cost = cost + taken * order["price"]
    wanted = wanted - taken

print(f"paid {cost:,.2f}, an average of {cost / 500:.2f} a share")
print(f"above the middle: {cost - 500 * middle:.2f}")
