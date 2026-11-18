deposit = 300
annual_rate = 0.06
months = 6
fund_prices = [20.0, 20.6, 19.9, 21.0, 21.4]


def print_savings(deposit, annual_rate, months):
    rate = annual_rate / 12
    balance = 0
    total_interest = 0
    for month in range(1, months + 1):
        interest = balance * rate
        balance = balance + interest + deposit
        total_interest = total_interest + interest
        print(f"month {month}: interest {interest:,.2f}, balance {balance:,.2f}")
    print(f"deposited {deposit * months:,.2f}")
    print(f"total interest {total_interest:,.2f}")


def monthly_changes(prices):
    changes = []
    for i in range(1, len(prices)):
        changes.append(prices[i] / prices[i - 1] - 1)
    return changes


def highest_so_far(prices):
    peaks = []
    peak = prices[0]
    for price in prices:
        peak = max(peak, price)
        peaks.append(peak)
    return peaks


print_savings(deposit, annual_rate, months)
changes = monthly_changes(fund_prices)
print(f"best month {max(changes) * 100:.1f}%, worst month {min(changes) * 100:.1f}%")
print(f"highest so far: {highest_so_far(fund_prices)}")
