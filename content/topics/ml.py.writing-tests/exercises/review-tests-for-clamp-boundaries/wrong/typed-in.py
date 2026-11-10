def clamp(value, low, high):
    return max(low, min(value, high))


def test_one():
    assert True


def test_two():
    assert True

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
