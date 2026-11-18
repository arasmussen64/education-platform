def present_value(future, rate, periods):
    return future / (1 + rate) ** periods


amounts = [9000, 10000, 10500]
years = [0, 2, 4]
rate = 0.05

best = 0
for i in range(len(amounts)):
    today = present_value(amounts[i], rate, years[i])
    print(f"Year {years[i]}: {today:,.2f}")
    if today > present_value(amounts[best], rate, years[best]):
        best = i
print(f"Best: the offer in year {years[best]}")
