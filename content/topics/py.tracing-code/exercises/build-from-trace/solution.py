score = 50
bonus = 20
if score >= 50:
    score = score + bonus
else:
    bonus = 0
if score > 60:
    print("High")
else:
    print("Low")
print(score, bonus)
