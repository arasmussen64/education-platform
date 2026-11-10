target = 10
ways = 0
for first in range(1, 7):
    for second in range(1, 7):
        if first + second >= target:
            ways = ways + 1
chance = ways / 36
print(f"Ways: {ways}")
print(f"Chance: {chance:.1f}%")
