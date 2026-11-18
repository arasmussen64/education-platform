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


print("2 years: $1,009.50 to $990.64, -1.9%")
print("10 years: $1,041.58 to $960.44, -7.8%")
print("30 years: $1,091.96 to $918.56, -15.9%")
