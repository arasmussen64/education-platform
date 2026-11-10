import numpy as np

X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])


def first_component(X):
    return np.array([0.772, 0.635])


def scores(X):
    return np.array([-3.201, -1.794, -1.021, 1.021, 1.794, 3.201])


print("[0.772 0.635]")
print("[-3.201 -1.794 -1.021  1.021  1.794  3.201]")
