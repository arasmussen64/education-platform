import math

balance = 1000
rate = 0.07
print(f"Year 0: {balance:,.2f}")
for year in range(1, 6):
    balance = balance * (1 + rate)
    print(f"Year {year}: {balance:,.2f}")

formula = 1000 * (1 + rate) ** 5
print(f"Formula: {formula:,.2f}")
print(f"Rule of 72: doubles in about {72 / (rate * 100):.1f} years")
print(f"Exactly: {math.log(2) / math.log(1 + rate):.1f} years")
