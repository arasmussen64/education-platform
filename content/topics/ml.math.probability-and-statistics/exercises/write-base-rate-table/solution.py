population = 1000
rate = 0.01
sensitivity = 0.9
false_positive = 0.1
sick = population * rate
healthy = population - sick
print(f"Positive and sick: {sick * sensitivity:.0f}")
print(f"Positive and healthy: {healthy * false_positive:.0f}")
