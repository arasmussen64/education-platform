import json
from dataclasses import dataclass


@dataclass
class Order:
    id: int
    item: str
    qty: int


def is_valid(record):
    if not isinstance(record, dict):
        return False
    if not isinstance(record.get("id"), int):
        return False
    item = record.get("item")
    if not isinstance(item, str) or item == "":
        return False
    qty = record.get("qty")
    return isinstance(qty, int) and qty > 0


def load_orders(text):
    orders = []
    bad = []
    for position, record in enumerate(json.loads(text)):
        if is_valid(record):
            orders.append(Order(record["id"], record["item"], record["qty"]))
        else:
            bad.append(position)
    return orders, bad


text = '[{"id": 1, "item": "pen", "qty": 2}, {"id": 2, "item": "", "qty": 1}, {"id": 3, "item": "ink", "qty": "5"}, {"id": 4, "item": "pad", "qty": 0}]'
orders, bad = load_orders(text)
print(orders)
print(bad)
