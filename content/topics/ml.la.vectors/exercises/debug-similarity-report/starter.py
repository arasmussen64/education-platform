import numpy as np


def report(query, rows):
    sims = query @ rows / (np.linalg.norm(rows) * np.linalg.norm(query))
    print("similarities:", np.round(sims, 3))
    print("most similar: row", int(sims.argmax()))


report(np.array([1.0, 1.0, 0.0]), np.array([[2.0, 2.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 5.0]]))
