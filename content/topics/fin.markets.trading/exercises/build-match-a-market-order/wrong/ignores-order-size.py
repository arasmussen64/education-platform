asks = [
    {"id": "S1", "price": 20.10, "shares": 300},
    {"id": "S2", "price": 20.05, "shares": 100},
    {"id": "S3", "price": 20.10, "shares": 200},
    {"id": "S4", "price": 20.25, "shares": 500},
]


def best_ask(asks):
    # The lowest price wins. On a tie the earlier order wins, and the list is
    # in the order the orders arrived, so only a strictly lower price replaces it.
    best = None
    for order in asks:
        if best is None or order["price"] < best["price"]:
            best = order
    return best


def match_market_buy(asks, shares):
    fills = []
    while shares > 0 and len(asks) > 0:
        order = best_ask(asks)
        taken = shares
        fills.append({"id": order["id"], "price": order["price"], "shares": taken})
        shares = shares - taken
        if taken == order["shares"]:
            asks.remove(order)
        else:
            order["shares"] = order["shares"] - taken
    return fills


fills = match_market_buy(asks, 500)
cost = 0
bought = 0
for fill in fills:
    print(f"{fill['shares']} at {fill['price']:.2f} from {fill['id']}")
    cost = cost + fill["shares"] * fill["price"]
    bought = bought + fill["shares"]
print(f"average price {cost / bought:.2f}")
print("left on the book:")
for order in asks:
    print(f"{order['id']} {order['shares']} at {order['price']:.2f}")
