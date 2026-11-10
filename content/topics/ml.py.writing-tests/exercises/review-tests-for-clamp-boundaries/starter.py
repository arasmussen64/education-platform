def clamp(value, low, high):
    return max(low, min(value, high))


# Your tests go here.

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
