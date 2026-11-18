monthly = 250
rate = 0.01
months = 24

by_loop = 0
for t in range(..., months + 1):
    by_loop = by_loop + monthly / (1 + rate) ** ...
by_formula = monthly * (1 - (1 + rate) ** ...) / rate
print(f"By loop: {by_loop:,.2f}")
print(f"By formula: {by_formula:,.2f}")
