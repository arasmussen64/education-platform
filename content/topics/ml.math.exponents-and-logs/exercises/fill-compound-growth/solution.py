start = 1000
rate = 5
years = 10
balance = start * (1 + rate / 100) ** years
print(f"After {years} years: {balance:.2f}")
