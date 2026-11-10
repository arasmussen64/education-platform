def two_sum(numbers, target):
    """A pair of values from the list adding to target, as (earlier, later), or None; one pass."""
    seen = set()
    for number in numbers:
        if target - number in seen:
            return (target - number, number)
        seen.add(number)
    return None


print(two_sum([3, 9, 14, 5, 11], 20))
print(two_sum([3, 9, 14, 5, 11], 100))
print(two_sum([8, 8], 16))
