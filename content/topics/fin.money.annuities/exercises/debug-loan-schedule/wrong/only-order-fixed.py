principal = 4800
yearly_rate = 0.12
months = 6

rate = yearly_rate / 12
monthly = principal * rate / (1 - (1 + rate) ** -months)
print(f"Payment: {monthly:,.2f}")

balance = principal
for month in range(1, months + 1):
    interest = balance * yearly_rate
    balance = balance + interest - monthly
    print(f"Month {month}: interest {interest:,.2f}, balance {balance:,.2f}")
