bill = float(input("Bill? "))
people = int(input("People? "))
tip_percent = int(input("Tip (%)? "))
tip = bill * tip_percent / 100
each = (bill + tip) / people
print(f"Bill: ${bill:.2f}")
print(f"Tip ({tip_percent}%): ${tip:.2f}")
print(f"Each of {people} pays: ${each:.2f}")
