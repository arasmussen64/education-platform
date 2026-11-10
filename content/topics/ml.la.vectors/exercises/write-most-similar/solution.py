import numpy as np

rows = np.array([[2.0, 2.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 5.0]])
query = np.array([1.0, 1.0, 0.0])


def most_similar(query, rows):
    sims = rows @ query / (np.linalg.norm(rows, axis=1) * np.linalg.norm(query))
    return int(sims.argmax())


print(most_similar(query, rows))
