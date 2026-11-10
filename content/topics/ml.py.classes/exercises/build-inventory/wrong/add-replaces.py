class Inventory:
    def __init__(self):
        self.counts = {}

    def add(self, item, count):
        self.counts[item] = count

    def remove(self, item, count):
        self.counts[item] = self.counts.get(item, 0) - count

    def total(self):
        return sum(self.counts.values())

    def __repr__(self):
        return f"Inventory({self.counts})"


stock = Inventory()
stock.add("pen", 10)
stock.add("ink", 2)
stock.add("pen", 5)
stock.remove("pen", 3)
print(stock)
print(stock.total())
