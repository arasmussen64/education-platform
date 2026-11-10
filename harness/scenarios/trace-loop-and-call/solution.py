def square(n):
    return n * n


total = 0
for i in range(1, 4):
    total = total + square(i)
    print(i, total)
print("done", total)
