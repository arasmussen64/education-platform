meal = float(input("Meal? "))
drinks = float(input("Drinks? "))
tip_percent = int(input("Tip (%)? "))
subtotal = meal + drinks
tip = subtotal * tip_percent / 100
total = subtotal + tip
print("Subtotal: $", f"{subtotal:.2f}")
print(f"Tip ({tip_percent}%): ${tip:.2f}")
print("Total: $", f"{total:.2f}")
