# Read the inputs
age = int(input("Age? "))
day = input("Day? ")
member = input("Member (yes/no)? ")

# Work out the ticket
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
if ...:
    price = price + 2
if ...:
    price = price * 0.9

# Print the ticket
print(f"Ticket: {kind}")
print(f"Price: ${price:.2f}")
