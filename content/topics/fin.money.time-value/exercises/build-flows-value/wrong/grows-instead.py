flows = [-5000, 1500, 2000, 2500]
rate = 0.07


def present_value_of_flows(flows, rate):
    total = 0
    for t in range(len(flows)):
        total = total + flows[t] * (1 + rate) ** t
    return total


worth = present_value_of_flows(flows, rate)
print(f"Worth today: {worth:,.2f}")
