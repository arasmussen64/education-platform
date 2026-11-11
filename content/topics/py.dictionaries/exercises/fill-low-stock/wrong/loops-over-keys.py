stock = {"apples": 3, "pears": 12, "plums": 0}
low = []
for fruit, count in stock:
    print(f"{fruit}: {count}")
    if count < 5:
        low.append(fruit)
print(low)
