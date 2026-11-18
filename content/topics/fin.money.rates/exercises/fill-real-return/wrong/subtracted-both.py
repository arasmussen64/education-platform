nominal = 0.07
inflation = 0.03
real = (1 + nominal) - (1 + inflation) - 1
rough = nominal - inflation
print(f"Real return: {real:.2%}")
print(f"Rough guess: {rough:.2%}")
