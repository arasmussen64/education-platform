principal = 6000
yearly_rate = 0.09
months = 6


def payment(principal, rate, periods):
    return principal * rate / (1 - (1 + rate) ** -periods)


rate = yearly_rate / 12
monthly = payment(principal, rate, months)
print(f"Payment: {monthly:,.2f}")

balance = principal
total_interest = 0
for month in range(1, months + 1):
    interest = balance * rate
    paid_down = monthly - interest
    balance = balance - paid_down
    total_interest = total_interest + round(interest, 2)
    print(
        f"Month {month}: interest {interest:,.2f}, "
        f"paid down {paid_down:,.2f}, balance {balance:,.2f}"
    )

print(f"Total paid: {monthly * months:,.2f}")
print(f"Total interest: {total_interest:,.2f}")
