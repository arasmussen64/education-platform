def count_steps(n):
    """How many comparisons a nested-loop duplicate check makes on n distinct items."""
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            count += 1
    return count


print(count_steps(10), count_steps(100), count_steps(1000))
print(count_steps(2000) // count_steps(1000))
