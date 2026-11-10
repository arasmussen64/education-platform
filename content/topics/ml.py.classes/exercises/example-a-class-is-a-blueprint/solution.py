class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance = self.balance + amount

    def __repr__(self):
        return f"Account({self.owner!r}, {self.balance})"


ada = Account("Ada", 100)
bob = Account("Bob")
ada.deposit(50)
bob.deposit(20)
print(ada)
print(bob)
print(ada.balance)
