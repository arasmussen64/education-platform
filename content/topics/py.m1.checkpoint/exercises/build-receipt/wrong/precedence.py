meal = float(input("Meal? "))
drinks = float(input("Drinks? "))
tip_percent = int(input("Tip (%)? "))
subtotal = meal + drinks
tip = meal + drinks * tip_percent / 100
total = subtotal + tip
print(f"Subtotal: ${subtotal:.2f}")
print(f"Tip ({tip_percent}%): ${tip:.2f}")
print(f"Total: ${total:.2f}")
