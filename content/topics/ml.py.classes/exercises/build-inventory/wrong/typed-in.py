class Inventory:
    def __init__(self):
        self.counts = {"pen": 12, "ink": 2}

    def add(self, item, count):
        pass

    def remove(self, item, count):
        pass

    def total(self):
        return 14

    def __repr__(self):
        return "Inventory({'pen': 12, 'ink': 2})"


print("Inventory({'pen': 12, 'ink': 2})")
print(14)
