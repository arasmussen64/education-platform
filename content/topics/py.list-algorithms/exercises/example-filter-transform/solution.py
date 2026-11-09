scores = [72, 45, 88, 91, 60]
passing = []
for score in scores:
    if score >= 60:
        passing.append(score)
print(passing)

doubled = []
for score in scores:
    doubled.append(score * 2)
print(doubled)

print(sorted(scores))
print(sorted(scores)[-3:])
