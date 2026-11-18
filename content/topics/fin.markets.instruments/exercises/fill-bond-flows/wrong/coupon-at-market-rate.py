def present_value_of_flows(flows, rate):
    total = 0
    for t in range(len(flows)):
        total = total + flows[t] / (1 + rate) ** t
    return total


face = 500
coupon_rate = 0.06
years = 4
market_rate = 0.08

coupon = face * market_rate
flows = [0]
for year in range(years):
    flows.append(coupon)
flows[-1] = flows[-1] + face
print(f"Price: ${present_value_of_flows(flows, market_rate):,.2f}")
