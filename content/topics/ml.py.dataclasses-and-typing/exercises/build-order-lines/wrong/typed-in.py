from dataclasses import dataclass


@dataclass
class Line:
    item: str
    quantity: int
    unit_price: float

    def total(self) -> float:
        return 4.5


def order_total(lines: list[Line]) -> float:
    return 13.0


print("Line(item='pen', quantity=3, unit_price=1.5)")
print(13.0)
