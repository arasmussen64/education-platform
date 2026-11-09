age = int(input("Age? "))
session = input("Session? ")
card = input("Swim card (yes/no)? ")
if age < 3:
    kind = "free"
    price = 0
elif age <= 15:
    kind = "child"
    price = 3
elif age >= 60:
    kind = "senior"
    price = 3.5
else:
    kind = "adult"
    price = 5
if session == "evening":
    price = price + 1
if card == "yes":
    price = price * 0.8
print(f"Ticket: {kind}")
print(f"Price: ${price:.2f}")
