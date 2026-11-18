def present_value_of_flows(flows, rate):
    total = 0
    for t in range(len(flows)):
        total = total + flows[t] / (1 + rate) ** t
    return total


dividends = [2.00, 2.10, 2.20, 2.30, 2.40]
sale_price = 60.00
rate = 0.08


def share_value(dividends, sale_price, rate):
    # Build the cash flows: nothing today, one dividend a year, and the sale
    # price added to the last year. Return their present value.
    ...


# Print the three lines.
