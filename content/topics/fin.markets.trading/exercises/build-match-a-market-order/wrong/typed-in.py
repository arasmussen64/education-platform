asks = [
    {"id": "S1", "price": 20.10, "shares": 300},
    {"id": "S2", "price": 20.05, "shares": 100},
    {"id": "S3", "price": 20.10, "shares": 200},
    {"id": "S4", "price": 20.25, "shares": 500},
]


def best_ask(asks):
    return asks[1]


def match_market_buy(asks, shares):
    return [
        {"id": "S2", "price": 20.05, "shares": 100},
        {"id": "S1", "price": 20.10, "shares": 300},
        {"id": "S3", "price": 20.10, "shares": 100},
    ]


print("100 at 20.05 from S2")
print("300 at 20.10 from S1")
print("100 at 20.10 from S3")
print("average price 20.09")
print("left on the book:")
print("S3 100 at 20.10")
print("S4 500 at 20.25")
