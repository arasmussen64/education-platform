x = 0.0
rate = 0.1
steps = 0
slope = 2 * (x - 3)
while abs(slope) > 0.01 and steps < 1000:
    x = x - rate * slope
    steps = steps + 1
print(f"Stopped at {x:.3f} after {steps} steps")
