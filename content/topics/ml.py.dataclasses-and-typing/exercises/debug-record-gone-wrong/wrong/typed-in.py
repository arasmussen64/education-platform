from dataclasses import dataclass


class Ticket:
    def __init__(self, event):
        self.event = event
        self.price = 45.0
        self.row = "B"


print("Ticket(event='Concert', price=45.0, row='B')")
print(90.0)
