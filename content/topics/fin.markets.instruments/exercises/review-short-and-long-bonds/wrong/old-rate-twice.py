def present_value_of_flows(flows, rate):
    total = 0
    for t in range(len(flows)):
        total = total + flows[t] / (1 + rate) ** t
    return total


old_rate = 0.035
new_rate = 0.045


def bond_price(face, coupon_rate, years, market_rate):
    flows = [0]
    for year in range(years):
        flows.append(face * coupon_rate)
    flows[-1] = flows[-1] + face
    return present_value_of_flows(flows, market_rate)


for years in [2, 10, 30]:
    before = bond_price(1000, 0.04, years, old_rate)
    after = bond_price(1000, 0.04, years, old_rate + 0.001)
    print(f"{years} years: ${before:,.2f} to ${after:,.2f}, {(after - before) / before:.1%}")
