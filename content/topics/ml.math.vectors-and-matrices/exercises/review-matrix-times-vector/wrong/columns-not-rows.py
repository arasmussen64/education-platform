m = [[2, 0], [1, 3]]
v = [4, 5]
result = []
for j in range(len(v)):
    entry = 0
    for i in range(len(m)):
        entry = entry + m[i][j] * v[i]
    result.append(entry)
print(result)
