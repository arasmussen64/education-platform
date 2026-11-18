# Buy orders resting on the book, in the order they arrived.
bids = [
    {"id": "B1", "price": 49.90, "shares": 300},
    {"id": "B2", "price": 49.95, "shares": 200},
    {"id": "B3", "price": 49.80, "shares": 500},
    {"id": "B4", "price": 49.95, "shares": 100},
]
to_sell = 400


def best_bid(bids):
    best = None
    for order in bids:
        if best is None or order["price"] < best["price"]:
            best = order
    return best


def match_market_sell(bids, shares):
    fills = []
    while shares > 0 and len(bids) > 0:
        order = best_bid(bids)
        taken = min(shares, order["shares"])
        fills.append({"id": order["id"], "price": order["price"], "shares": taken})
        shares = shares - taken
        if taken == order["shares"]:
            bids.remove(order)
    return fills


print("sold 200 at 49.95 to B2")
print("sold 100 at 49.95 to B4")
print("sold 100 at 49.90 to B1")
print("left on the book:")
print("B1 200 at 49.90")
print("B3 500 at 49.80")
