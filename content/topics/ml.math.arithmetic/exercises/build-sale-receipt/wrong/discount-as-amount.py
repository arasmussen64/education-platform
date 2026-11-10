price = 120
discount_percent = 15
tax_percent = 8
discount = discount_percent
after_discount = price - discount
tax = after_discount * tax_percent / 100
total = after_discount + tax
print(f"Discount: {discount:.2f}")
print(f"Price after discount: {after_discount:.2f}")
print(f"Tax: {tax:.2f}")
print(f"Total: {total:.2f}")
