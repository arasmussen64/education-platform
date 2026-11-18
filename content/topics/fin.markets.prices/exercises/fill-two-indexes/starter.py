companies = {"Alpha": {"shares": 50, "start": 20.0, "end": 30.0}, "Beta": {"shares": 10, "start": 100.0, "end": 90.0}, "Gamma": {"shares": 200, "start": 5.0, "end": 5.5}}

price_start = 0
price_end = 0
value_start = 0
value_end = 0
for name in companies:
    company = companies[name]
    price_start = price_start + company["start"]
    price_end = price_end + company["end"]
    value_start = value_start + company["start"] ... company["shares"]
    value_end = value_end + company["end"] ... company["shares"]

print(f"price-weighted: {(price_end ... price_start - 1) * 100:+.1f}%")
print(f"cap-weighted: {(value_end ... value_start - 1) * 100:+.1f}%")
