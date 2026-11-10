import json
from dataclasses import dataclass


@dataclass
class Order:
    id: int
    item: str
    qty: int


def load_orders(text):
    orders = []
    bad = []
    for position, record in enumerate(json.loads(text)):
        try:
            qty = int(record["qty"])
            if record["item"] and qty > 0:
                orders.append(Order(int(record["id"]), record["item"], qty))
            else:
                bad.append(position)
        except (KeyError, TypeError, ValueError):
            bad.append(position)
    return orders, bad


text = '[{"id": 1, "item": "pen", "qty": 2}, {"id": 2, "item": "", "qty": 1}, {"id": 3, "item": "ink", "qty": "5"}, {"id": 4, "item": "pad", "qty": 0}]'
orders, bad = load_orders(text)
print(orders)
print(bad)
