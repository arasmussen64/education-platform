def clamp(value, low, high):
    return max(low, min(value, high))


def test_the_high_end_is_inside():
    assert clamp(10, 0, 10) == 10


def test_the_low_end_is_inside():
    assert clamp(0, 0, 10) == 0

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
