how_many = int(input("How many? "))
total = 0
for _ in range(1, how_many):
    n = int(input("Number? "))
    total += n
average = total / how_many
print(f"Average: {average:.1f}")
