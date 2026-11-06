item = input("Item? ")
quantity = float(input("How many? "))
price = float(input("Price each? "))
total = quantity * price
print(f"{quantity} {item} cost ${total:.2f}")
