def present_value_of_flows(flows, rate):
    total = 0
    for t in range(len(flows)):
        total = total + flows[t] / (1 + rate) ** t
    return total


face = 1000
coupon_rate = 0.05
years = 3

coupon = face * coupon_rate
flows = [0]
for year in range(1, years + 1):
    flows.append(coupon)
flows[-1] = flows[-1] + face
print("Cash flows:", flows)

for market_rate in [0.03, 0.05, 0.07]:
    price = present_value_of_flows(flows, market_rate)
    print(f"Market rate {market_rate:.0%}: ${price:,.2f}")
