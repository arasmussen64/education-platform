def clamp(value, low, high):
    return max(low, min(value, high))


def test_inside():
    assert clamp(5, 0, 10) == 5


def test_also_inside():
    assert clamp(7, 0, 10) == 7

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
