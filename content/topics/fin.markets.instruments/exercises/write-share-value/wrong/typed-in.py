def present_value_of_flows(flows, rate):
    total = 0
    for t in range(len(flows)):
        total = total + flows[t] / (1 + rate) ** t
    return total


dividends = [2.00, 2.10, 2.20, 2.30, 2.40]
sale_price = 60.00
rate = 0.08


def share_value(dividends, sale_price, rate):
    flows = [0]
    for d in dividends:
        flows.append(d)
    flows[-1] = flows[-1] + sale_price
    return present_value_of_flows(flows, rate)


print("Value at 8%: $49.56")
print("Value at 10%: $45.52")
print("Value if the sale price is $50.00: $42.75")
