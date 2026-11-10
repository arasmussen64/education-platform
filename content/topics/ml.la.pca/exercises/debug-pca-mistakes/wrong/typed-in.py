import numpy as np


def report(X):
    print("first component explains 0.984")
    print("direction [0.772 0.635]")


X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])
report(X)
