principal = 300000
yearly_rate = 0.06
years = 30

rate = yearly_rate / 12
months = years * 12
monthly = principal * rate / (1 - (1 + rate) ** -months)
print(f"Payment: {monthly:,.2f}")

balance = principal
for month in range(1, 3):
    interest = balance * rate
    paid_down = monthly - interest
    balance = balance - paid_down
    print(f"Month {month}: interest {interest:,.2f}, paid down {paid_down:,.2f}")
    print(f"  balance {balance:,.2f}")

print(f"Total interest: {monthly * months - principal:,.2f}")
