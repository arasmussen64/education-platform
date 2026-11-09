def area(width, height):
    result = width * height
    """Return the area of a rectangle."""
    return result


def perimeter(width, height):
    """Return the distance around a rectangle."""
    2 * (width + height)


def describe(width, height):
    """Return one line with the area and the perimeter."""
    return f"{width} x {height}: area {area(width, height)}, perimeter {perimeter(width, height)}"


def main():
    print(describe(w, h))
    w = 3
    h = 4


main()
