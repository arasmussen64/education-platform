age = int(input("Age? "))
member = input("Member (yes/no)? ")
if age < 12 or age >= 65:
    price = 6
else:
    price = 10
if member == "yes" and price > 6:
    price = price - 2
print(f"Price: ${price}")
