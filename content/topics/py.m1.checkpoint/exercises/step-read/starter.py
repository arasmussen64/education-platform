# Read the inputs
meal = ...
drinks = ...
tip_percent = ...

# Work out the numbers
subtotal = meal + drinks
tip = subtotal * tip_percent / 100
total = subtotal + tip

# Print the receipt
print(f"Subtotal: ${subtotal:.2f}")
print(f"Tip ({tip_percent}%): ${tip:.2f}")
print(f"Total: ${total:.2f}")
