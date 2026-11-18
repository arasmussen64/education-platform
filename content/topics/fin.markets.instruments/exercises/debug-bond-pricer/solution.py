face = 1000
coupon_rate = 0.03
years = 4
market_rate = 0.05

price = 0
for t in range(1, years + 1):
    coupon = face * coupon_rate
    price = price + coupon / (1 + market_rate) ** t
price = price + face / (1 + market_rate) ** years

print(f"Price: ${price:,.2f}")
if round(price, 2) < face:
    print("Below face value: the market wants more than the coupon pays")
else:
    print("At or above face value: the coupon pays at least what the market wants")
