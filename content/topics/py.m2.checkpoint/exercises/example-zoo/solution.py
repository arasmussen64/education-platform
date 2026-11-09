# Read the inputs
age = int(input("Age? "))
day = input("Day? ")
pass_holder = input("Annual pass (yes/no)? ")

# Work out the ticket
if age < 3:
    kind = "free"
    price = 0
elif age <= 15:
    kind = "child"
    price = 9
elif age >= 60:
    kind = "senior"
    price = 11
else:
    kind = "adult"
    price = 16
if (day == "Sat" or day == "Sun") and price > 0:
    price = price + 3
if pass_holder == "yes":
    price = price * 0.75

# Print the ticket
print(f"Zoo ticket: {kind}")
print(f"Price: ${price:.2f}")
