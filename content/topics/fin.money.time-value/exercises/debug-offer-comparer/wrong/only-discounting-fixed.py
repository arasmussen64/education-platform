rate = 0.08
offer_a = [3000, 3000, 3000]
offer_b = [0, 4000, 5200]


def worth_today(flows, rate):
    total = 0
    for t in range(len(flows)):
        total = total + flows[t] / (1 + rate) ** t
    return total


a = worth_today(offer_a, rate)
b = worth_today(offer_b, rate)
print(f"Offer A: {a:,.2f}")
print(f"Offer B: {b:,.2f}")
if sum(offer_a) > sum(offer_b):
    print("Take offer A")
else:
    print("Take offer B")
