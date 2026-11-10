def multiply(a, b):
    result = []
    for i in range(len(a)):
        row = []
        for j in range(len(b)):
            entry = 0
            for k in range(len(a[0])):
                entry = entry + a[i][k] * b[j][k]
            row.append(entry)
        result.append(row)
    return result


product = multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
for row in product:
    print(row)
