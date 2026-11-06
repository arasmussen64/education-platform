# Read the inputs
price = float(input("Price each? "))
quantity = int(input("How many? "))
discount_percent = int(input("Discount (%)? "))

# Work out the numbers
subtotal = price * quantity
discount = subtotal * discount_percent / 100
total = subtotal - discount

# Print the receipt
print(f"Subtotal: ${subtotal:.2f}")
print(f"Discount ({discount_percent}%): -${discount:.2f}")
print(f"Total: ${total:.2f}")
