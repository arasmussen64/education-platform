def multiply(a, b):
    rows = len(a)
    inner = len(b)
    columns = len(b[0])
    result = []
    for i in range(rows):
        row = []
        for j in range(columns):
            entry = 0
            for k in range(inner):
                entry = entry + a[i][k] * b[k][j]
            row.append(entry)
        result.append(row)
    return result


product = multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
for row in product:
    print(row)
