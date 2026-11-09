from statistics import mean
import math


def average(numbers):
    """Return the mean of the numbers."""
    return mean(numbers)


def hypotenuse(a, b):
    """Return the long side of a right triangle with short sides a and b."""
    return math.sqrt(a * a + b)
