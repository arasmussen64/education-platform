import numpy as np

X = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])


def first_component(X):
    centered = X - X.mean(axis=0)
    C = centered.T @ centered / (len(X) - 1)
    values, vectors = np.linalg.eigh(C)
    top = vectors[:, 0]
    return top * np.sign(top[0])


def scores(X):
    return (X - X.mean(axis=0)) @ first_component(X)


print(np.round(first_component(X), 3))
print(np.round(scores(X), 3))
