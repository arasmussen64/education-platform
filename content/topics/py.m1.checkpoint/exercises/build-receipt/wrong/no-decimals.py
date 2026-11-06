meal = float(input("Meal? "))
drinks = float(input("Drinks? "))
tip_percent = int(input("Tip (%)? "))
subtotal = meal + drinks
tip = subtotal * tip_percent / 100
total = subtotal + tip
print(f"Subtotal: ${subtotal}")
print(f"Tip ({tip_percent}%): ${tip}")
print(f"Total: ${total}")
