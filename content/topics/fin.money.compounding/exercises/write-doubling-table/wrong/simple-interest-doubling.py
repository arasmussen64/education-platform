import math


def rule_of_72(rate):
    return 72 / (rate * 100)


def doubling_time(rate):
    return 1 / rate


rates = [0.02, 0.06, 0.10, 0.24]
for rate in rates:
    print(f"{rate * 100:.0f}%: rule {rule_of_72(rate):.1f}, exact {doubling_time(rate):.1f}")
