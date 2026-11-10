import math

power = 0.5
reference = 1e-12
ratio = reference / power
decibels = 10 * math.log10(ratio)
print(f"{decibels:.1f} dB")
