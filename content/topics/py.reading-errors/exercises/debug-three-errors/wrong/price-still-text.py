item = input("Item? ")
count = int(input("How many? "))
each = input("Price each? ")
total = count * each
print(f"{count} {item}: ${total:.2f}")
