def grow(plant_height):
    return plant_height + 5


def report(height):
    return f"The plant is {height} cm tall"


def main():
    height = 10
    height = grow(height)
    print(report(height))


main()
