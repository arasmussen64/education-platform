from dataclasses import dataclass


@dataclass
class Line:
    item: str
    quantity: int
    unit_price: float

    def total(self) -> float:
        return self.quantity * self.unit_price


def order_total(lines: list[Line]) -> float:
    total = 0.0
    for line in lines:
        total = total + line.total()
    return total


order = [Line("pen", 3, 1.5), Line("notebook", 2, 4.25)]
print(order[0])
print(order_total(order))
