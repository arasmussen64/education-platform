age = int(input("Age? "))
day = input("Day? ")
member = input("Member (yes/no)? ")
if age < 5:
    kind = "free"
    price = 0
elif age <= 12:
    kind = "child"
    price = 6
elif age >= 65:
    kind = "senior"
    price = 8
else:
    kind = "adult"
    price = 12
if member == "yes":
    price = price * 0.9
if (day == "Sat" or day == "Sun") and price > 0:
    price = price + 2
print(f"Ticket: {kind}")
print(f"Price: ${price:.2f}")
