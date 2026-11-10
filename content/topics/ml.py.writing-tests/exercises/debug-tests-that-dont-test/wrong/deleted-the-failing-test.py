def add(a, b):
    return a + b


def test_zero_changes_nothing():
    assert add(7, 0) == 7


def test_negative_numbers():
    assert add(-2, -3) == -5


def test_nothing():
    pass

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
