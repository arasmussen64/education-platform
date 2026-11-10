from dataclasses import dataclass


class Ticket:
    event: str
    price: float = "45.0"
    row: str = "B"


one = Ticket("Concert")
print(one)
print(one.price * 2)
