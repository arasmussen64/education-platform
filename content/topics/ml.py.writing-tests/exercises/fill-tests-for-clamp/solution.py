def clamp(value, low, high):
    return max(low, min(value, high))


def test_inside_the_range_is_unchanged():
    assert clamp(5, 0, 10) == 5


def test_above_the_range_becomes_the_high_end():
    assert clamp(15, 0, 10) == 10


def test_below_the_range_becomes_the_low_end():
    assert clamp(-3, 0, 10) == 0

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
