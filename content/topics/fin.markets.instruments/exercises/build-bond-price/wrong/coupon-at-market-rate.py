def present_value_of_flows(flows, rate):
    total = 0
    for t in range(len(flows)):
        total = total + flows[t] / (1 + rate) ** t
    return total


def bond_price(face, coupon_rate, years, market_rate):
    flows = [0]
    for year in range(years):
        flows.append(face * market_rate)
    flows[-1] = flows[-1] + face
    return present_value_of_flows(flows, market_rate)


face = 1000
coupon_rate = 0.04
years = 6

for market_rate in [0.02, 0.04, 0.06]:
    print(f"At {market_rate:.0%}: ${bond_price(face, coupon_rate, years, market_rate):,.2f}")
