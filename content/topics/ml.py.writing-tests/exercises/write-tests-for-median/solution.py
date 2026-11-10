def median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def test_odd_count_out_of_order():
    assert median([3, 1, 2]) == 2


def test_even_count_takes_the_middle_two():
    assert median([4, 1, 3, 2]) == 2.5

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
