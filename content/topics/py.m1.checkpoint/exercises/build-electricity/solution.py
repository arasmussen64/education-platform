units = float(input("kWh used? "))
price = float(input("Price per kWh? "))
tax_percent = int(input("Tax (%)? "))
energy = units * price
tax = energy * tax_percent / 100
total = energy + tax
print(f"Energy: ${energy:.2f}")
print(f"Tax ({tax_percent}%): ${tax:.2f}")
print(f"Total: ${total:.2f}")
