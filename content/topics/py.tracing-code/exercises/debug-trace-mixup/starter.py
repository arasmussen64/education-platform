apples = int(input("Apples? "))
oranges = int(input("Oranges? "))
if apples > oranges:
    difference = oranges - apples
    print(f"More apples, by {difference}")
elif oranges >= apples:
    difference = oranges - apples
    print(f"More oranges, by {apples}")
else:
    print("Same number")
