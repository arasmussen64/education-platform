item = input("Item? ")
count = int(input("How many? "))
each = float(input("Price each? "))
total = count * each
print(f"{count} {item}: ${total:.2f}")
