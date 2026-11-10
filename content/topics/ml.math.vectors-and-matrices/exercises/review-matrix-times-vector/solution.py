m = [[2, 0], [1, 3]]
v = [4, 5]
result = []
for row in m:
    entry = 0
    for j in range(len(row)):
        entry = entry + row[j] * v[j]
    result.append(entry)
print(result)
