import numpy as np

grad = np.array([3.0, 4.0])


def steepest_ascent(grad):
    return grad / np.linalg.norm(grad)


def directional_derivative(grad, direction):
    return grad @ direction / np.linalg.norm(direction)


print(steepest_ascent(grad))
for direction in [np.array([1.0, 0.0]), np.array([-4.0, 3.0]), grad]:
    print(round(float(directional_derivative(grad, direction)), 6) + 0.0)
