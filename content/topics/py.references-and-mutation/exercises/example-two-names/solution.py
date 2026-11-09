scores = [70, 80, 90]
same = scores
copy = list(scores)
same.append(100)
copy.append(0)
print(scores)
print(same)
print(copy)
print(same is scores)
print(copy is scores)
