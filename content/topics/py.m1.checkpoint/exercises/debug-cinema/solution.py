adults = int(input("Adult tickets? "))
children = int(input("Child tickets? "))
price = float(input("Adult price? "))
total = (adults + children / 2) * price
print("Tickets:", adults + children)
print(f"Total: ${total:.2f}")
