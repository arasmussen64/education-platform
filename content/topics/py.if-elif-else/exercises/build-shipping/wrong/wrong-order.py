weight = float(input("Weight (kg)? "))
if weight <= 5:
    cost = 9.5
elif weight <= 1:
    cost = 5.0
else:
    cost = 20.0
print(f"Shipping: ${cost:.2f}")
