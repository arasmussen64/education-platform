def cost(km):
    return 3.0 + 1.2 * km


for km in (1, 5, 10):
    print(f"{km} km: {cost(km):.2f}")
