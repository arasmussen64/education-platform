def grow(plant_height):
    plant_height = plant_height + 5


def report(height):
    message = f"The plant is {height} cm tall"


def main():
    height = 10
    grow(height)
    report(height)
    print(message)


main()
