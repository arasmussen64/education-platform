apples = int(input("Apples? "))
oranges = int(input("Oranges? "))
if apples > oranges:
    difference = apples - oranges
    print(f"More apples, by {difference}")
elif oranges > apples:
    difference = oranges - apples
    print(f"More oranges, by {difference}")
else:
    print("Same number")
