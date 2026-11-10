import numpy as np

rows = np.array([[2.0, 2.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 5.0]])
query = np.array([1.0, 1.0, 0.0])


def most_similar(query, rows):
    return int((rows @ query).argmax())


print(most_similar(query, rows))
