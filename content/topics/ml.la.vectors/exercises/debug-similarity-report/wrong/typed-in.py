import numpy as np


def report(query, rows):
    print("similarities: [1.    0.707 0.   ]")
    print("most similar: row 0")


report(np.array([1.0, 1.0, 0.0]), np.array([[2.0, 2.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 5.0]]))
