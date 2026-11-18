def present_value(future, rate, periods):
    return future / (1 + rate) ** periods


offer_now = 10000
offer_later = 11000
rate = 0.06
years = 2

later_today = present_value(offer_later, rate, years)
print(f"The later offer, today: {later_today:,.2f}")
print(f"Money now wins by: {offer_now - later_today:,.2f}")

now_later = offer_now * (1 + rate) ** years
print(f"The offer now, in {years} years: {now_later:,.2f}")
