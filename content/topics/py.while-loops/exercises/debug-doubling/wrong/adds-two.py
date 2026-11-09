target = int(input("Target? "))
amount = 1
steps = 0
while amount < target:
    amount = amount + 2
    steps = steps + 1
    print(f"Step {steps}: {amount}")
print(f"Reached {target} in {steps} steps")
