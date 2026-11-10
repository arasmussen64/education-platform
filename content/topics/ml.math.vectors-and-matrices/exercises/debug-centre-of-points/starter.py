points = [[1, 2], [3, 4], [5, 0]]
centre = []
for j in range(len(points)):
    total = 0
    for point in points:
        total = total + point[j]
    centre.append(total / len(points[0]))
print(centre)
