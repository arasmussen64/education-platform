from dataclasses import dataclass


@dataclass
class Order:
    id: int
    item: str
    qty: int


def load_orders(text):
    return [Order(1, "pen", 2)], [1, 2, 3]


print([Order(1, "pen", 2)])
print([1, 2, 3])
