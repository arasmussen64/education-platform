weight = float(input("Weight (kg)? "))
if weight <= 1:
    cost = 5
elif weight <= 5:
    cost = 9.5
else:
    cost = 20
print(f"Shipping: ${cost}")
