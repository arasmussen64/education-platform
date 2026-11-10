a = [1, 2, 3]
b = [4, 5, 6]
total = []
for i in range(len(a)):
    total.append(a[i] + b[i])
print(total)

scaled = []
for value in a:
    scaled.append(3 * value)
print(scaled)

dot = 0
for i in range(len(a)):
    dot = dot + a[i] * b[i]
print(dot)

c = [3, 4]
length = (c[0] * c[0] + c[1] * c[1]) ** 0.5
print(length)
