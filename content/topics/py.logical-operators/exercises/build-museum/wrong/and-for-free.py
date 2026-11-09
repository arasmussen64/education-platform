age = int(input("Age? "))
member = input("Member (yes/no)? ")
if age < 5 and age >= 70:
    price = 0
elif age <= 17:
    price = 4
else:
    price = 12
if member == "yes" and price > 0:
    price = price / 2
print(f"Entry: ${price:.2f}")
