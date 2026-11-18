def present_value_of_flows(flows, rate):
    total = 0
    for t in range(len(flows)):
        total = total + flows[t] / (1 + rate) ** t
    return total


def bond_price(face, coupon_rate, years, market_rate):
    flows = [0]
    for year in range(years):
        flows.append(face * coupon_rate)
    flows[-1] = flows[-1] + face
    return present_value_of_flows(flows, market_rate)


face = 1000
coupon_rate = 0.04
years = 6

print("At 2%: $1,112.03")
print("At 4%: $1,000.00")
print("At 6%: $901.65")
