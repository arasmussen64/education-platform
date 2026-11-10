import math

power = 0.5
reference = 1e-12
ratio = power / reference
decibels = 10 * math.log(ratio)
print(f"{decibels:.1f} dB")
