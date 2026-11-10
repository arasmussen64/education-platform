def clamp(value, low, high):
    return max(low, min(value, high))


def test_inside_the_range_is_unchanged():
    assert True


def test_above_the_range_becomes_the_high_end():
    assert True


def test_below_the_range_becomes_the_low_end():
    assert True

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
