def present_value(future, rate, periods):
    return future / (1 + rate) ** periods


offer_now = 8000
offer_later = 9000
rate = 0.05
years = 3

later_today = present_value(offer_later, rate, years)
print(f"The later offer, today: {later_today:,.2f}")
if later_today < offer_now:
    print("Take the later offer")
else:
    print("Take the money now")
