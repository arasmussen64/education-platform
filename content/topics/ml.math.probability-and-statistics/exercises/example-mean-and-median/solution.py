scores = [2, 4, 4, 10]
mean = sum(scores) / len(scores)
ordered = sorted(scores)
middle = len(ordered) // 2
median = (ordered[middle - 1] + ordered[middle]) / 2
print("mean", mean)
print("median", median)
