item = input("Item? ")
quantity = int(input("How many? "))
price = float(input("Price each? "))
total = quantity * price
print("{quantity} {item} cost ${total:.2f}")
