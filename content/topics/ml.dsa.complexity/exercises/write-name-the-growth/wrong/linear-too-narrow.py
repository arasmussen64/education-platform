def growth_name(counts):
    """Name the growth from step counts at n, 2n, 4n, ...: the average ratio between neighbours."""
    ratios = [later / earlier for earlier, later in zip(counts, counts[1:])]
    average = sum(ratios) / len(ratios)
    if average < 1.5:
        return "constant"
    if average < 1.9:
        return "linear"
    if average < 6:
        return "quadratic"
    return "faster than quadratic"


print(growth_name([7, 7, 7]))
print(growth_name([100, 201, 398]))
print(growth_name([45, 190, 780]))
print(growth_name([8, 64, 512]))
