principal = 10000
yearly_rate = 0.06
payments = [300, 350, 400]


def months_to_repay(principal, rate, monthly):
    balance = principal
    months = 0
    while balance > 0:
        balance = balance - monthly
        months = months + 1
    return months


for monthly in payments:
    months = months_to_repay(principal, yearly_rate / 12, monthly)
    print(f"{monthly} a month: {months} months")
